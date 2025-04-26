import json
import os
import chainlit as cl
import logging
import base64
from fpdf import FPDF
from docx import Document
from docx2pdf import convert
from typing import List
import tempfile
import httpx

# MCP server URLs per tool
TOOL_ENDPOINTS = {
    "DML Requests": "http://localhost:8880/handle_request",
    "Alerts Info": "http://localhost:8881/handle_request",
    "Message Spec": "http://localhost:8882/handle_request",
}


# ---------------------------
# CALL TOOL USING HTTPX (no fastmcp)
# ---------------------------
async def call_mcp_tool(tool_name, user_query, chat_history):
    tool_url = TOOL_ENDPOINTS.get(tool_name)
    if not tool_url:
        return f"❌ Unknown tool selected: {tool_name}"

    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "user_query": user_query,
                "chat_history": chat_history,
                "user_id": "demo-user"
            }
            response = await client.post(tool_url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            logging.info(f"Result from MCP =========== {result}")

            if result.get("type") == "file":
                file_content_base64 = result["content"].get("file_content")
                file_name = result["content"].get("file_name")
                mime = result["content"].get("mime")

                if file_content_base64 and file_name:
                    file_content = base64.b64decode(file_content_base64)
                    return cl.File(
                        name=file_name,
                        content=file_content,
                        mime=mime
                    )
                else:
                    return "⚠️ File content or file name missing in the response."

            elif result.get("type") == "text":
                return result.get("response")

            return "⚠️ Unexpected MCP server response."

    except Exception as e:
        return f"❌ Failed to connect to MCP server: {str(e)}"


# ---------------------------
# CHAT START
# ---------------------------
@cl.on_chat_start
async def start():
    await start_again()


async def start_again():
    await cl.Message(
        content="👋 Welcome! Please choose what you'd like help with:",
        actions=[
            cl.Action(name="dml_requests", label="🛠 DML Requests", payload={"tool": "DML Requests"}),
            cl.Action(name="alerts_info", label="🚨 Alerts Info", payload={"tool": "Alerts Info"}),
            cl.Action(name="message_spec", label="💬 Message Spec", payload={"tool": "Message Spec"}),
        ]
    ).send()
    cl.user_session.set("chat_history", [])
    cl.user_session.set("tool", None)


# ---------------------------
# TOOL SELECTION HANDLER
# ---------------------------
@cl.action_callback("dml_requests")
async def on_action(action: cl.Action):
    selected_tool = action.payload["tool"]
    cl.user_session.set("tool", selected_tool)
    cl.user_session.set("chat_history", [])
    await cl.Message(content=f"✅ Selected **{selected_tool}**. Please enter your request.").send()


async def check_tools_shift(user_str: str):
    if "tools" in str(user_str).lower():
        await start_again()
        return False
    return True

# ---------------------------
# HANDLE USER MESSAGE
# ---------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    tool = cl.user_session.get("tool")
    if not tool:
        await cl.Message(content="⚠️ Please select a tool first.").send()
        return

    tools_status = await check_tools_shift(message.content)

    if tools_status:
        chat_history = cl.user_session.get("chat_history") or []
        chat_history.append({"role": "user", "content": message.content})

        response = await call_mcp_tool(tool, message.content, chat_history)

        if isinstance(response, cl.File):
            file_path = response.path
            logging.info(f" response ======== {response}")
            if not file_path:
                # ❗ Path is None — so create temp file from content
                suffix = '.sql' if response.mime == "application/sql" else '.docx'
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(response.content)  # cl.File has content!
                    file_path = tmp_file.name
                print(f"✅ Temp file created: {file_path}")

            logging.info(f" file path ======== {file_path}")
            msg = await cl.Message(content="✅ SQL file generated! Click below to download.").send()
            msg1 = await response.send(for_id=msg.id)

            file_ext = os.path.splitext(file_path)[1].lower()

            pdf_path = None

            if file_ext == ".sql":
                # Convert SQL to PDF
                pdf_path = file_path.replace('.sql', '.pdf')
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                with open(file_path, 'r') as file:
                    for line in file:
                        pdf.cell(0, 10, txt=line.strip(), ln=True)
                pdf.output(pdf_path)

            elif file_ext == ".docx":
                # Convert DOCX to PDF
                pdf_path = file_path.replace('.docx', '.pdf')
                try:
                    # Try native docx2pdf (only works in Windows or Mac)
                    convert(file_path, pdf_path)
                except Exception as e:
                    print(f"docx2pdf conversion failed: {e}")
                    # Alternative: Save as docx content into PDF manually (if needed)
                    document = Document(file_path)
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    for para in document.paragraphs:
                        pdf.cell(0, 10, txt=para.text.strip(), ln=True)
                    pdf.output(pdf_path)
            logging.info(f" pdf_path ======== {pdf_path}")
            # Display the generated PDF
            if pdf_path and os.path.exists(pdf_path):
                elements = [
                    cl.Pdf(name="Generated PDF", display="inline", path=pdf_path, page=1)
                ]
                # Reminder: The name of the pdf must be in the content of the message
                await cl.Message(content="Preview", elements=elements).send()
        else:
            await cl.Message(content=response).send()

        chat_history.append({"role": "assistant", "content": str(response)})
        cl.user_session.set("chat_history", chat_history)
