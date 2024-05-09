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

# Resnet-18 to create image embeddings
img2vec = Img2Vec(cuda=False)

# bert variant to create text embeddings
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

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
        print(f"Processed {str(len(output_dict))} product images")

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
                "usage": row["usage"],
                "image_url": '',
                "keywords": '',
                "brand": '',
                "age_group": ''
            }
        }
        products.append(product)

    return products

def push_redis_data(redis_client, image_vectors, text_vectors, metadata):
    print("push JSON data to Redis")
    pipeline = redis_client.pipeline(transaction=False)
    index=0
    for index in range(len(metadata)):
        # Get Product by id
        query = Query(f"@product_id:[{metadata[index]['product_id']} {metadata[index]['product_id']}]")
        product = redis_client.ft(f"{REDIS_KEY}").search(query)
        if product:
            id = product.docs[0].id
            json_obj = json.loads(product.docs[0]['json'])
            metadata[index]['product_metadata']['image_url'] = json_obj['product_metadata']['image_url']
            
            pipeline.json().set(id, "$", metadata[index])
            if index%50==0:
                pipeline.execute()
    pipeline.execute()

def get_product_from_dict(product_dict, product_id):
    return [value for value in product_dict.values() if value.get('product_id') == product_id]

def set_product_vectors(product_vectors, redis_conn, products_with_pk):
    # iterate through products data and save vectors hash model
    for product in product_vectors:
        product_id = product["product_id"]
        product_pk = get_product_from_dict(products_with_pk, product_id)
        key = f"product_vector:{str(product_id)}"
        redis_conn.hset(
            key,
            mapping={
                "product_id": product_id,

                # Add tag fields to vectors for hybrid search
                "gender": product_pk[0]["gender"],
                "category": product_pk[0]["masterCategory"],

                # add image and text vectors as blobs
                "img_vector": np.array(product["img_vector"], dtype=np.float32).tobytes(),
                "text_vector": np.array(product["text_vector"], dtype=np.float32).tobytes()
        })


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
   
    metadata = create_product_metadata(df[:DB_LIMIT])
    
    #setup Redis for product cache and VSS
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, ssl=True, decode_responses=True)
    set_product_vectors(vector_dict, redis_client, df[:DB_LIMIT].to_dict(orient='index'))
    push_redis_data(redis_client, image_vectors, text_vectors, metadata)

