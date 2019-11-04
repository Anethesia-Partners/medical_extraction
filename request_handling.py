import argparse
from google.cloud import vision
from google.cloud.vision import types
import io
from gcloud import storage

def create_uri(bucket_name, blob_name):
    return "gs://" + bucket_name + "/" + blob_name

def get_text(image_uri):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = image_uri
    response = client.document_text_detection(image=image)
    document = response
    return response

def get_all_text(bucket_name, directory):
    client = storage.Client(project='medical-extraction')
    bucket = client.get_bucket(bucket_name)
    full_text = []

    for blob in bucket.list_blobs(prefix=directory):
        print(blob.name)
        full_text += get_text(create_uri(bucket_name,blob.name)).full_text_annotation.text.splitlines()
        # print(full_text)
        for line in full_text:
            print (line)

    return full_text
