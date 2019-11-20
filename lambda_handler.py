
import os
import sys
import nltk

import moline_sheet_src
import caa_sheet_src
import sag_sheet_src

from request_handling_aws import *


def identify_pipeline(full_body):
    print(dir(moline_sheet_src.main))
    identifiers = {
                    'moline_id' : ('QUAD CITIES',moline_sheet_src.main.run_pipeline),
                    'sag_id' : ('SAINT ANTHONY',sag_sheet_src.main.run_pipeline),
                    'caa_id' : ('Advocate Illinois Masonic Medical Center',caa_sheet_src.main.run_pipeline)
                    }

    for line in full_body:
        for key, val in identifiers.items():
            if nltk.edit_distance(val[0], line.strip())<3:
                return val[1]


def run_pipeline(event, context):
    full_body, ids, form_data = get_all_text(os.getenv("S3_BUCKET_NAME"),os.getenv("BUCKET_DIR"), event_list = event["Records"], require_form=True)

    pipeline_func = identify_pipeline(full_body)


    # block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
    # breaking_phrase = 'QUAD CITIES'

    # patient_list = get_patients(full_body,block_markers,breaking_phrase)
    # fin_df = compile_dataframe(patient_list)
    fin_df = pipeline_func(full_body, form_data)

    put_dynamo(os.getenv("DYNAMO_TABLE_NAME"), fin_df, ids)


if __name__ == "__main__":
    os.environ["S3_BUCKET_NAME"] = "facesheet-ap"
    os.environ["BUCKET_DIR"] = "facesheet_moline/"
    os.environ["DYNAMO_TABLE_NAME"] = "patient_data"
    event = {"Records":[{"s3":{"object":{"key":"facesheet_moline/000a5953-9b4a-4abd-9002-a1347ba949e2.png"}}}]}
    run_pipeline(event, {})
