from parsi_io.modules.number_extractor import NumberExtractor
from .base import BaseTest


class TestNumberExtraction(BaseTest):
    def test_json(self):
        errors = []

        test_cases = self.get_testcases('testcases/NumberExtraction.json')
        o = NumberExtractor()
        for i in test_cases:
            predicted_answer = o.run(i['input'])
            correct_answer = i['output']

            for x1, x2 in zip(predicted_answer, correct_answer):
                self.assertListEqual(x1['span'], x2['span'])
                self.assertEquals(x1['value'], x2['value'])
