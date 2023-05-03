from base import BaseTest
from parsi_io.modules.address_extractor.address_extractions import AddressExtractor


class TestAddressExtraction(BaseTest):
    def run_test(self):
        errors = []
        test_cases = self.get_testcases('/parsi_io/test/testcases/AddressExtraction.json')
        obj = AddressExtractor()

        for i in test_cases:
            your_answer = obj.run(i['input'])
            correct_answer = i['outputs']
            d = {k: (your_answer[k], correct_answer[k]) for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(i['id'], d[j][0], d[j][1]))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))


if __name__ == '__main__':
    TestAddressExtraction().run_test()

