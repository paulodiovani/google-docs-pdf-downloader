import os.path
from tempfile import TemporaryDirectory

import click
import requests
from google.auth.external_account_authorized_user import (
    Credentials as AuthorizedUserCredentials,
)
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PyPDF2 import PdfMerger

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
]


type GoogleCredentials = Credentials | AuthorizedUserCredentials


def get_google_credentials() -> GoogleCredentials:
    """
    Obtains Google API credentials for the user.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("config/token.json"):
        creds = Credentials.from_authorized_user_file("config/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "config/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("config/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def get_google_document(credentials: GoogleCredentials, document_id: str) -> dict:
    """
    Get a Google docs Document
    """
    service = build("docs", "v1", credentials=credentials)
    return (
        service.documents()
        .get(documentId=document_id, includeTabsContent=True)
        .execute()
    )


def get_all_tabs(document_or_tab: dict) -> list[dict]:
    """
    Get all tabs and child tabs from a document
    and return a list of tab properties
    """
    all_tabs = []

    if "tabs" in document_or_tab:
        for tab in document_or_tab["tabs"]:
            all_tabs = all_tabs + [tab["tabProperties"]] + get_all_tabs(tab)

    if "childTabs" in document_or_tab:
        for tab in document_or_tab["childTabs"]:
            all_tabs = all_tabs + [tab["tabProperties"]] + get_all_tabs(tab)

    return all_tabs


def download_pdfs(
    credentials: GoogleCredentials,
    temp_dir: str,
    document_id: str,
    tab_id: str | None = None,
    index: int | None = 0,
):
    """
    Download a google document,
    or google document tab,
    as PDF
    """
    url = f"https://docs.google.com/document/d/{document_id}/export?format=pdf"
    filename = f"{temp_dir}/{document_id}"

    if tab_id:
        url += f"&tab={tab_id}"
        filename += f"-{str(index).rjust(4, '0')}"

    filename += ".pdf"

    headers = {"Authorization": f"Bearer {credentials.token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
    else:
        raise Exception(
            f"Failed to download PDF: {response.status_code} - {response.text}"
        )


def merge_pdfs(temp_dir: str, output_file: str):
    """
    Merge a list of PDF files from a directory
    into a single file
    """
    pdf_files = [
        os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".pdf")
    ]
    pdf_files.sort()
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()


@click.command()
@click.argument("url")
@click.option("--output", default=None, help="Output name of the destination PDF")
def main(url: str, output: str):
    # Extract document ID from URL
    document_id = url.split("/d/")[1].split("/")[0]
    credentials = get_google_credentials()
    document = get_google_document(credentials, document_id)

    # Use google document title as filename if none is sprovided
    if not output:
        output = document["title"] + ".pdf"

    all_tabs = get_all_tabs(document)

    # Define the temporary output directory
    with TemporaryDirectory(prefix="google-docs-downloader-") as temp_dir:
        # Download PDFs
        if len(all_tabs) >= 1:
            for index, tab in enumerate(all_tabs):
                download_pdfs(
                    credentials, temp_dir, document["documentId"], tab["tabId"], index
                )
        else:
            download_pdfs(credentials, temp_dir, document["documentId"])

        # Merge PDFs
        merge_pdfs(temp_dir, output)


if __name__ == "__main__":
    main()
