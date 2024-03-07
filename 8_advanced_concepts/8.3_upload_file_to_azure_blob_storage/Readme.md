# Flask API for Uploading Files to Azure Blob Storage

This Flask API allows you to upload files to Azure Blob Storage and returns a SAS token URL for the uploaded file.

## Prerequisites

Before running this API, make sure you have the following installed:

- Python
- Flask
- Azure Storage Blob library (`azure-storage-blob`)

You also need to have an Azure Blob Storage account with a container created to store the uploaded files.

## Installation

1. Clone this repository:
```
git clone <repository_url>
```

2. Install the required dependencies:
```
pip install Flask azure-storage-blob
```

## Configuration

Before running the API, make sure to set the following environment variables:

- `AZURE_STORAGE_CONNECTION_STRING`: The connection string for your Azure Blob Storage account.
- `CONTAINER_NAME`: The name of the container in your Azure Blob Storage account where the files will be uploaded.
- `ACCOUNT_KEY`: The account key for your Azure Blob Storage account.

You can set these environment variables in your system or create a `.env` file in the project directory and define them there.

## Usage

1. Start the Flask server by running the following command:
```
python app.py
```

2. Send a POST request to the `/upload` endpoint with a file attached.

You can use tools like cURL or Postman to send the POST request.

### Example cURL command:

```bash
curl -X POST -F "file=@/path/to/your/file.mp4" http://localhost:5000/upload
```