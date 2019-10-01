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

def get_blocks(text_block, block_markers,breaking_phrase):
    text_block = ['<START>'] + text_block
    blocks = {x:[] for x in block_markers}
    curr_marker = ''
    for line in text_block:
        if breaking_phrase in line.strip():
            curr_marker = '<START>'
            print("NEW")
        if line.strip() in block_markers:
                curr_marker = line.strip()
                continue
        blocks[curr_marker].append(line)
    return blocks

full_body = get_text('gs://report-ap/test_image.jpg').full_text_annotation.text.splitlines()
record = []
pat_fl = 0
nam_nl = 0
block_markers = ['<START>', 'ENCOUNTER', 'PATIENT', 'GUARANTOR', 'COVERAGE']
breaking_phrase = 'QUAD CITIES'
print(get_blocks(full_body,block_markers,breaking_phrase))
