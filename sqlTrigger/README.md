# SQL Trigger Binding for Redis Demo

This SQL Trigger will work with the Redis Vector DB demo. It tracks updates to the styles table, creates embedings, and inserts the JSON back into the Redis Vector DB.

## Prerequisits

Run the following to prepare your environment for the trigger function

### Install the following VS Code Extentions
- Python (ms-python.python)
- Azure Functions (ms-azuretools.vscode-azurefunctions)
- Jupyter (ms-toolsai.jupyter)

### Install the python libraries
```BASH
pip install -r requirements.txt
```

### Install functions core tools
```BASH
npm install -g azure-functions-core-tools@4
```

### Update the environments file (.env)
You can use the template.env as a template. Copy and rename the file to .env and fill out the following entries for the Azure Cache for Redis:

```BASH
DB_LIMIT=100
REDIS_HOST=''
REDIS_PORT=''
REDIS_PASSWORD=''
REDIS_KEY=''
```

### Update the local.settings.json file with the database connection information
Replace **SERVER_NAME**, **DB_NAME**, **USER**, **PASSWORD**, and change the **port number** if necessary.

```JSON
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "connection-string": "Server=tcp:SERVER_NAME.database.windows.net,1433;Initial Catalog=DB_NAME;Persist Security Info=False;User ID=USER;Password=PASSWORD;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  }
}
```

