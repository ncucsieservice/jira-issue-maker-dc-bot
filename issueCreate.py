import os
from jira import JIRA
from userMapping import get_jira_email
import discord


JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

jiraOptions = {'server': JIRA_URL}
jira = JIRA(options=jiraOptions, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

CATEGORY_PROJECT_MAPPING = {
    "Admin": ("CSTPTEST", "jira-notify-admin"),
    "中學生AI": ("CSTPTEST", "jira-notify-ai1"),
    "小學生AI": ("CSTPAI2", "jira-notify"),
}


def get_jira_account_id(email):
    """
    根據用戶的 Email 地址查詢其 Jira 帳戶 ID。
    
    參數:
    email (str): 用戶的 Email 地址
    
    返回:
    str: 匹配的 Jira 帳戶 ID，如果找不到則返回 None。
    """
    user = jira.search_users(query=email)
    if user:
        return user[0].accountId  # 取得第一個匹配的帳號 ID
    return None


async def make_issue(interaction, assignee: str, issue_name: str, issue_description: str):
    """
    建立 Jira Issue，並發送相關通知。

    參數:
    interaction (discord.Interaction): 與 Discord 用戶的交互。
    assignee (str): 被指定為受託人的用戶名稱或 Discord @標註。
    issue_name (str): Jira Issue 的標題。
    issue_description (str): Jira Issue 的描述。
    """
    try:
        # 立即回應以避免 interaction 過期
        await interaction.response.send_message("正在處理請求...")

        # 如果沒有指定 issue_name，使用默認名稱
        issue_title = issue_name if issue_name else "No title provided for the issue."
        issue_desc = issue_description if issue_description else "No description provided for the issue."
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

        # 判斷發送通知的頻道，根據頻道類別來決定 Jira 專案與通知頻道
        category = interaction.channel.category  # 取得頻道所屬的類別

        if category:
            category_name = category.name
            if category_name in CATEGORY_PROJECT_MAPPING:
                jira_project_key, notify_channel_name = CATEGORY_PROJECT_MAPPING[category_name]

                issue_dict = {
                    'project': {'key': jira_project_key},
                    'summary': issue_title,
                    'description': issue_desc, 
                    'issuetype': {'name': 'Task'},
                    'assignee': {'accountId': assignee_jira_id},  
                    'reporter': {'accountId': reporter_jira_id},  
                }
                new_issue = jira.create_issue(fields=issue_dict)

                # 發送到對應頻道
                notify_channel = discord.utils.get(interaction.guild.text_channels, name=notify_channel_name)
                if notify_channel:
                    await notify_channel.send(f"✅ 已建立 Jira Issue: {new_issue.key} (受託人: `{assignee_name}`, 回報者: `{interaction.user.name}`)")
                else:
                    await interaction.followup.send(f"❌ 找不到通知頻道 `{notify_channel_name}`。")
            else:
                await interaction.followup.send(f"❌ 無法識別此類別 `{category_name}`，無法發送通知。")
        else:
            await interaction.followup.send(f"❌ 無法判斷訊息所屬類別，無法發送通知。")

    except Exception as e:
        await interaction.followup.send(f"❌ An error occurred: {e}")
        print(f"Error creating Jira issue: {e}")
