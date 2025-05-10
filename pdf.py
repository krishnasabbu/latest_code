from pywinauto import Application
import time
import os

def open_pdf_and_select_label(pdf_path, output_docx):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found.")

    print("🚀 Launching Word...")
    app = Application(backend='uia').start("winword.exe")

    time.sleep(2)  # Give Word a moment to open

    print("📂 Opening PDF file...")
    word = app.window(title_re=".*Word")
    word.wait("visible", timeout=10)
    word.type_keys('^o')  # Ctrl+O (Open)
    time.sleep(1)
    word.type_keys(pdf_path)
    word.type_keys('{ENTER}')
    time.sleep(5)  # Wait for the file to open

    print("🔐 Looking for sensitivity label window...")
    try:
        # You might need to adjust title or timeout depending on your system
        dlg = app.window(title_re=".*Sensitivity.*")
        dlg.wait("visible", timeout=10)

        # Select the 3rd label (you may need to adjust this logic based on label UI)
        dlg.child_window(auto_id="Item 2", control_type="ListItem").click_input()  # 0-based index
        dlg.child_window(title="Apply", control_type="Button").click_input()

        print("✅ Label applied successfully.")
    except Exception as e:
        print(f"⚠️ Label selection window not found or auto interaction failed: {e}")

    print("💾 Saving as DOCX...")
    word.type_keys('^s')  # Ctrl+S
    time.sleep(1)
    word.type_keys(output_docx)
    word.type_keys('{ENTER}')

    time.sleep(2)
    word.type_keys('%{F4}')  # Alt+F4 to close Word
    print("✅ Document saved and Word closed.")

# Example usage
open_pdf_and_select_label(
    pdf_path=r"C:\Users\YourName\Desktop\sample.pdf",
    output_docx=r"C:\Users\YourName\Desktop\output.docx"
)
