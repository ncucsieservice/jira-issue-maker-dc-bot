# This code sample uses the 'requests' library
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
import os

from dotenv import load_dotenv

load_dotenv()
url = os.getenv("JIRA_CREATE_ISSUE_URL")
email = os.getenv("JIRA_EMAIL")
api_token = os.getenv("JIRA_API_TOKEN")
auth = HTTPBasicAuth(email, api_token)

headers = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}

payload = json.dumps( {
  "fields": {
    "issuetype": {
      "id": "10002"
    },
    "labels": [
      "bugfix",
      "blitz_test"
    ],
   
    "project": {
      "id": "10000"
    },
    "summary": "Main order flow broken",
  },
  "update": {}
} )

response = requests.request(
   "POST",
   url,
   data=payload,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))