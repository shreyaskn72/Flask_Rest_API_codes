# Azure Blob Storage File Uploader Function

This Azure Function written in Python allows you to upload files to Azure Blob Storage and obtain both a regular URL and a SAS token URL for the uploaded file.

## Prerequisites

- Azure Blob Storage account
- Azure Function App created
- Python environment with Azure Functions SDK installed
- Azure Storage Blob client library installed (`azure-storage-blob`)

## Setup

1. Clone this repository or copy the provided Python script (`upload_file.py`) to your Azure Function project directory.

2. Install the required Python packages by running:

    ```
    pip install -r requirements.txt
    ```

3. Set up your Azure Blob Storage connection string as an environment variable named `AzureWebJobsStorage` in your Azure Function App settings.

4. Replace `"your-container-name"` in the script with the name of your Azure Blob Storage container.

## Usage

1. Deploy the Azure Function to your Azure Function App.

2. Use an HTTP client (e.g., Postman, cURL) to send an HTTP POST request with the file to be uploaded in the request body. Optionally, you can specify the filename in the request headers.

3. The function will upload the file to the specified container in Azure Blob Storage and return a response with both the normal URL and the SAS token URL of the uploaded file.

## Example

Assuming the Azure Function is deployed and running at `https://your-function-app.azurewebsites.net/api/upload`, you can upload a file named `example.txt` using cURL:

```bash
curl -X POST -H "Content-Type: application/octet-stream" --data-binary "@example.txt" https://your-function-app.azurewebsites.net/api/upload -H "filename: example.txt"
```

Replace https://your-function-app.azurewebsites.net/api/upload with the actual URL of your Azure Function endpoint. Make sure to replace example.txt with the actual file you want to upload. This command sends an HTTP POST request with the file contents as the request body and includes the filename in the request headers.

## Note
- Make sure your Azure Function App has the necessary permissions to access the Azure Blob Storage account.
- Ensure that the Azure Blob Storage container is created before running the function.
- The SAS token generated for the file provides read access and expires after one day.

```css
This README.md provides setup instructions, usage guidelines, an example of how to upload a file using cURL, and important notes to consider. Customize the content according to your specific project requirements and preferences.
```
