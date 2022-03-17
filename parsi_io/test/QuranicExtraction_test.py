from parsi_io.modules.quranic_extractions import QuranicExtraction
from base import *


class TestQuranicExtraction(BaseTest):

    def get_testcases(self, addr):
        f = open(os.getcwd()+addr, 'r', encoding='UTF-8')
        test_cases = json.load(f)
        f.close()
        return test_cases

    def run_test(self, obj, addr):
        errors = []
        test_cases = self.get_testcases(addr)
        for i in test_cases:
            your_initial_answer = obj.run(i['input'])
            your_initial_answer = sorted(your_initial_answer, key= lambda x: x['input_span'][0])

            input_span = []
            quran_id = []
            for ans in your_initial_answer:
                if ans['input_span'] in input_span:
                    quran_id[-1].append(ans['quran_id'])
                else:
                    input_span.append(ans['input_span'])
                    quran_id.append([ans['quran_id']])
            for ind in range(len(quran_id)):
                quran_id[ind] = sorted(quran_id[ind], key=lambda x: (int(x.split('##')[0]), int(x.split('##')[1])))

            your_answer = {}
            your_answer['input_span'] = input_span
            your_answer['quran_id'] = quran_id

            correct_answer = i['outputs']
            d = {k: (your_answer[k], correct_answer[k]) for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(i['id'], d[j][0], d[j][1]))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

    def test_quranic_extraction(self):
        os.chdir('../modules')
        obj = QuranicExtraction(model = 'exact', precompiled_patterns='prebuilt', num_of_output_in_apprx_model=5)
        os.chdir('../test')
        self.run_test(obj, '/testcases/QuranicExtraction.json')
