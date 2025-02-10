import discord
from discord.ext import commands
from getSheet import get_google_sheet

def get_jira_email(discord_id):
    """從 Google Sheets 查找對應的 Jira 郵件"""
    sheet = get_google_sheet()
    records = sheet.get_all_records()

    print("target discord_id: ", discord_id)
    for row in records:
        if str(row["Discord"]) == discord_id:
            return row["Jira"]
    return None
