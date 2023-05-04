from base import BaseTest
from parsi_io.modules.price_quantity_extractor.price_quantity_extraction import PriceAndQuantityExtraction


class TestPriceAndQuantityExtractor(BaseTest):    
    def run_test(self):
        errors = []
        test_cases = self.get_testcases('/parsi_io/test/testcases/PriceAndQuantityExtraction.json')
        obj = PriceAndQuantityExtraction()

        for i in test_cases:
            your_answer = obj.run(i['input'])
            correct_answer = i['outputs']
            d = {k: (your_answer[k], correct_answer[k]) for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(i['id'], d[j][0], d[j][1]))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))


if __name__ == '__main__':
    TestPriceAndQuantityExtractor().run_test()
