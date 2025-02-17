# google-docs-pdf-downloader

Download Google Documents with multiple tabs as a single PDF

For more about Tabs in Google Documents check these topics:

- [Use document tabs in Google Docs](https://support.google.com/docs/answer/15499791)
- [Work with tabs](https://developers.google.com/docs/api/how-tos/tabs)

## Requirements

- Python >= `3.10`

## Setup

### Setup Google project and credentials

1. Create a Google Project in [console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate) or use an existing one
2. Create new OAuth Credentials in [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) and download the client secret JSON
3. Save the secrets JSON to `config/credentials.json`
4. Enable the Google Docs API for your project in [console.cloud.google.com/apis/library/docs.googleapis.com](https://console.cloud.google.com/apis/library/docs.googleapis.com)

### Setup Python

```bash
# create and activate a python venv
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

## Usage

```bash
./google-docs-pdf-downloader GOOGLE_DOCS_URL [--output output-file.pdf]
```

Use `./google-docs-pdf-downloader --help` for more details.
