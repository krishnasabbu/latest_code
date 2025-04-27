import win32com.client as win32

def send_exception_email(exception_list, recipients):
    # Initialize Outlook application
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0: MailItem

    # Email details
    mail.To = ";".join(recipients)  # multiple recipients separated by semicolon
    mail.Subject = '🚨 Exception Report - Last 24 Hours'
    
    # Build the HTML table
    html_table = """
    <html>
    <body>
        <h2 style="color:#D9534F;">Exception Report</h2>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2a654; color: white;">
                <th>SNO</th>
                <th>Exception</th>
                <th>Root Cause</th>
            </tr>
    """

    for idx, item in enumerate(exception_list, start=1):
        exception = item.get('exception', 'N/A')
        root_cause = item.get('root_cause', 'N/A')

        html_table += f"""
            <tr style="background-color: #f9f9f9;">
                <td style="text-align: center;">{idx}</td>
                <td>{exception}</td>
                <td>{root_cause}</td>
            </tr>
        """

    html_table += """
        </table>
        <p style="color: gray;">This is an auto-generated email. Please do not reply.</p>
    </body>
    </html>
    """

    # Attach the HTML body
    mail.HTMLBody = html_table

    # Send the email
    mail.Send()

    print("✅ Email sent successfully!")

# ----------------------
# 📋 Example usage:

exception_list = [
    {"exception": "NullPointerException", "root_cause": "Missing value in user profile"},
    {"exception": "DatabaseTimeoutException", "root_cause": "Slow response from DB server"},
    {"exception": "FileNotFoundError", "root_cause": "Missing configuration file"}
]

recipients = ["recipient1@example.com", "recipient2@example.com"]

send_exception_email(exception_list, recipients)
