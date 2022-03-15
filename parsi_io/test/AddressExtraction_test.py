from parsi_io.modules.address_extractions import AddressExtraction
# from itertools import chain
from .base import *
# import collections


class TestAddressExtraction(BaseTest):


    def test_address_extraction(self):
        obj = AddressExtraction()
        self.run_test(obj, '/test/testcases/AddressExtraction.json')

        # errors = []
        # text_list = []
        # span_list = []
        # compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

        # test_cases = self.get_testcases('/test/testcases/AddressExtraction.json')

        # your_answer = o.run(i['input'])

        #     correct_answer = list(i['outputs'].values())
        #     while None in correct_answer: correct_answer.remove(None)
        #     correct_answer = list(chain.from_iterable(correct_answer))
        #     for i in your_answer:
        #         text_list.append(i[0])
        #         span_list.append(i[1])
        #     assert False, (your_answer,correct_answer)

        #     if not compare(your_answer, correct_answer):
        #         errors.append('Input {0}: your answer is {1}'.format(str(i['id']), str(your_answer)))
        #     if not compare(your_answer, correct_answer):
        #         errors.append('Input {0}: your answer is {1}'.format(str(i['id']), str(your_answer)))
        # assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
