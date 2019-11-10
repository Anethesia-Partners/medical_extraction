import numpy as np
import re
import os
import googlemaps
import usaddress
import pandas as pd
import nltk
import sys

US_STATES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"}

US_CITY_CORRECTS = {"st louis":"saint louis"}

class Patient:
    def __init__(self,block_markers):

        self.fields = {'address', 'adm diagnosis', 'admitting physician', 'attending physician', 'bed', 'city',
                        'coded procedure', 'contact serial #', 'dob', 'encounter date', 'guarantor', 'guarantor employer', 'guarantor id',
                        'home phone', 'hospital account', 'hospital service', 'mrn', 'name', 'patient class', 'payor', 'po_box', 'primary care provider',
                        'primary phone', 'race', 'relation to patient', 'sex', 'status', 'unit'}
        self.pat_dic = {}
        self.insurance_df = pd.read_excel('../Insurance Companies_Updated.xlsx')
        self.insurance_alias = {'uhc':'united healthcare',}


        self.update_keys(block_markers)


    def process_gen_info(self,text_block):
        for key, value in text_block.items():
            # print (key, value)
            if key == 'COVERAGE':
                self.process_coverage_info(value)
            elif key == '<START>':
                try:
                    self.pat_dic['START_name'] = value[0]
                except:
                    print("No Start Name")
                print("START ADDRESS:\n")
                self.get_address(value,'START')
            else:
                self.process_coloned(value,key)
        self.get_insurance_medcode()

    def process_coverage_info(self, text_block):
        self.coverage_blocks = {'PRIMARY INSURANCE', 'SECONDARY INSURANCE'}
        self.update_keys(self.coverage_blocks)
        blocks = {x:[] for x in self.coverage_blocks}
        curr_marker = ''

        for line in text_block:
            if any(nltk.edit_distance(line.strip(),x)<3 for x in self.coverage_blocks):
                    curr_marker = min([(x, nltk.edit_distance(line.strip(),x)) for x in self.coverage_blocks], key = lambda x: x[1])[0]
                    continue
            elif curr_marker == '':
                continue

            blocks[curr_marker].append(line)

        for key,value in blocks.items():
            self.process_coloned(value,key)
            print("\n" + key)
            print(value)
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

        # add_pattern = re.compile(r'([A-Z,a-z,0-9][^.!\-:;,\s]+)[,|\s]+([A-Z,a-z][^.!\-:;]+?)\s*(\d{5})')
        add_pattern = re.compile(r'([A-Z,a-z,0-9][^!\-:;,]+)[,|\s]+([A-Z,a-z][^.!\-:;]+?)\s*(\d{5})')

        addresses = []

        for line in text_block:
            addresses.append(re.findall(add_pattern, line.lower()))

        print(addresses)
        for matches in addresses:
            if len(matches) > 0:
                try:
                    tags = usaddress.tag(' '.join(matches[0]))[0]
                    if 'PlaceName' in tags.keys() and 'StateName' in tags.keys() and tags['StateName'].upper() in US_STATES:
                        self.pat_dic[key+ '_' + 'address'] = ' '.join(matches[0]).replace('.','')
                        self.pat_dic[key+'_' + 'PlaceName'] = tags['PlaceName']
                        self.pat_dic[key+'_' + 'StateName'] = tags['StateName']


                except:
                    print ("Unexpected error:", sys.exc_info()[0])

        for matches in text_block:
            if len(matches) > 0:
                try:
                    main_tags = usaddress.tag(matches.lower())
                    tags = main_tags[0]
                    if len(main_tags) > 0:
                        if "StreetName" in tags.keys() and "AddressNumber" in tags.keys() and main_tags[1] == 'Street Address' and ('SubaddressType' not in tags.keys() and 'Recipient' not in tags.keys()):
                            if tags["AddressNumber"].isdigit():
                                print(tags)
                                self.pat_dic[key+ '_' + 'street'] = matches.lower()

                except:
                    print ("Unexpected error:", sys.exc_info()[0])

    def update_keys(self,block_markers):
        for key in self.fields:
            for pref in block_markers:
                if pref != '<START>':
                    self.pat_dic[pref+ '_' + key] = None
                else:
                    self.pat_dic[key] = None

    def get_insurance_medcode(self):
        for cov_block in self.coverage_blocks:
            print (cov_block, self.pat_dic[cov_block+ '_' + 'po_box'],self.pat_dic[cov_block + '_' + 'address'])
            if self.pat_dic[cov_block + '_' + 'address'] != None and self.pat_dic[cov_block+ '_' + 'po_box'] != None:
                tags_add = usaddress.tag(self.pat_dic[cov_block + '_' + 'address'])[0]

                for word, replacement in US_CITY_CORRECTS.items():
                    tags_add['PlaceName'] = tags_add['PlaceName'].replace(word, replacement)

                print(tags_add)

                companies_df = self.insurance_df.loc[(self.insurance_df['Address'] == "PO BOX " + self.pat_dic[cov_block + '_' + 'po_box']) &
                (self.insurance_df['City'] == tags_add['PlaceName'].upper()) &
                (self.insurance_df['St'] == tags_add['StateName'].upper())]

                if not companies_df.empty:

                    print(companies_df)
                    if len(companies_df.index) > 1 and self.pat_dic[cov_block + "_payor"] != None:
                        print(self.pat_dic[cov_block + "_payor"])
                        min_dis = (0,10000)
                        company_payor = self.pat_dic[cov_block + "_payor"]

                        for word, replacement in self.insurance_alias.items():
                            company_payor = company_payor.replace(word, replacement)

                        for index, row in companies_df.iterrows():
                            min_dis = min((index,nltk.edit_distance(company_payor, row["Insurance Company Name"].lower())) , min_dis, key=lambda x: x[1])

                        self.pat_dic[cov_block + "_mednetcode"] = companies_df[companies_df.index == min_dis[0]]['MedNetCode'].item()

                        print("MULTIPLE",companies_df[companies_df.index == min_dis[0]]['Insurance Company Name'])
                    else:
                        self.pat_dic[cov_block + "_mednetcode"] = companies_df.iloc[0]['MedNetCode']


                else:
                    self.pat_dic[cov_block + "_mednetcode"] = None
            else:
                self.pat_dic[cov_block + "_mednetcode"] = None
                # print(self.pat_dic[cov_block + "_mednetcode"])
    def csv_rep(self):
        return self.pat_dic
