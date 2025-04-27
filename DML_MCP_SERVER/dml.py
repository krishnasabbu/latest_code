import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from llm_client import LLMClient
import logging
import asyncio
import json
import re
import base64
from docx import Document
from schema_parser import parse_schema
from query_generator import generate_delete_queries, generate_update_query

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------
# CONFIGURATION
# ---------------------------
app = FastAPI()
# mcp = FastMCP("Basic MCP Server")
llm = LLMClient()  # Using Together AI client, model is configured internally


# ---------------------------
# REQUEST/RESPONSE MODELS
# ---------------------------
class Message(BaseModel):
    role: str
    content: str


class MCPInput(BaseModel):
    user_query: str
    chat_history: Optional[List[Message]] = []
    user_id: Optional[str] = None


class MCPOutput(BaseModel):
    response: str
    context: Optional[Dict[str, Any]] = {}


# Define a Pydantic model for the request body
class RequestData(BaseModel):
    user_query: str
    chat_history: list
    user_id: str


# ---------------------------
# DUMMY JIRA FETCHER
# ---------------------------
def fetch_jira_description(jira_id: str) -> str:
    # Replace this with real JIRA API call

    return (f"Please delete the record in t_request table as request_id is 1 \n "
            f"Please delete the record in t_request table as request_id is 1")


# ---------------------------
# HELPER: Extract JIRA ID
# ---------------------------
def extract_jira_id(text: str) -> list[str]:
    match = re.findall(r"[A-Z]{2,}-\d+", text)
    return match


def extract_valid_json(llm_response: str) -> dict:
    # Remove ```json or ``` markers and unescape the string
    cleaned = re.sub(r'```json|```', '', llm_response)
    unescaped = cleaned.encode().decode('unicode_escape')
    return json.loads(unescaped)


def generate_sql_query(jira_id):
    description = fetch_jira_description(jira_id)

    prompt = get_sql_prompt(description)

    llm_response = llm.query(prompt)

    try:
        dml_info = extract_valid_json(llm_response)
        logging.info(f"dml info ========== {dml_info}")
        return generate_sql(dml_info)
    except Exception as e:
        return f"❌ Failed to parse LLM output: {e}\n\nRaw LLM response: {llm_response}"


def generate_query(table_details):
    tables, relationships = parse_schema("schema.sql")

    table = table_details['table']
    condition = table_details['condition']
    operation = table_details['action']
    set = table_details['set']

    if table not in tables:
        print(f"Table '{table}' not found in schema.")
        return

    if operation == 'DELETE':
        query = generate_delete_queries(table, condition, relationships)
    elif operation == 'UPDATE':
        if not set:
            print("SET clause is required for UPDATE operation.")
            return
        query = generate_update_query(table, set, condition)
    else:
        print("Unsupported operation.")
        return
    logging.info(f"Query === {query}")
    return query


def generate_sql(dml_details_list):
    # Initialize empty SQL text
    sql_text = ""

    # Iterate over list of DML instructions
    for dml_details in dml_details_list:
        action = dml_details.get('action')
        table = dml_details.get('table')
        condition = dml_details.get('condition')
        set_clause = dml_details.get('set')

        if action == "UPDATE":
            sql_text += f"UPDATE {table} SET {set_clause} WHERE {condition};\n"
        elif action == "DELETE":
            sql_text += f"DELETE FROM {table} WHERE {condition};\n"
        else:
            # Unknown action, you can raise error or ignore
            continue

    # Save to temporary file
    file_path = f"/tmp/generated_query.sql"
    with open(file_path, "w") as f:
        f.write(sql_text)

    with open(file_path, "rb") as f:
        file_content = f.read()
    encoded_file_content = base64.b64encode(file_content).decode('utf-8')

    return {
        "type": "file",
        "extension": "sql",
        "content": {
            "file_content": encoded_file_content,
            "file_name": "generated_query.sql",
            "mime": "application/sql"
        }
    }


