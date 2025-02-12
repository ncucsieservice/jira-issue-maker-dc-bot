# jira-issue-maker-dc-bot
用來 assign issue 的 DC 機器人

## 虛擬環境設立(Wins)
```
python -m venv venv
.\venv\bin\activate
pip install -r requirements.txt
```

## DC bot
官方文件: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

## Jira

### API 設定
https://id.atlassian.com/manage-profile/security

- issue type: 
  - https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-types/
  - https://confluence.atlassian.com/jirakb/finding-the-id-for-issue-types-646186508.html

### project permission 設定
參考[官方文件](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post)裡面提及的內容，若要使用 API 建立專案 issue，必須先開啟 permission，開啟參考[此文件](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/#permissions)。


### 1. **JIRA_URL**
   - **位置**：這是你的 Jira 站點的 URL。
   - **如何取得**：
     1. 登入你的 Jira 帳戶。
     2. 查看瀏覽器的地址列，你會看到像這樣的網址：`https://yourdomain.atlassian.net`。
     3. 這就是你的 `JIRA_URL`。

---

### 2. **JIRA_EMAIL**
   - **位置**：這是你登入 Jira 的電子郵件地址。
   - **如何取得**：
     1. 使用你平常登入 Jira 的電子郵件。
     2. 這個電子郵件需要與 API Token 配對使用。

---

### 3. **JIRA_API_TOKEN**
   - **位置**：這是一個用於 API 認證的專用密鑰，類似密碼。
   - **如何取得**：
     1. 登入你的 Atlassian 帳戶：[Atlassian API Token](https://id.atlassian.com/manage-profile/security/api-tokens)。
     2. 點擊「**Create API token**」按鈕。
     3. 輸入 Token 名稱（例如 `Discord Bot Token`）。
     4. 點擊「Create」，然後複製生成的 Token，並妥善保存。
        - **注意**：Token 只會顯示一次，請確保將它存入安全的地方（例如 `.env` 文件）。

### 4. **JIRA_PROJECT_KEY**
   - **位置**：這是你的 Jira 專案的代碼，用於指定在哪個專案中建立 Issue。
   - **如何取得**：
     1. 登入你的 Jira 帳戶，進入你要使用的專案。
     2. 查看該專案的 Issue 列表。
     3. 在 Issue 的名稱前面，會有一個專案代碼，例如：
        ```
        MYPROJ-123
        ```
     4. 取 `MYPROJ` 作為 `JIRA_PROJECT_KEY`。

## 小提醒
- 不要用 3.13
  - https://github.com/Rapptz/discord.py/issues/9742
- 不要用 MSYS 的 Python ...
  - 用 vscode 開一個 Python 官網載的 python.exe 所建立的虛擬環境 ... 不然會一直報SSL錯誤
    - discord.com:443 ssl:True [SSLCertVerificationError: (1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)')]

## DB
- 使用 Google Sheet: https://docs.google.com/spreadsheets/d/1K14CPDDEDbGQxB2NIWUVfP3ke65iwIkfxtMftQAalbA/edit?usp=sharing