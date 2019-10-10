import numpy as np
import re

class Patient:
    def __init__(self,block_markers):
        self.fields = {'Encounter Date', 'Hospital Account', 'MRN', 'Guarantor', 'Contact Serial #', 'Name', 'Address','City',
                    'Primary Care Provider','DOB','Sex','Race','Primary Phone','Relation to Patient','Guarantor ID','Guarantor Employer',
                    'Status','Home Phone','Patient Class','Hospital Service','Unit','Bed','Admitting Physician','Attending Physician',
                    'Adm Diagnosis', 'Coded Procedure'}
        self.pat_dic = {}
        self.update_keys(block_markers)


    def process_gen_info(self,text_block):
        for key, value in text_block.items():

            if key == 'COVERAGE':
                self.process_coverage_info(value)

            self.process_coloned(value,key)

    def process_coverage_info(self, text_block):
        coverage_blocks = {'PRIMARY INSURANCE', 'SECONDARY INSURANCE'}
        self.update_keys(coverage_blocks)
        blocks = {x:[] for x in coverage_blocks}
        curr_marker = ''

        for line in text_block:
            if line.strip() in coverage_blocks:
                    curr_marker = line.strip()
                    continue
            elif curr_marker == '':
                continue

            blocks[curr_marker].append(line)
        print(blocks)
        for key,value in blocks.items():
            self.process_coloned(value,key)


    def process_coloned(self,text_block,key):
        for line in text_block:
            curr_line = line.strip().split(':')

            if any(field == curr_line[0] for field in self.fields) and len(curr_line)>1 and '' not in curr_line:
                if key != '<START>':
                    self.pat_dic[key+ '_' + curr_line[0].strip()] = curr_line[1].strip()
                else:
                    self.pat_dic[curr_line[0].strip()] = curr_line[1].strip()

    def update_keys(self,block_markers):

        for key in self.fields:
            for pref in block_markers:
                if pref != '<START>':
                    self.pat_dic[pref+ '_' + key] = np.nan
                else:
                    self.pat_dic[key] = np.nan

    def csv_rep(self):
        return self.pat_dic
