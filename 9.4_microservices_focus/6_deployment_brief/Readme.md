[![Deploy a Python web app container to ...](https://images.openai.com/thumbnails/84f5274f3223e83e9e83898c14fdd6ad.png)](https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-deploy-python-web-app-azure-04)

To deploy your **Dockerized Flask application with HTTPS and Nginx** to **Azure App Service**, follow these steps:

---

## 🛠️ 1. Prerequisites

Ensure you have the following:

* **Azure CLI**: Installed and configured.
* **Docker**: Installed and running.
* **Azure Subscription**: Active and accessible.
* **Domain Name**: Registered and pointing to Azure (e.g., via A or CNAME records).

---

## 🐳 2. Build and Push Docker Image to Azure Container Registry (ACR)

### 2.1. Create Azure Container Registry

```bash
az acr create --resource-group <ResourceGroupName> --name <ACRName> --sku Basic
```

### 2.2. Log in to ACR

```bash
az acr login --name <ACRName>
```

### 2.3. Build and Tag Docker Image

```bash
docker build -t <ACRName>.azurecr.io/flask-app:v1 .
```

### 2.4. Push Docker Image to ACR

```bash
docker push <ACRName>.azurecr.io/flask-app:v1
```

---

## ☁️ 3. Deploy to Azure App Service

### 3.1. Create App Service Plan

```bash
az appservice plan create --name <AppServicePlanName> --resource-group <ResourceGroupName> --sku B1 --is-linux
```

### 3.2. Create Web App with Docker Image

```bash
az webapp create --resource-group <ResourceGroupName> --plan <AppServicePlanName> --name <WebAppName> --deployment-container-image-name <ACRName>.azurecr.io/flask-app:v1
```

### 3.3. Configure Web App to Use ACR

```bash
az webapp config container set --name <WebAppName> --resource-group <ResourceGroupName> --docker-custom-image-name <ACRName>.azurecr.io/flask-app:v1 --docker-registry-server-url https://<ACRName>.azurecr.io
```

---

## 🔐 4. Set Up HTTPS with Let's Encrypt

Azure App Service provides free SSL certificates for custom domains:

1. **Navigate to your Web App** in the Azure Portal.
2. Go to **TLS/SSL settings** > **Private Key Certificates (.pfx)**.
3. Click **Create App Service Managed Certificate**.
4. Select your custom domain and follow the prompts.

Azure will handle the certificate issuance and renewal automatically.

---

## 🌐 5. Update DNS Records

Ensure your domain's DNS settings point to your Azure Web App:

* **A Record**: Point to the IP address of your Azure Web App.
* **CNAME Record**: Point to `<WebAppName>.azurewebsites.net`.

---

## ✅ 6. Access Your Application

Once DNS propagation is complete, access your application securely via:

```
https://<WebAppName>.<Region>.azurewebsites.net
```

---

For a detailed walkthrough, refer to the official Azure documentation: ([Microsoft Learn][1])


[1]: https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app-for-app-service?utm_source=chatgpt.com "Deploy a Flask or FastAPI web app as a container in Azure App Service - Python on Azure | Microsoft Learn"
