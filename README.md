# Customer API — Azure Cloud Deployment

A cloud-hosted REST API for managing customer data, built with FastAPI and deployed to Microsoft Azure.

The project demonstrates a complete cloud application architecture including Azure SQL, secure secret management with Azure Key Vault and Managed Identity, automated CI/CD with GitHub Actions and OIDC authentication, unit and integration testing, and application monitoring.

## Architecture

```text
Developer
    |
    | git push
    v
GitHub
    |
    v
GitHub Actions
    |
    |-- Install dependencies
    |-- Run unit tests
    |
    | Tests pass
    v
OIDC Authentication
    |
    v
Azure App Service
    |
    |-- FastAPI application
    |
    |-- Managed Identity ------> Azure Key Vault
    |                              |
    |                              | Secrets
    |                              v
    |                           Application
    |
    |--------------------------> Azure SQL
    |
    `--------------------------> Application Insights
                                  Monitoring & Telemetry
```

### Deployment Flow

1. Code is pushed to the `main` branch.
2. GitHub Actions creates the Python environment and installs dependencies.
3. Unit tests run before deployment.
4. A failed build or unit test prevents deployment.
5. GitHub Actions authenticates to Azure using OIDC.
6. The application is deployed to Azure App Service.
7. The running application uses its Managed Identity to access secrets in Azure Key Vault.
8. The application connects to Azure SQL using its runtime configuration and securely retrieved credentials.
9. Application Insights collects request and performance telemetry.

## Technology Stack

- Python
- FastAPI
- Pydantic
- Azure App Service
- Azure SQL Database
- Azure Key Vault
- Azure Managed Identity
- Azure Application Insights
- OpenTelemetry
- GitHub Actions
- OpenID Connect (OIDC)
- mssql-python
- pytest

## Security

Secrets are not stored in source code or committed to GitHub.

The deployed App Service uses a system-assigned Managed Identity to authenticate to Azure Key Vault. Key Vault stores sensitive application secrets, including database credentials and API authentication secrets.

GitHub Actions authenticates to Azure using OIDC rather than storing a long-lived Azure client secret in the repository.

Protected API routes require an API key.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Check application health |
| GET | `/version` | Return application version information |
| GET | `/customers` | Retrieve customers with pagination |
| POST | `/customers` | Create a customer |
| GET | `/customers/{customer_id}` | Retrieve a specific customer |
| PUT | `/customers/{customer_id}` | Update a customer |
| DELETE | `/customers/{customer_id}` | Delete a customer |
| GET | `/customers/search` | Search customers |
| GET | `/customers/stats` | Retrieve customer statistics |
| POST | `/customers/bulk` | Create customers in bulk |

## Testing

The project separates unit tests from integration tests.

### Unit Tests

Unit tests use fake dependencies so they can test application behavior without connecting to Azure SQL or Azure Key Vault.

Run:

```bash
python -m pytest tests/unit -v
```

The GitHub Actions CI pipeline automatically runs these tests before deployment.

### Integration Tests

Integration tests exercise the application with its real external dependencies and are kept separate from the CI unit-test gate.

Run:

```bash
python -m pytest tests/integration -v
```

## Local Development

### 1. Clone the repository

```bash
git clone <repository-url>
cd customer-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure local environment

Create a `.env` file containing the required local configuration.

Do not commit `.env` or application secrets to source control.

### 5. Start the API

```bash
python -m uvicorn main:app --reload
```

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## CI/CD

The repository uses GitHub Actions for continuous integration and deployment.

Every push to `main` triggers the pipeline:

```text
Push
  ↓
Build
  ↓
Install Dependencies
  ↓
Unit Tests
  ↓
OIDC Azure Login
  ↓
Deploy to App Service
```

If the unit tests fail, the deployment job does not run.

## Monitoring

The deployed API is connected to Azure Application Insights.

Application Insights provides visibility into:

- incoming requests
- failed requests
- response times
- application telemetry
- runtime performance

## Live Deployment

The API is deployed on Microsoft Azure App Service.

Health endpoint:

```text
https://customer-api-wonderful.azurewebsites.net/health
```

Interactive API documentation:

```text
https://customer-api-wonderful.azurewebsites.net/docs
```

## Project Purpose

This project was built as a hands-on cloud engineering project to demonstrate the transition of a locally developed REST API into a secure, monitored, automatically deployed Azure application.

It demonstrates API development, cloud deployment, identity-based secret access, database integration, automated testing, CI/CD, and observability.