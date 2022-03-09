from parsi_io.modules.address_extractions import AddressExtraction
from itertools import chain
from base import BaseTest
import collections


class TestAddressExtraction(BaseTest):

    def test_json(self):
        errors = []
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

        test_cases = self.get_testcases('/testcases/AddressExtraction.json')
        o = AddressExtraction()
        for i in test_cases:
            your_answer = o.run(i['input'])
            correct_answer = list(i['outputs'].values())
            while None in correct_answer: correct_answer.remove(None)
            correct_answer = list(chain.from_iterable(correct_answer))
            print(correct_answer)
            print(your_answer)
            if not compare(your_answer, correct_answer):
                errors.append('Input {0}: your answer is {1}'.format(str(i['id']), str(your_answer)))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
