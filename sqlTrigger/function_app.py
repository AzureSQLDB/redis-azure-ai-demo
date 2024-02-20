# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import logging
import azure.functions as func
import pandas as pd
from azure.functions.decorators.core import DataType
import os
#import pyodbc
#import tiktoken
import numpy as np
from openai import AzureOpenAI
from tokenizers import Tokenizer
from sentence_transformers import SentenceTransformer
# for creating image vector embeddings
from PIL import Image
from img2vec_pytorch import Img2Vec
# for Redis
import redis
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from dotenv import load_dotenv

# load connection info from .env
load_dotenv('../.env')
DB_LIMIT=100
REDIS_HOST=os.environ.get('REDIS_HOST')
REDIS_PORT=os.environ.get('REDIS_PORT')
REDIS_PASSWORD=os.environ.get('REDIS_PASSWORD')
REDIS_KEY=os.environ.get('REDIS_KEY')

app = func.FunctionApp()

client = AzureOpenAI(
    api_key = "05c28289fa3d42daa7fa13439cb02f5e",  
    api_version = "2024-02-15-preview",
    azure_endpoint = "https://testwed.openai.azure.com"
)

# Resnet-18 to create image embeddings
img2vec = Img2Vec(cuda=False)

# bert variant to create text embeddings
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

#def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
#    return client.embeddings.create(input = [text], model=model).data[0].embedding

######################## Functions

def get_batch(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def generate_image_vectors(products, image_base_path, batch_size=1000):
    output_dict={}

    for batch in get_batch(products, batch_size):
        product_ids = batch['product_id'].values.tolist()
        image_filenames = [image_base_path + "/" + str(_id) + ".jpg" for _id in product_ids]
        images=[]
        converted=[]

        for img_path, _id in zip(image_filenames, product_ids):
            try:
                img = Image.open(img_path).convert('RGB')
                img = img.resize((224, 224))
                images.append(img)
                converted.append(_id)
            except:
                #unable_to_convert -> skip to the next image
                continue

        #Generate vectors for all images in this batch
        vec_list = img2vec.get_vec(images)

        #update the dictionary to be returned
        batch_dict= dict(zip(converted, vec_list))
        output_dict.update(batch_dict)
        print(f"Processed {str(batch_size)} product images")

    return output_dict

def generate_text_vectors(products_df):
    text_vectors = {}
    # generate text vector
    for index, row in products_df.iterrows():
        text_vector = model.encode(row["product_text"])
        text_vectors[row["product_id"]] = text_vector.astype(np.float32)
    
    print(f"Processed {str(len(text_vectors))} product text fields")
    return text_vectors

# combine into a single json file
def combine_vector_dicts(txt_vectors, img_vectors, products):
    product_vectors = []
    for _, row in products.iterrows():
        try:
            _id = row["product_id"]
            text_vector = txt_vectors[_id].tolist()
            img_vector = img_vectors[_id].tolist()
            vector_dict = {
                "text_vector": text_vector,
                "img_vector": img_vector,
                "product_id": _id
            }
            product_vectors.append(vector_dict)
        except KeyError:
            continue
    return product_vectors

def write_product_vector_json(vector_dict):
    product_vector_json = json.dumps(vector_dict)
    with open("./product_vectors.json", "w") as f:
        f.write(product_vector_json)

def write_product_metadata_json(metadata):

    products_json = json.dumps(metadata)
    with open("./product_metadata.json", "w") as f:
        f.write(products_json)

def create_product_metadata(metadata_df):
    products = []
    for _, row in metadata_df.iterrows():
        product = {
            "product_id": row["product_id"],
            # create a text based representation to create a semantic embedding with
            "product_metadata": {
                "name": row["productDisplayName"],
                "gender": row["gender"],
                "master_category": row["masterCategory"],
                "sub_category": row["subCategory"],
                "article_type": row["articleType"],
                "base_color": row["baseColour"],
                "season": row["season"],
                "year": row["year"],
                "usage": row["usage"]
            }
        }
        products.append(product)

    return products

def create_redis_index(redis_client, vector_dim, text_dim):
    print("create index for product and vector data")
    schema = (
        TextField("$.product_id", no_stem=True, as_name="product_id"),
        TextField("$.gender", no_stem=True, as_name="gender"),
        NumericField("$.masterCategory", as_name="category"),
        TagField("$.subCategory", as_name="sub"),
        TextField("$.articleType", as_name="type"),
        TextField("$.baseColor", as_name="color"),
        TextField("$.season", as_name="season"),
        NumericField("$.year", as_name="year"),
        TextField("$.usage", as_name="usage"),
        TextField("$.productDisplayName", as_name="name"),
        VectorField(
            "$.image_embeddings",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": vector_dim,
                "DISTANCE_METRIC": "COSINE",
            },
            as_name="image_vectors",
        ),
        VectorField(
            "$.text_embeddings",
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": text_dim,
                "DISTANCE_METRIC": "COSINE",
            },
            as_name="text_vectors",
        ),
    )
    definition = IndexDefinition(prefix=[f"{{{REDIS_KEY}}}:"], index_type=IndexType.JSON)
    
    try:
        res = redis_client.ft(f"idx:{REDIS_KEY}").create_index(
            fields=schema, definition=definition
        )
    except:
        print("index already exists")

def push_redis_data(redis_client, image_vectors, text_vectors, metadata):
    print("push JSON data to Redis")
    pipeline = redis_client.pipeline()
    index=0
    for index in range(len(metadata)):
        redis_key = f"{{{REDIS_KEY}}}:{metadata[index]['product_id']:03}"
        pipeline.json().set(redis_key, "$", metadata[index])
        pipeline.json().set(redis_key, "$.image_embeddings", image_vectors[metadata[index]['product_id']].tolist())
        pipeline.json().set(redis_key, "$.text_embeddings", text_vectors[metadata[index]['product_id']].tolist())
        if index%50==0:
            pipeline.execute()
    pipeline.execute()




# The function gets triggered when a change (Insert, Update, or Delete)
# is made to the Styles table.

@app.function_name(name="redisDemoTrigger")
@app.sql_trigger(arg_name="styles",
                        table_name="aidemo.styles",
                        connection_string_setting="connection-string")
def products_trigger(styles: str) -> None:
    productData = []
    jdata = json.loads(styles)

    for item in jdata:
        productData.append(item["Item"])

    df = pd.DataFrame(productData) #json_normalize(item["Item"])
    df["product_text"] = df.apply(lambda row: f"name {row['productDisplayName']} category {row['masterCategory']} subcategory {row['subCategory']} color {row['baseColour']} gender {row['gender']}".lower(), axis=1)
    df.rename({"id":"product_id"}, inplace=True, axis=1)


########### New Finishing Steps

    #process vector and metadata for products
    data_path = "../app/vecsim_app/static/images"
    image_vectors = generate_image_vectors(df[:DB_LIMIT], data_path, DB_LIMIT)
    text_vectors = generate_text_vectors(df[:DB_LIMIT])
    vector_dict = combine_vector_dicts(text_vectors, image_vectors, df)
    image_dim = [len(i) for i in image_vectors.values()][0]
    text_dim = [len(i) for i in text_vectors.values()][0]

    metadata = create_product_metadata(df[:DB_LIMIT])
    #optional write to file system
    write_product_metadata_json(metadata)
    write_product_vector_json(vector_dict)


    #setup Redis for product cache and VSS
    
    #vector_dim = len(vector_dict[1])
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    create_redis_index(redis_client, image_dim, text_dim)
    push_redis_data(redis_client, image_vectors, text_vectors, metadata)

