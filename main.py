import os
import requests
import json
import time
import random
import sys

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

CALLS = [
    # Microsoft Graph - OneDrive
    'https://graph.microsoft.com/v1.0/me/drive/root',
    'https://graph.microsoft.com/v1.0/me/drive',
    'https://graph.microsoft.com/v1.0/drive/root',
    'https://graph.microsoft.com/v1.0/me/drive/root/children',

    # Microsoft Graph - Usuarios
    'https://graph.microsoft.com/v1.0/users',
    'https://graph.microsoft.com/v1.0/me/?$select=displayName',

    # Microsoft Graph - Mail/Mensajes
    'https://graph.microsoft.com/v1.0/me/messages',
    'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
    'https://graph.microsoft.com/v1.0/me/mailFolders',
    'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/delta',

    # Microsoft Graph - Outlook
    'https://graph.microsoft.com/v1.0/me/outlook/masterCategories',
    'https://graph.microsoft.com/beta/me/outlook/masterCategories',
    'https://graph.microsoft.com/beta/me/messages?$select=internetMessageHeaders&$top=1',

    # Microsoft Graph - Aplicaciones
    'https://graph.microsoft.com/v1.0/applications?$count=true',

    # Microsoft Graph - SharePoint/Sites
    'https://graph.microsoft.com/v1.0/sites/root/lists',
    'https://graph.microsoft.com/v1.0/sites/root',
    'https://graph.microsoft.com/v1.0/sites/root/drives',

    # Power BI
    'https://api.powerbi.com/v1.0/myorg/apps'
]

def get_tokens():
    """Obtains the access_token and updates the refresh_token if necessary."""
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'http://localhost:53682/'
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data['access_token']
        new_refresh_token = token_data.get('refresh_token')

        # Microsoft rotates refresh tokens. If we receive a new one, we must save it.
        if new_refresh_token and new_refresh_token != REFRESH_TOKEN:
            print("New refresh_token detected. Saving for update...")
            with open("new_token.txt", "w") as f:
                f.write(new_refresh_token)

        return access_token

    except requests.exceptions.RequestException as e:
        print(f"Error obtaining token: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'N/A'}")
        sys.exit(1)

def main():
    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        print("Error: Environment variables are missing (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN).")
        sys.exit(1)

    print("Obtaining access token...")
    access_token = get_tokens()

    session = requests.Session()
    session.headers.update({
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    })

    random.shuffle(CALLS)
    endpoints_to_call = CALLS[:random.randint(5, len(CALLS))]

    success_count = 0
    for endpoint in endpoints_to_call:
        try:
            resp = session.get(endpoint, timeout=30)
            if resp.status_code == 200:
                success_count += 1
                print(f"OK [{resp.status_code}]: {endpoint}")
            else:
                print(f"FAIL [{resp.status_code}]: {endpoint}")
        except Exception as e:
            print(f"Error calling {endpoint}: {e}")

    with open("time.log", "a") as f:
        f.write(f"{time.asctime(time.localtime(time.time()))} - Successful calls: {success_count}/{len(endpoints_to_call)}")

if __name__ == '__main__':
    main()