def update_game_plan(existing_doc_path: str, jira_ids: List[str]) -> dict:
    try:
        # Open the existing Word document
        doc = Document(existing_doc_path)

        # Update the document content based on JIRA IDs
        for jira_id in jira_ids:
            # Search for placeholder or section to update
            # Example: we assume there's a placeholder like "JIRA_ID_PLACEHOLDER" that we want to update
            for para in doc.paragraphs:
                if "JIRA_ID_PLACEHOLDER" in para.text:
                    para.text = para.text.replace("JIRA_ID_PLACEHOLDER", jira_id)

        # Save the updated document to a temporary location
        updated_file_path = "/tmp/updated_game_plan.docx"
        doc.save(updated_file_path)

        # Read the file content and encode it to base64
        with open(updated_file_path, "rb") as f:
            file_content = f.read()
        encoded_file_content = base64.b64encode(file_content).decode('utf-8')

        # Return the file content in base64-encoded format
        return {
            "type": "file",
            "extension": "word",
            "content": {
                "file_content": encoded_file_content,
                "file_name": "game_plan.docx",
                "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        }
    except Exception as e:
        logging.error(f"Error updating the document: {e}")
        return {"response": f"Error updating the document: {e}"}


def generate_game_plan(jira_ids):
    return update_game_plan("game_plan.docx", jira_ids)


def get_sql_prompt(description):
    return f"""
            You are a helpful assistant that extracts database DML operations from a user's description.
    
            Instructions:
            - Read the description carefully.
            - Identify each DML operation (UPDATE or DELETE) mentioned.
            - Extract the following information for each operation:
              - "action" → Either "UPDATE" or "DELETE"
              - "table" → Target table name
              - "set" → Fields and values to be updated (for UPDATE only, null for DELETE)
              - "condition" → SQL WHERE condition
            
            Output Format:
            - Always return a **JSON list**.
            - If multiple queries exist, return multiple items in the list.
            - If no UPDATE fields exist for DELETE, put "set" as null.
            
            Example Output:
            [
              {{
                "action": "UPDATE",
                "table": "employees",
                "set": "salary = 60000, department = 'HR'",
                "condition": "employee_id = 101"
              }},
              {{
                "action": "DELETE",
                "table": "departments",
                "set": null,
                "condition": "department_id = 5"
              }}
            ]
            
            Input Description:
            {description}
            """


# ---------------------------
# MAIN MCP TOOL (FOR SSE)
# ---------------------------
@app.post("/handle_request")
async def handle_request(request_data: RequestData):
    logging.info(f"user_query ===== {request_data.user_query}")
    logging.info(f"chat_history ===== {request_data.chat_history}")
    logging.info(f"user_id ===== {request_data.user_id}")

    user_query = request_data.user_query.strip()
    chat_history = request_data.chat_history or []

    if not chat_history:
        return "👋 Hi! Please provide a JIRA Story ID or describe the DML change you'd like to make."

    jira_ids = extract_jira_id(user_query)

    logging.info(f"jira_id ===== {jira_ids}")

    if len(jira_ids) == 1:
        return generate_sql_query(jira_ids[0])

    if len(jira_ids) > 1:
        return generate_game_plan(jira_ids)

    if len(jira_ids) <= 0:
        prompt = f"""
                You are both a SQL and Intent Classification expert. Please follow the steps below:

                **Step 1: DML Extraction**
                
                You are a helpful assistant that extracts information from user input to perform a DML (Data Manipulation Language) operation.
                
                {get_sql_prompt(user_query)}
                
                If no DML information is found, proceed to **Step 2**.
                
                ---
                
                **Step 2: Intent Classification**
                
                You are an assistant that classifies the intent of the user's query. Based on the input, classify the intent as either:
                - **'generate_game_plan'** for game plan-related queries
                - **'dml_operation'** for DML-related queries
                
                **Input:** {user_query}
                
                Respond in JSON format:
                {{
                    "intent": "generate_game_plan" // OR "dml_operation"
                }}
                
                If you are unable to classify the intent as either **generate_game_plan** or **dml_operation**, proceed to **Step 3**.
                
                ---
                
                **Step 3: Fallback Response**
                
                If you cannot determine whether the query is related to generating a game plan or performing a DML operation, respond with a message in this format:
                
                {{
                    "response": "I understand queries related to both game plan generation and DML operations. Could you please clarify your request?"
                }}
                
                Remember please send only response - don't explain or don't add any text to the response

                """
        llm_response = llm.query(prompt)

        logging.info(llm_response)

        try:
            response_info = extract_valid_json(llm_response)

            logging.info(response_info)
            logging.info(response_info.get("action"))
            logging.info(response_info.get("intent"))

            response_info_string = json.dumps(response_info)

            if "action" in response_info_string:
                return generate_sql(response_info)

            if response_info.get("intent"):
                intent = response_info.get("intent")

                if intent == "generate_game_plan":
                    return {
                        "type": "text",
                        "response": "Please send the list of JIRA IDs to generate a game plan."
                    }
                elif intent == "dml_operation":
                    return {
                        "type": "text",
                        "response": "I can help you with DML operations. Please provide more details."
                    }

        except Exception as e:
            logging.error(f"Failed to classify intent: {e}")
            return {
                "type": "text",
                "response": "There was an error while processing your request. Please try again later."
            }

            # If intent classification fails, move to Step 3: Fallback Response
        return {
            "type": "text",
            "response": "I understand queries related to both game plan generation and DML operations. Could you "
                        "please clarify your request?"
        }


if __name__ == "__main__":
    uvicorn.run(app, port=8880)
