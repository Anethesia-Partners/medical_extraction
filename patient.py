import numpy as np
import re
import os
import googlemaps
import usaddress
import pandas as pd

class Patient:
    def __init__(self,block_markers):

        self.fields = {'address', 'adm diagnosis', 'admitting physician', 'attending physician', 'bed', 'city',
                        'coded procedure', 'contact serial #', 'dob', 'encounter date', 'guarantor', 'guarantor employer', 'guarantor id',
                        'home phone', 'hospital account', 'hospital service', 'mrn', 'name', 'patient class', 'payor', 'po_box', 'primary care provider',
                        'primary phone', 'race', 'relation to patient', 'sex', 'status', 'unit'}
        self.pat_dic = {}
        self.insurance_df = pd.read_excel('./Insurance Companies.xlsx')
        self.update_keys(block_markers)


    def process_gen_info(self,text_block):
        for key, value in text_block.items():

            if key == 'COVERAGE':
                self.process_coverage_info(value)
            else:
                self.process_coloned(value,key)
        self.get_insurance_medcode()

    def process_coverage_info(self, text_block):
        self.coverage_blocks = {'PRIMARY INSURANCE', 'SECONDARY INSURANCE'}
        self.update_keys(self.coverage_blocks)
        blocks = {x:[] for x in self.coverage_blocks}
        curr_marker = ''

        for line in text_block:
            if line.strip() in self.coverage_blocks:
                    curr_marker = line.strip()
                    continue
            elif curr_marker == '':
                continue

            blocks[curr_marker].append(line)

        for key,value in blocks.items():
            self.process_coloned(value,key)
            self.get_address(value,key)



    def process_coloned(self,text_block,key):
        for line in text_block:
            curr_line = line.strip().lower().split(':')

            if any(field == curr_line[0] for field in self.fields) and len(curr_line)>1 and '' not in curr_line:
                if key != '<START>':
                    self.pat_dic[key+ '_' + curr_line[0].strip()] = curr_line[1].strip()
                else:
                    self.pat_dic[curr_line[0].strip()] = curr_line[1].strip()

    def get_address(self,text_block,key):
        block_string = ' '.join(text_block).lower()
        po_pattern = re.compile(r'(po box)\s*\d+')
        po_box = re.search(po_pattern, block_string)
        if po_box != None:
            self.pat_dic[key+ '_' + 'po_box'] = po_box[0].split()[-1]

        add_pattern = re.compile(r'([A-Z,a-z,0-9][^.!\-:;,\s]+)[,|\s]+([A-Z,a-z][^.!\-:;]+?)\s*(\d{5})')
        address = re.findall(add_pattern, block_string)
        for matches in address:
            try:
                tags = usaddress.tag(' '.join(matches))[0]
                if 'PlaceName' in tags.keys() and 'StateName' in tags.keys():
                    self.pat_dic[key+ '_' + 'address'] = ' '.join(matches)

            except:
                print('Error!....')



    def update_keys(self,block_markers):
        for key in self.fields:
            for pref in block_markers:
                if pref != '<START>':
                    self.pat_dic[pref+ '_' + key] = None
                else:
                    self.pat_dic[key] = None

    def get_insurance_medcode(self):
        for cov_block in self.coverage_blocks:
            print (self.pat_dic[cov_block+ '_' + 'po_box'],self.pat_dic[cov_block + '_' + 'address'])
            if self.pat_dic[cov_block + '_' + 'address'] != None and self.pat_dic[cov_block+ '_' + 'po_box'] != None:
                tags_add = usaddress.tag(self.pat_dic[cov_block + '_' + 'address'])[0]
                print(self.insurance_df[(self.insurance_df['Address'] == "PO BOX " + self.pat_dic[cov_block + '_' + 'po_box']) & (self.insurance_df['City'] == tags_add['PlaceName'].upper()) & (self.insurance_df['St'] == tags_add['StateName'].upper())])


    def csv_rep(self):
        return self.pat_dic
