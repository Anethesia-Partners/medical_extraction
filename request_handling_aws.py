import argparse
import io
import boto3
from trp import Document

# https://facesheet-ap.s3.amazonaws.com/000a5953-9b4a-4abd-9002-a1347ba949e2.png
client_text = boto3.client('textract')
client_s3 = boto3.client('s3')
client_dynamo = boto3.client('dynamodb')
med_comp_client = boto3.client("comprehendmedical")

def get_text(bucket_name, key):
    response = client_text.detect_document_text( Document={'S3Object': {'Bucket': bucket_name, 'Name': key}})
    doc_text = []
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            doc_text.append(item["Text"])
    return doc_text, key.split("/")[1].split(".")[0]

def get_all_text(bucket_name, directory, event_list = None, require_form=False):

    full_text = []
    ids = []
    form_data = []

    if event_list != None:
        for s3_item in event_list:
            next_doc, id = get_text(bucket_name, s3_item['s3']['object']['key'])
            ids.append(id)
            full_text += next_doc
            if require_form == True:
                form = get_text_analysis(bucket_name, s3_item['s3']['object']['key'])
                form_data.append(form)

    else:
        bucket_list = client_s3.list_objects_v2(Bucket = bucket_name, Prefix=directory)
        for blob in bucket_list['Contents']:
            if blob['Key'] != directory:
                print("----------------------" + blob['Key'] + "---------------------------")
                next_doc, id = get_text(bucket_name,blob['Key'])
                print(id)
                print(next_doc)
                ids.append(id)
                full_text += next_doc
                # print(full_text)
                for line in next_doc:
                    print (line)
                if require_form == True:
                    form = get_text_analysis(bucket_name, blob['Key'])
                    form_data.append(form)

    if len(form_data) > 0:
        return full_text, ids, form_data
    else:
        return full_text, ids

def get_comprehend(text_block):
    detection_map = med_comp_client.detect_entities_v2(Text='\n'.join(text_block))
    # out_map = {}
    # for entity in detection_map["Entities"]:
    #     out_map[entity['Type']] = entity['Text']

    # return out_map
    return detection_map["Entities"]

def get_text_analysis(bucket_name, key):
    response_analysis = client_text.analyze_document( Document={'S3Object': {'Bucket': bucket_name, 'Name': key}}, FeatureTypes=['FORMS'])
    extract = Document(response_analysis)
    form_ext = []
    for page in extract.pages:
        print("Key Value Pairs:")
        for headings in page.form.fields:
            print("Detected Key: {}, Detected Value: {}".format(headings.key, headings.value))
            form_ext.append((str(headings.key), str(headings.value)))

    return form_ext

def put_dynamo(table_name, df, ids):
    put_dict = {}
    list_records = df.to_dict("records")
    print(ids)
    for dict,id in zip(list_records,ids):
        for key, val in dict.items():
            if val != None:
                put_dict[key] = {"S" : val}

        print(id)
        put_dict["patient_id"] = {"S" : id}
        client_dynamo.put_item(TableName=table_name, Item=put_dict)
        print("Patient Item Stored. ID = " + id)
