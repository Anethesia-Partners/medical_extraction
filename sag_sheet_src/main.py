import sys
import os
sys.path.append(os.path.abspath("../"))

import argparse
from enum import Enum
import io
from gcloud import storage
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import os
import tempfile
from pdf2image import convert_from_path, convert_from_bytes
from request_handling_aws import get_text, get_all_text
from patient import Patient
import re
import pandas as pd
import nltk


block_markers = ['<START>', 'NAME AND ADDRESS', 'EMERGENCY CONTACT NAME AND ADDRESS', 'PRIMARY INSURANCE', 'GUARANTOR', 'ADMITTING PHYSICIAN']
breaking_phrase = 'SAINT ANTHONY'


def get_patients(text_block, form_data, block_markers, breaking_phrase):

    patient_list = []

    text_block = ['<START>'] + text_block
    blocks = {x:[] for x in block_markers}
    curr_marker = ''
    curr_patient = Patient(block_markers=block_markers)

    i = 0
    for line in text_block:
        nxt_ln = 0
        if nltk.edit_distance(breaking_phrase, line.strip())<3:
            for key,val in blocks.items():
                print("\n\n" + key)
                print(val)
            if len(blocks['<START>']) == 0:
                continue
            curr_patient.process_gen_info(blocks, form_data[i])
            i += 1
            patient_list.append(curr_patient)
            curr_marker = '<START>'
            blocks = {x:[] for x in block_markers}
            curr_patient = Patient(block_markers=block_markers)

        for block_marker in block_markers:
            if nltk.edit_distance(block_marker, line.strip())<3:
                curr_marker = block_marker
                nxt_ln = 1
                break

        if nxt_ln == 1:
            continue

        blocks[curr_marker].append(line)
    for key,val in blocks.items():
        print("\n\n" + key)
        print(val)
    curr_patient.process_gen_info(blocks, form_data[i])
    patient_list.append(curr_patient)
    return patient_list

def compile_dataframe(patient_list):
    pat_df = pd.DataFrame()
    for patient in patient_list:
        pat_df = pd.concat([pat_df,pd.DataFrame([patient.csv_rep()], columns=patient.csv_rep().keys())],axis=0,join='outer').reset_index(drop=True)
    pat_df = pat_df.dropna(axis=1, how='all')

    dob_cols = [col for col in pat_df.columns if 'dob' in col]
    print("DOB COLS:", dob_cols)
    print(pat_df)
    for col in dob_cols:
        pat_df[col] = pat_df[col].astype(str).apply(lambda x:  x.split(" ")[0] if (x != None) else x)
    return pat_df

def run_pipeline(full_body, form_data=None):
    print("RUNNING SAG PIPELINE........")
    block_markers = ['<START>', 'NAME AND ADDRESS', 'EMERGENCY CONTACT NAME AND ADDRESS', 'PRIMARY INSURANCE', 'GUARANTOR', 'ADMITTING PHYSICIAN']
    breaking_phrase = 'SAINT ANTHONY'
    patient_list = get_patients(full_body, form_data, block_markers, breaking_phrase)
    fin_df = compile_dataframe(patient_list)
    return fin_df

if __name__ == "__main__":
    full_body, ids, form_data = get_all_text("facesheet-ap","facesheet_sag/", require_form=True)
    record = []
    pat_fl = 0
    nam_nl = 0
    block_markers = ['<START>', 'NAME AND ADDRESS', 'EMERGENCY CONTACT NAME AND ADDRESS', 'PRIMARY INSURANCE', 'GUARANTOR', 'ADMITTING PHYSICIAN']
    breaking_phrase = 'SAINT ANTHONY'
    patient_list = get_patients(full_body, form_data, block_markers, breaking_phrase)
    fin_df = compile_dataframe(patient_list)
    fin_df.to_excel("./output_fin.xlsx")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(fin_df)
