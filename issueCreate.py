import discord
import requests
import json
import os
from dotenv import load_dotenv
from discord.ext import commands
from jira import JIRA
from userMapping import get_jira_email
from discord import app_commands


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

jiraOptions = {'server': JIRA_URL}
jira = JIRA(options=jiraOptions, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents = intents)



def get_jira_account_id(email):
    user = jira.search_users(query=email)
    if user:
        return user[0].accountId  # 取得第一個匹配的帳號 ID
    return None


@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")
    slash = await bot.tree.sync()
    print(f"載入 {len(slash)} 個斜線指令")


@bot.tree.command(name="make-issue", description="建立 Jira Issue")
@app_commands.describe(
    assignee="指定誰要處理這份任務 (可以是 Discord @標人 或是純文字 username)",
    issue_name="指定任務的名稱"
)
async def make_issue(interaction: discord.Interaction, assignee: str, issue_name: str):
    try:
        # 立即回應以避免 interaction 過期
        await interaction.response.send_message("正在處理您的請求...")

        # 如果沒有指定 issue_name，使用默認名稱
        issue_title = issue_name if issue_name else "No title provided for the issue."
        reporter_discord_id = str(interaction.user.name)  # 記錄報告者 (A 用戶的 Discord ID)

        # 處理 assignee 字串或標註
        if assignee.startswith('<@') and assignee.endswith('>'):
            # 處理 @標註，提取出用戶ID
            assignee_discord_id = assignee[2:-1]  # 去除 <@> 符號
            assignee_user = await interaction.guild.fetch_member(assignee_discord_id)  # 通過 ID 查找用戶
            if assignee_user:
                assignee_name = assignee_user.name  # 獲取用戶名稱
            else:
                await interaction.followup.send(f"❌ 無法找到 `{assignee}` 的 Discord 用戶。請確認名稱或 @標註正確。")
                return
        else:
            assignee_user = discord.utils.get(interaction.guild.members, name=assignee)  # 根據名稱查找用戶
            if assignee_user:
                assignee_name = assignee_user.name
            else:
                await interaction.followup.send(f"❌ 無法找到 `{assignee}` 的 Discord 用戶。請確認名稱或 @標註正確。")
                return

        assignee_discord_id = str(assignee_user.name)  # 獲取用戶名稱

        assignee_jira_email = get_jira_email(assignee_discord_id)
        reporter_jira_email = get_jira_email(reporter_discord_id)

        assignee_jira_id = get_jira_account_id(assignee_jira_email)
        reporter_jira_id = get_jira_account_id(reporter_jira_email)

        if not assignee_jira_email:
            await interaction.followup.send(f"❌ 無法找到 `{assignee_name}` 的 Jira 帳戶，請先綁定！")
            return
        if not reporter_jira_email:
            await interaction.followup.send(f"❌ 無法找到 `{interaction.user.name}` 的 Jira 帳戶，請先綁定！")
            return

        print(f"Issue Title: {issue_title}")
        print(f"Assignee: {assignee_name}, Reporter: {interaction.user.name}")

        # 建立 Jira issue
        issue_dict = {
            'project': {'key': JIRA_PROJECT_KEY},
            'summary': issue_title,
            'description': f'This issue was automatically created from Discord by {interaction.user.name}.',
            'issuetype': {'name': 'Task'},
            'assignee': {'accountId': assignee_jira_id},  # 指定受託人
            'reporter': {'accountId': reporter_jira_id},  # 指定回報者
        }
        new_issue = jira.create_issue(fields=issue_dict)

        # 判斷發送通知的頻道，假設我們需要根據不同的類別來發送通知
        category = interaction.channel.category  # 取得頻道所屬的類別
        if category:
            # 判斷類別名稱來確定發送通知的頻道
            if category.name == "Admin":
                channel_name = "jira-notify"
            else:
                channel_name = "一般"  # 默認頻道名稱

            # 發送到對應頻道
            notify_channel = discord.utils.get(interaction.guild.text_channels, name=channel_name)
            if notify_channel:
                await notify_channel.send(f"✅ Jira issue created: {new_issue.key} (assignee: `{assignee_name}`, reporter: `{interaction.user.name}`)")
            else:
                await interaction.followup.send(f"❌ 找不到通知頻道 `{channel_name}`。")
        else:
            await interaction.followup.send(f"❌ 無法判斷訊息所屬類別，無法發送通知。")

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}")
        print(f"Error creating Jira issue: {e}")


bot.run(DISCORD_TOKEN)
