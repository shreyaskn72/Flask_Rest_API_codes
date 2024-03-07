from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Azure Blob Storage credentials
connection_string = "your_storage_connection_string"
container_name = "your_container_name"
account_key = "your_account_key"

# Set maximum content length to 200 MB (adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB limit

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Upload file to Azure Blob Storage using streaming
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)
    with file.stream as stream:
        blob_client.upload_blob(stream)

    # Generate SAS token for the uploaded blob
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=file.filename,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)  # Valid for 1 hour
    )

    # Construct SAS token URL
    sas_token_url = f"{blob_client.url}?{sas_token}"

    return jsonify({'message': 'File uploaded to Azure Blob Storage', 'sas_token_url': sas_token_url}), 200

if __name__ == '__main__':
    app.run(debug=True)
