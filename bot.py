import discord
import requests
import json
import os
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "$", intents = intents)

@bot.event
async def on_ready():
    slash = await bot.tree.sync()
    print(f"目前登入身份 --> {bot.user}")
    print(f"載入 {len(slash)} 個斜線指令")

@bot.command(name="make-issue")
async def make_issue(ctx):
    # 確認是否回覆了某條訊息
    if not ctx.message.reference:
        await ctx.send("❌ 請回覆一條訊息後使用 `/make-issue` 指令。")
        return

    # 取得被回覆的訊息
    replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    issue_title = replied_message.content
    print(replied_message.content)

    # 構建 Jira Issue 請求的 Payload
    jira_payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY,
            },
            "summary": issue_title,
            "description": f"此 issue 是由 {ctx.author.name} 在 Discord 建立。\n\n內容: {issue_title}",
            "issuetype": {
                "name": "Task",  # Issue 類型，可改為 Bug, Story 等
            },
        }
    }

    # 發送請求到 Jira
    # try:
    response = requests.post(
        JIRA_URL,
        json=jira_payload,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()  # 檢查請求是否成功

    # 回覆成功訊息
    issue_key = response.json()["key"]
    await ctx.send(f"🎉 成功建立 Jira Issue: {issue_key}")
    # except requests.exceptions.RequestException as e:
    #     print(f"❌ 建立 Jira Issue 時出錯: {e}")
    #     await ctx.send("❌ 無法建立 Jira Issue，請檢查設定或稍後再試。")

@bot.command(name='test')
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')


bot.run(DISCORD_TOKEN)
