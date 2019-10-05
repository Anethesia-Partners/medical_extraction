import numpy as np

class Patient:
    def __init__(self,block_markers):
        self.fields = {'Encounter Date', 'Hospital Account', 'MRN', 'Guarantor', 'Contact Serial #', 'Name', 'Address','City',
                    'Primary Care Provider','DOB','Sex','Race','Primary Phone','Relation to Patient','Guarantor ID','Guarantor Employer',
                    'Status','Home Phone','Patient Class','Hospital Service','Unit','Bed','Admitting Physician','Attending Physician',
                    'Adm Diagnosis', 'Coded Procedure'}
        self.pat_dic = {}
        for key in self.fields:
            for pref in block_markers:
                if pref != '<START>':
                    self.pat_dic[pref+ '_' + key] = np.nan
                else:
                    self.pat_dic[key] = np.nan


    def process_gen_info(self,text_block):
        for key, value in text_block.items():
            for line in value:
                curr_line = line.strip().split(':')

                if key == 'COVERAGE':
                    print (line)
                if any(field == curr_line[0] for field in self.fields) and len(curr_line)>1 and '' not in curr_line:

                    if key != '<START>':
                        self.pat_dic[key+ '_' + curr_line[0].strip()] = curr_line[1].strip()
                    else:
                        self.pat_dic[curr_line[0].strip()] = curr_line[1].strip()

    def process_start_info(self, text_block, fields):
        pass


    def process_pat_info(self, text_block, fields):
        pass

    def process_encounter_info(self, text_block, fields):
        pass

    def process_guaranter_info(self, text_block, fields):
        pass

    def process_coverage_info(self, text_block, fields):
        pass

    def csv_rep(self):
        return self.pat_dic
