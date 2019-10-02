
class Patient:
    def __init__(self):
        self.pat_dic = {}
        self.fields = {'Encounter Date', 'Hospital Account', 'MRN', 'Guarantor', 'Contact Serial #', 'Name', 'Address','City'}
    # def process_block(self, text_block, fields):
    #     self.process_pat_info(text_block['PATIENT'], fields)
    #     self.process_start_info(text_block['<START>'], fields)
    #     self.process_encounter_info(text_block['ENCOUNTER'], fields)
    #     self.process_guaranter_info(text_block['GUARANTOR'], fields)
    #     self.process_coverage_info(text_block['COVERAGE'], fields)


    def process_gen_info(self,text_block):
        for key, value in text_block.items():
            for line in value:
                if any(field == line.split(':')[0] for field in self.fields) and len(line.split(':'))>1:
                    print (line)
                    if key != '<START>':
                        self.pat_dic[key+ '_' + line.split(':')[0].strip()] = line.split(':')[1].strip()
                    else:
                        self.pat_dic[line.split(':')[0].strip()] = line.split(':')[1].strip()

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
