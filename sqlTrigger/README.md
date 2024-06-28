# SQL Trigger Binding for Redis Demo

This SQL Trigger will work with the Redis Vector DB demo. It tracks updates to the styles table, creates embedings, and inserts the JSON back into the Redis Vector DB.

## Prerequisits

Run the following to prepare your environment for the trigger function

### Install the following VS Code Extentions
- Python (ms-python.python)
- Azure Functions (ms-azuretools.vscode-azurefunctions)
- Jupyter (ms-toolsai.jupyter)

### Install the python libraries

1. Go to the sqlTrigger folder by running the following in the terminal:

    ```sh
    cd /workspaces/redis-azure-ai-demo/sqlTrigger
    ```

1. Run the following code in the terminal

    ```BASH
    pip install -r requirements.txt
    ```

### Install functions core tools

1. Again, in the terminal, same sqlTrigger directory, run the following to install Azure Functions Core

    ```BASH
    npm install -g azure-functions-core-tools@4
    ```

### Update the local.settings.json file with the database connection information

Open the [local.settings.json](./local.settings.json) file and replace **SERVER_NAME**, **DB_NAME**, **USER**, **PASSWORD**, and change the **port number** if necessary.

> [!IMPORTANT]  
> Remember to use the aiuser and password for **USER** and **PASSWORD** in the [local.settings.json](./local.settings.json) file!


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
### Start the Azure SQL Trigger Function

1. Again, in the terminal, run the following to start the Azure SQL Trigger Function

    ```sh
    func host start
    ```
