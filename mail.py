import win32com.client
import os
import tempfile
import time
from datetime import datetime

OUTLOOK_FOLDER_NAME = "TranslateMe"  # Custom folder name under Inbox

def get_outlook_folder():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox
    folder = inbox.Folders(OUTLOOK_FOLDER_NAME)
    return folder

def translate_file_dummy(filepath):
    # Replace with real translation logic
    translated_path = filepath.replace(".pdf", "_translated.pdf").replace(".docx", "_translated.docx")
    with open(filepath, "rb") as src, open(translated_path, "wb") as dst:
        dst.write(src.read())  # Dummy: just copy file
    print(f"✅ Translated file saved: {translated_path}")
    return translated_path

def reply_with_attachment(mail, translated_path):
    reply = mail.Reply()
    reply.Body = "Here is your translated document.\n\n" + mail.Subject
    reply.Attachments.Add(translated_path)
    reply.Send()
    print("📤 Replied to sender with translated file.")

def process_email(mail):
    print(f"\n📩 New Email: {mail.Subject} from {mail.SenderEmailAddress}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(1, mail.Attachments.Count + 1):
            attachment = mail.Attachments.Item(i)
            if attachment.FileName.endswith((".pdf", ".docx")):
                filepath = os.path.join(tmpdir, attachment.FileName)
                attachment.SaveAsFile(filepath)
                print(f"📎 Saved attachment: {filepath}")
                
                translated_path = translate_file_dummy(filepath)
                reply_with_attachment(mail, translated_path)

    mail.Unread = False  # Mark as read

def monitor_folder():
    folder = get_outlook_folder()
    print(f"🔍 Monitoring folder: {OUTLOOK_FOLDER_NAME}")
    
    seen_ids = set()

    while True:
        messages = folder.Items.Restrict("[Unread] = true")
        messages.Sort("[ReceivedTime]", True)

        for mail in messages:
            if mail.EntryID not in seen_ids and mail.Attachments.Count > 0:
                seen_ids.add(mail.EntryID)
                process_email(mail)

        time.sleep(10)  # Poll every 10 seconds

if __name__ == "__main__":
    monitor_folder()
