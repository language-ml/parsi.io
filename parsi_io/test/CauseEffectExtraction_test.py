from parsi_io.modules.cause_effect_extractions import CauseEffectExtraction
from itertools import chain
from base import BaseTest
import collections


class TestCauseEffectExtraction(BaseTest):

    def test_json(self):
        errors = []
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

        test_cases = self.get_testcases('/testcases/CauseEffectExtraction.json')
        o = CauseEffectExtraction()
        for i in test_cases:
            your_answer = o.run(i['input'])
            correct_answer = list(i['outputs'].values())
            correct_answer = list(correct_answer)
            print("Testing {0}: ".format(str(i['id']) ))
            print(correct_answer)
            print(your_answer)
            print("***********************************")
            if not compare(your_answer, correct_answer):
                errors.append('Input {0}: your answer is {1}'.format(str(i['id']), str(your_answer)))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))  
