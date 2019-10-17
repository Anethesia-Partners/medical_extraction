import numpy as np
import re
import os
import googlemaps
import usaddress

class Patient:
    def __init__(self,block_markers):

        self.fields = {'encounter date', 'hospital account', 'mrn', 'guarantor', 'contact serial #', 'name', 'address','city',
                    'primary care provider','dob','sex','race','primary phone','relation to patient','guarantor id','guarantor employer',
                    'status','home phone','patient class','hospital service','unit','bed','admitting physician','attending physician',
                    'adm diagnosis', 'coded procedure'}
        self.pat_dic = {}
        self.g_map_client = googlemaps.Client(os.getenv("GOOGLE_GEOCODING_KEY"))

        self.update_keys(block_markers)


    def process_gen_info(self,text_block):
        for key, value in text_block.items():

            if key == 'COVERAGE':
                self.process_coverage_info(value)

            self.process_coloned(value,key)

    def process_coverage_info(self, text_block):
        coverage_blocks = {'primary insurance', 'secondary insurance'}
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
        # print(blocks)

        self.get_address(text_block)
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

    def get_address(self,text_block):
        block_string = ' '.join(text_block)
        po_pattern = re.compile(r'(po box)\s*\d+')
        add_pattern = re.compile(r'([A-Z,a-z,0-9][^.!\-:;,\s]+)[,|\s]+([A-Z,a-z][^.!\-:;]+?)\s*(\d{5})')
        po_box = re.search(po_pattern, block_string)
        address = re.findall(add_pattern, block_string)
        for matches in address:
            tags = usaddress.tag(' '.join(matches))[0]
            if 'PlaceName' in tags.keys() and 'StateName' in tags.keys():
                print(tags)
        print(po_box)


    def update_keys(self,block_markers):
        for key in self.fields:
            for pref in block_markers:
                if pref != '<START>':
                    self.pat_dic[pref+ '_' + key] = np.nan
                else:
                    self.pat_dic[key] = np.nan



    def csv_rep(self):
        return self.pat_dic
