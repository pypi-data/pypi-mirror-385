import os, base64
from pathlib import Path
from colorama import init, Fore, Style
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from muffinbite.utils.abstracts import AbstractESP
from muffinbite.management.settings import session, CLIENT_SECRET_FILE, BASE_DIR, CONFIG_DIR

init(autoreset=True)

SCOPES = {
    "ACTION_COMPOSE": "https://www.googleapis.com/auth/gmail.addons.current.action.compose",
    "MESSAGE_ACTION": "https://www.googleapis.com/auth/gmail.addons.current.message.action",
    "MESSAGE_METADATA": "https://www.googleapis.com/auth/gmail.addons.current.message.metadata",
    "MESSAGE_READONLY": "https://www.googleapis.com/auth/gmail.addons.current.message.readonly",
    "LABELS": "https://www.googleapis.com/auth/gmail.labels",
    "SEND": "https://www.googleapis.com/auth/gmail.send",
    "READONLY": "https://www.googleapis.com/auth/gmail.readonly",
    "COMPOSE": "https://www.googleapis.com/auth/gmail.compose",
    "INSERT": "https://www.googleapis.com/auth/gmail.insert",
    "MODIFY": "https://www.googleapis.com/auth/gmail.modify",
    "METADATA": "https://www.googleapis.com/auth/gmail.metadata",
    "SETTINGS_BASIC": "https://www.googleapis.com/auth/gmail.settings.basic",
    "SETTINGS_SHARING": "https://www.googleapis.com/auth/gmail.settings.sharing",
    "DELETE_PERMANENT": "https://mail.google.com/"
}

class GoogleESP(AbstractESP):

    def __init__(self, config, scope='SEND'):

        self.scope = [SCOPES[scope]]
        self.service = ''
        self.config = config
        self.token_path = self.get_token_path()

    def get_token_path(self):
        """
        Returns the token path based on the email stored in the config file.
        Falls back to '' if no email is set.
        """

        email = self.config.get("user", "email", fallback=None)

        # sanitize email for filename
        token_name = ""
        if email:
            token_name = email.replace("@", "_at_").replace(".", "_") + ".json"

        tokens_dir = Path(CONFIG_DIR) / "tokens"
        os.makedirs(tokens_dir, exist_ok=True)

        return tokens_dir / token_name

    def get_credentials(self):
        """Get credentials for the user"""
        creds = None

        if not os.path.exists(CLIENT_SECRET_FILE):
            print(Fore.YELLOW + Style.BRIGHT +f"""
     Please provide default credentials via, `credentials.json` file in the {BASE_DIR},
     You can get it from google cloud console for gmail api.
     For further details, please visit: https://muffinbite.dev/docs/requirements/ and search for Gmail API
""")
            return False
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scope)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, self.scope)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_service(self):

        credentials = self.get_credentials()

        if credentials:
            self.service = build('gmail', 'v1', credentials=credentials)

            return self.service
        else:
            return None

    def send(self, message):
        if not self.service:
            service = self.get_service()

            if not service:
                return False, None, None
        try:
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            response = self.service.users().messages().send(userId='me', body={'raw': encoded_message}).execute()

            if response['labelIds'][0] == "SENT":
                return True, response['id'], response['threadId']

        except HttpError as error:
            print(Fore.RED + Style.BRIGHT + "     Mail sending Limit reached! Please try again after 24 hours.\n")
            return False, None, None

        except Exception as error:
            if session.debug:
                session.logger.error(f"Error: {error}\n")

            return False, None, None