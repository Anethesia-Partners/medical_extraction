import argparse
import io
import boto3


# https://facesheet-ap.s3.amazonaws.com/000a5953-9b4a-4abd-9002-a1347ba949e2.png
def create_uri(bucket_name, blob_name):
    return "gs://" + bucket_name + "/" + blob_name

def get_text(bucket_name, key):
    client_text = boto3.client('textract')
    response = client_text.detect_document_text( Document={'S3Object': {'Bucket': bucket_name, 'Name': key}})
    doc_text = []
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            doc_text.append(item["Text"])
    return doc_text

def get_all_text(bucket_name, directory):
    prefix = "facesheet_moline/"
    client_s3 = boto3.client('s3')
    bucket_list = client_s3.list_objects_v2(Bucket = bucket_name, Prefix=prefix)
    full_text = []
    # print(bucket)
    for blob in bucket_list['Contents']:
        if blob['Key'] != prefix:
            print("----------------------" + blob['Key'] + "---------------------------")
            next_doc = get_text(bucket_name,blob['Key'])
            print(next_doc)

            full_text += next_doc
            # print(full_text)
            # for line in next_doc:
            #     print (line)

    return full_text
