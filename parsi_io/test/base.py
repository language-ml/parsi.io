import json
import os


class BaseTest:

    def get_testcases(self, addr):
        f = open(os.getcwd()+addr, 'r')
        test_cases = json.load(f)
        f.close()
        return test_cases

    def test_json(self, obj, addr):
        errors = []
        test_cases = self.get_testcases(addr)
        for i in test_cases:
            your_answer = obj.run(i['input'])
            correct_answer = i['outputs']
            d = {k: your_answer[k] for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1}'.format(str(i['id']), str(d[j])))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
