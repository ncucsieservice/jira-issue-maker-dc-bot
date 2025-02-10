import discord
import requests
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
from jira import JIRA

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

jiraOptions = {'server': JIRA_URL}
jira = JIRA(options=jiraOptions, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

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

    try:
        # 取得被回覆的訊息
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        issue_title = replied_message.content
        print(replied_message.content)

        # 建立 Jira issue
        issue_dict = {
            'project': {'key': JIRA_PROJECT_KEY},
            'summary': issue_title,
            'description': 'This issue was automatically created from a Discord bot command.',
            'issuetype': {'name': 'Task'}
        }
        new_issue = jira.create_issue(fields=issue_dict)
        await ctx.send(f"✅ Jira issue created: {new_issue.key}")  # Send confirmation message
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        print(f"Error creating Jira issue: {e}")


@bot.command(name='test')
async def test(ctx, *args):
    arguments = ', '.join(args)
    await ctx.send(f'{len(args)} arguments: {arguments}')


bot.run(DISCORD_TOKEN)
