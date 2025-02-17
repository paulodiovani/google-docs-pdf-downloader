import os.path
from sys import prefix
from tempfile import TemporaryDirectory, gettempdir

import click
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PyPDF2 import PdfMerger

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def get_google_credentials():
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


# Function to authenticate and get the Google Document
def get_google_document(credentials, document_id):
    service = build("drive", "v3", credentials=credentials)
    return service.files().get(fileId=document_id).execute()


# Function to download each tab of the Google Document as a PDF
# TODO: this doesn't work, but maybe https://stackoverflow.com/a/79183961
# and maybe this: https://developers.google.com/docs/api/samples/output-json
def download_pdf(credentials, document_id, output_dir):
    service = build("drive", "v3", credentials=credentials)
    request = service.files().export_media(
        fileId=document_id, mimeType="application/pdf"
    )
    with open(f"{output_dir}/{document_id}.pdf", "wb") as f:
        f.write(request.execute())


# Function to merge all downloaded PDFs into a single PDF
def merge_pdfs(pdf_files, output_file):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_file)
    merger.close()


@click.command()
@click.argument("url")
@click.option("--output", default=None, help="Output name of the destination PDF")
def main(url, output):
    # Extract document ID from URL
    document_id = url.split("/d/")[1].split("/")[0]

    # Define the temporary output directory
    temp_dir = TemporaryDirectory(prefix="google-docs-downloader")
    credentials = get_google_credentials()

    # Get Google Document name if output is not provided
    if not output:
        document = get_google_document(credentials, document_id)
        print(document)
        output = document["name"] + ".pdf"

    # # Download PDF
    # download_pdf(credentials, document_id, temp_dir.name)
    #
    # # Merge PDFs (assuming only one PDF for simplicity)
    # pdf_files = [f"{temp_dir.name}/{document_id}.pdf"]
    # merge_pdfs(pdf_files, output)

    # cleanup temp dir
    # temp_dir.cleanup()


if __name__ == "__main__":
    main()
