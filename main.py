import argparse
from enum import Enum
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw
import os
import tempfile
from pdf2image import convert_from_path, convert_from_bytes
from request_handling import get_text
from patient import Patient
import re
import pandas as pd



def get_patients(text_block, block_markers,breaking_phrase):

    patient_list = []

    text_block = ['<START>'] + text_block
    blocks = {x:[] for x in block_markers}
    curr_marker = ''
    curr_patient = Patient(block_markers=block_markers)

    for line in text_block:

        if breaking_phrase in line.strip():
            curr_patient.process_gen_info(blocks)
            patient_list.append(curr_patient)
            curr_marker = '<START>'
            blocks = {x:[] for x in block_markers}
            curr_patient = Patient(block_markers=block_markers)

        if line.strip() in block_markers:
                curr_marker = line.strip()
                continue

        blocks[curr_marker].append(line.lower())
    curr_patient.process_gen_info(blocks)
    return patient_list

def compile_dataframe(patient_list):
    pat_df = pd.DataFrame()
    for patient in patient_list:
        pat_df = pd.concat([pat_df,pd.DataFrame([patient.csv_rep()], columns=patient.csv_rep().keys())],axis=0,join='outer').reset_index(drop=True)
    pat_df = pat_df.dropna(axis=1, how='all')
    return pat_df

full_body = get_text('gs://report-ap/test_image.jpg').full_text_annotation.text.splitlines()

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
