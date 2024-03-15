import os
import datetime
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Get connection string and container name from environment variables
    connection_string = os.environ["AzureWebJobsStorage"]
    container_name = "your-container-name"
    blob_url_format = "https://{0}.blob.core.windows.net/{1}/{2}"

    try:
        req_body = req.get_body()
        # Check if request body exists and is not empty
        if not req_body:
            return func.HttpResponse(
                "Please provide a file in the request body.",
                status_code=400
            )

        # Create a BlobServiceClient object which will be used to create a container client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a ContainerClient object which will be used to upload the file
        container_client = blob_service_client.get_container_client(container_name)

        # Get file name from request headers or use a default name
        filename = req.headers.get("filename", "default_filename.txt")

        # Upload the file to Azure Blob Storage
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(req_body)

        # Construct the URL of the uploaded file
        blob_url = blob_url_format.format(blob_service_client.account_name, container_name, filename)

        # Generate a SAS token for the blob
        expiry = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token expires in 1 day
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=filename,
            account_key=None,  # Use account key if available, else use account SAS token
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )

        # Construct the SAS token URL of the uploaded file
        sas_token_url = f"{blob_url}?{sas_token}"

        return func.HttpResponse(
            f"File '{filename}' uploaded successfully.\nNormal URL: {blob_url}\nSAS Token URL: {sas_token_url}",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(f"An error occurred: {e}", status_code=500)
