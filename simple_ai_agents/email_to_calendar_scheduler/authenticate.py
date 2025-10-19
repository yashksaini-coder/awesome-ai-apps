# authenticator.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CLIENT_SECRETS = "credentials.json"  # your OAuth client secret (Desktop app)
TOKEN_PATH = "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    # For creating events only:
    "https://www.googleapis.com/auth/calendar.events",
    # If you later need full calendar read/write, replace/add:
    # "https://www.googleapis.com/auth/calendar"
]

def main():
    # Remove old token to force re-consent if you changed scopes
    if os.path.exists(TOKEN_PATH):
        print("Removing existing token to force re-consent...")
        os.remove(TOKEN_PATH)

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=8090)  # change port if needed

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    print("✅ Authentication complete. Token written to", TOKEN_PATH)

if __name__ == "__main__":
    main()
