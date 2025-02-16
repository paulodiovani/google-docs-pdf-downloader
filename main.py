from os import getenv
import click
from googleapiclient.discovery import build
from PyPDF2 import PdfMerger


# Function to authenticate and get the Google Document
def get_google_document(api_key, document_id):
    service = build("drive", "v3", developerKey=api_key)
    return service.files().get(fileId=document_id).execute()


# Function to download each tab of the Google Document as a PDF
def download_pdf(api_key, document_id, output_dir):
    service = build("drive", "v3", developerKey=api_key)
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

    # Define service account file and output directory
    api_key = getenv('GOOGLE_API_KEY')
    output_dir = "output"

    # Get Google Document name if output is not provided
    if not output:
        document = get_google_document(api_key, document_id)
        output = document["name"] + ".pdf"

    # Download PDF
    download_pdf(api_key, document_id, output_dir)

    # Merge PDFs (assuming only one PDF for simplicity)
    pdf_files = [f"{output_dir}/{document_id}.pdf"]
    merge_pdfs(pdf_files, output)


if __name__ == "__main__":
    main()
