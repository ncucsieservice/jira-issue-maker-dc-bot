import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from issueCreate import make_issue  # 引入 issueCreate.py 中的 make_issue 函數


# 載入環境變數
load_dotenv()

# 從環境變數中獲取 Discord 和 Jira 的設置
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 設置 Discord Bot 設定
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents = intents)


@bot.event
async def on_ready():
    """
    當 Bot 成功啟動並登入後，執行此函數。
    會顯示 Bot 登入的使用者名稱並同步斜線指令。
    """
    print(f"目前登入身份 --> {bot.user}")
    slash = await bot.tree.sync()
    print(f"載入 {len(slash)} 個斜線指令")


# 透過斜線指令來調用 issueCreate 模組的 make_issue 函數
@bot.tree.command(name="make-issue", description="建立 Jira Issue")
async def make_issue_command(interaction: discord.Interaction, assignee: str, issue_name: str, issue_description: str):
    await make_issue(interaction, assignee, issue_name, issue_description)

# 啟動 Bot
bot.run(DISCORD_TOKEN)
