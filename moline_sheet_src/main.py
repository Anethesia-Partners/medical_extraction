import sys
import os
sys.path.append(os.path.abspath("./"))

# import argparse
# from enum import Enum
import io
# from PIL import Image, ImageDraw
import os
# import tempfile
# from pdf2image import convert_from_path, convert_from_bytes
from request_handling_aws import get_text, get_all_text
from patient import Patient
import re
import pandas as pd

block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
breaking_phrase = 'QUAD CITIES'

def get_patients(text_block, block_markers,breaking_phrase):

    patient_list = []

    text_block = ['<START>'] + text_block
    blocks = {x:[] for x in block_markers}
    curr_marker = ''
    curr_patient = Patient(block_markers=block_markers)

    for line in text_block:

        if breaking_phrase in line.strip():
            for key,val in blocks.items():
                print("\n\n" + key)
                print(val)
            curr_patient.process_gen_info(blocks)
            patient_list.append(curr_patient)
            curr_marker = '<START>'
            blocks = {x:[] for x in block_markers}
            curr_patient = Patient(block_markers=block_markers)


        marker_change = 0
        for block_marker in block_markers:
            if block_marker in line.strip():
                    curr_marker = block_marker
                    marker_change = 1
                    break

        if marker_change == 1:
            continue

        blocks[curr_marker].append(line)

    curr_patient.process_gen_info(blocks)
    patient_list.append(curr_patient)
    return patient_list

def compile_dataframe(patient_list):
    pat_df = pd.DataFrame()
    for patient in patient_list:
        to_concat_df = patient.csv_rep()
        pat_df = pd.concat([pat_df,pd.DataFrame([to_concat_df], columns=patient.csv_rep().keys())],axis=0,join='outer').reset_index(drop=True)
    pat_df = pat_df.dropna(axis=1, how='all')

    dob_cols = [col for col in pat_df.columns if 'dob' in col]
    print("DOB COLS:", dob_cols)
    for col in dob_cols:
        pat_df[col] = pat_df[col].apply(lambda x:  x.split(" ")[0] if (x != None) else x)
    return pat_df.iloc[1:]

def run_pipeline(full_body, form_data=None):
    print("RUNNING MOLINE PIPELINE........")
    block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
    breaking_phrase = 'QUAD CITIES'
    patient_list = get_patients(full_body,block_markers,breaking_phrase)
    fin_df = compile_dataframe(patient_list)
    return fin_df

if __name__ == "__main__":
    full_body, ids = get_all_text("facesheet-ap","facesheet_moline/")
    print(full_body)
    record = []
    pat_fl = 0
    nam_nl = 0
    block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
    breaking_phrase = 'QUAD CITIES'
    patient_list = get_patients(full_body,block_markers,breaking_phrase)
    fin_df = compile_dataframe(patient_list)
    fin_df.to_excel("./output_fin.xlsx")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(fin_df)
