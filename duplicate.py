import re
from rapidfuzz import fuzz

def preprocess_message(msg):
    # Remove numbers (line numbers, IDs) and extra spaces
    msg = re.sub(r'\d+', '', msg)
    msg = re.sub(r'\s+', ' ', msg)
    return msg.strip().lower()

def deduplicate_exceptions(messages, threshold=90):
    cleaned_messages = [preprocess_message(msg) for msg in messages]
    unique_messages = []

    for i, msg in enumerate(cleaned_messages):
        if not any(fuzz.ratio(msg, existing) > threshold for existing in unique_messages):
            unique_messages.append(msg)
    
    # Map back to original message (optional)
    final_unique = []
    for clean_msg in unique_messages:
        for orig in messages:
            if preprocess_message(orig) == clean_msg:
                final_unique.append(orig)
                break
    
    return final_unique

# Example
messages = [
    "Exception in com.example.MyService: NullPointerException at line 123",
    "Exception in com.example.MyService: NullPointerException at line 456",
    "Different Exception in com.other.Service: IOException"
]

unique_exceptions = deduplicate_exceptions(messages)
print(unique_exceptions)
