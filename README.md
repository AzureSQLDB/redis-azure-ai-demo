# Redis Vector Search Demo Application using ACRE and Cache Prefetching from Azure SQL with Azure Functions

## Summary

We based this project from our [Product Search Demo](<https://github.com/redis-developer/redis-product-search>) which showcase how to use Redis as a Vector Db. We modified the demo by adding a Cache Prefetching pattern from Azure SQL to ACRE using Azure Functions. The Azure Function uses a SQL Trigger that will trigger for any updates that happen in the table.

## Features

- Uses Azure Function to sync the updates in Azure SQL to Redis using a Prefetch caching pattern
- Vector Similarity Search
  - by image
  - by text
- Multiple vector indexing types
  - HNSW
  - Flat (brute-force)
- Hybrid Queries
  - Apply tags as pre-filter for vector search

## Architecture


## Prerequisites

- VS Code or Visual Studio
- Python 3.8
- OSX or Windows
- Azure SQL
- Azure Cache for Redis Enterprise
  - Configuration steps [here](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/quickstart-create-redis-enterprise)

## Running the Solution

### Step 1 - Create data to load into Redis

The Jupyter notebook will create two json files with the product metadata and the product vectors. These files will be placed in the data folder. The application will load these files to ACRE and create the indexes automatically when the docker container starts.

1. Run the Jupyter notebook located in data folder

### Step 2 - Load Data to Azure SQL

1. Run the create_aiuser.sql script located in the scripts folder
2. Run the styles_table.sql script located in the scripts folder

- This will also enable CDC on the database and the table

3. Import the styles.csv data to the [aidemo].[styles] table using the import functionality of Azure Data Studio or through any other familiar options

### Step 3 - Run the App

1. Create docker image by running

```sh
docker build -t product-search-app . --no-cache
```

2. Export Redis Endpoint Environment Variables:

```sh
  $ export REDIS_HOST=your-redis-host
  $ export REDIS_PORT=your-redis-port
  $ export REDIS_PASSOWRD=your-redis-password
```

3. Run docker image by running

```sh
docker compose -f docker-cloud-redis.yml up
```


### Step 4 - Run the Azure Function

1. Go to the sqlTrigger folder by running

```sh
cd sqlTrigger
```

2. Run the Azure Function

```sh
func start
```

### Datasets

The dataset was taken from the the following Kaggle links.

- [Large Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset)
- [Smaller Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small)