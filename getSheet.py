import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets API 授權設定
SHEET_ID = os.getenv("SHEET_ID") 
SHEET_NAME = os.getenv("SHEET_NAME")  

def get_google_sheet():
    """連線到 Google Sheets 並回傳工作表"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)  # 你的 JSON 憑證
    client = gspread.authorize(creds)

    # open with name = "113-2 jira-dc-mapping"
    sheet = client.open("113-2 jira-dc-mapping").worksheet("sheet1")
    # sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return sheet