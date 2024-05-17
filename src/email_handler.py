"""Classes to handle email interactions."""
import os
from base64 import urlsafe_b64decode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class EmailHandler:
    """Basic class to communicate with the Gmail API."""

    def __init__(self, token_path: str, scopes: list) -> None:
        """Initialise the email handler.

        Args:
            token_path (str): path to the file containing the access and refresh tokens.
            scopes (list): list of scope for interacting with the API.
        """
        self.token_path = token_path
        self.scopes = scopes
        self.service = None

    def set_service(self):
        """Set the connection to the service."""
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            self.service = build("gmail", "v1", credentials=creds)

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    def get_service(self):
        """Get the Gmail API service."""
        return self.service

    def get_size_format(self, b, factor=1024, suffix="B"):
        """Scale bytes to its proper byte format."""
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if b < factor:
                return f"{b:.2f}{unit}{suffix}"
            b /= factor
        return f"{b:.2f}Y{suffix}"

    def clean(self, text):
        """Create a folder name where to save a file with special characters removed from the text."""
        return "".join(c if c.isalnum() else "_" for c in text)

    def parse_parts(self, parts, folder_name, message):
        """Parse the content of an email partition."""
        if parts:
            for part in parts:
                filename = part.get("filename")
                mimeType = part.get("mimeType")
                body = part.get("body")
                data = body.get("data")
                file_size = body.get("size")
                part_headers = part.get("headers")
                if part.get("parts"):
                    # recursively call this function when we see that a part
                    # has parts inside
                    self.parse_parts(part.get("parts"), folder_name, message)
                if mimeType == "text/plain":
                    # if the email part is text plain
                    if data:
                        text = urlsafe_b64decode(data).decode()
                        if not filename:
                            filename = "email.txt"
                        filepath = os.path.join(folder_name, filename)
                        with open(filepath, "wb") as f:
                            f.write(text)
                elif mimeType == "text/html":
                    # if the email part is an HTML content
                    # save the HTML file and optionally open it in the browser
                    if not filename:
                        filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    with open(filepath, "wb") as f:
                        f.write(urlsafe_b64decode(data))
                else:
                    # attachment other than a plain text or HTML
                    for part_header in part_headers:
                        part_header_name = part_header.get("name")
                        part_header_value = part_header.get("value")
                        if part_header_name == "Content-Disposition":
                            if "attachment" in part_header_value:
                                # we get the attachment ID
                                # and make another request to get the attachment itself
                                print(
                                    "Saving the file:",
                                    filename,
                                    "size:",
                                    self.get_size_format(file_size),
                                )
                                attachment_id = body.get("attachmentId")
                                attachment = (
                                    self.service.users()
                                    .messages()
                                    .attachments()
                                    .get(
                                        id=attachment_id,
                                        userId="me",
                                        messageId=message["id"],
                                    )
                                    .execute()
                                )
                                data = attachment.get("data")
                                filepath = os.path.join(folder_name, filename)
                                if data:
                                    with open(filepath, "wb") as f:
                                        f.write(urlsafe_b64decode(data))

    def search_messages(self, query):
        """Search a mail based on a query."""
        result = self.service.users().messages().list(userId="me", q=query).execute()
        messages = []
        if "messages" in result:
            messages.extend(result["messages"])
        while "nextPageToken" in result:
            page_token = result["nextPageToken"]
            result = self.service.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
            if "messages" in result:
                messages.extend(result["messages"])
        return messages

    def read_message(self, message):
        """Do the following for a given message_id.

        - Downloads the content of the email
        - Prints email basic information (To, From, Subject & Date) and plain/text parts
        - Creates a folder for each email based on the subject
        - Downloads text/html content (if available) and saves it under the folder created as index.html
        - Downloads any file that is attached to the email and saves it in the folder created
        """
        msg = self.service.users().messages().get(userId="me", id=message["id"], format="full").execute()
        # parts can be the message body, or attachments
        payload = msg["payload"]
        headers = payload.get("headers")
        parts = payload.get("parts")
        folder_name = "email"
        has_subject = False
        if headers:
            # this section prints email basic info & creates a folder for the email
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == "subject":
                    # make our boolean True, the email has "subject"
                    has_subject = True
                    # make a directory with the name of the subject
                    folder_name = os.path.join(DATA_DIR, self.clean(value))
                    # we will also handle emails with the same subject name
                    folder_counter = 0
                    while os.path.isdir(folder_name):
                        folder_counter += 1
                        # we have the same folder name, add a number next to it
                        if folder_name[-1].isdigit() and folder_name[-2] == "_":
                            folder_name = f"{folder_name[:-2]}_{folder_counter}"
                        elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                            folder_name = f"{folder_name[:-3]}_{folder_counter}"
                        else:
                            folder_name = f"{folder_name}_{folder_counter}"
                    os.mkdir(folder_name)
        if not has_subject:
            # if the email does not have a subject, then make a folder with "email" name
            # since folders are created based on subjects
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
        self.parse_parts(parts, folder_name, message)

    def get_mails(self):
        """Get all emails."""
        results = self.search_messages("")
        print(f"Found {len(results)} results.")
        # for each email matched, read it (output plain/text to console & save HTML and attachments)
        for msg in tqdm(results):
            self.read_message(msg)

    def initialise_set_up(self):
        """Initialise the setup for the first time."""
        self.set_service()
        self.get_mails()
