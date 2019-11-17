
import os
import sys

sys.path.append(os.path.abspath("moline_sheet_src/"))

from moline_sheet_src.main import *
from request_handling_aws import *



def run_pipeline(event, context):
    full_body, ids = get_all_text(os.getenv("S3_BUCKET_NAME"),os.getenv("BUCKET_DIR"), event["Records"])
    block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
    breaking_phrase = 'QUAD CITIES'
    patient_list = get_patients(full_body,block_markers,breaking_phrase)
    fin_df = compile_dataframe(patient_list)
    put_dynamo(os.getenv("DYNAMO_TABLE_NAME"), fin_df, ids)


if __name__ == "__main__":
    os.environ["S3_BUCKET_NAME"] = "facesheet-ap"
    os.environ["BUCKET_DIR"] = "facesheet_moline/"
    os.environ["DYNAMO_TABLE_NAME"] = "patient_data"
    event = {"Records":[{"s3":{"object":{"key":"facesheet_moline/000a5953-9b4a-4abd-9002-a1347ba949e2.png"}}}]}
    run_pipeline(event, {})
