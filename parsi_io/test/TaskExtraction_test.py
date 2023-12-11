from parsi_io.modules.address_extractor.address_extractions import AddressExtractor
from parsi_io.modules.task_extractor.TaskRunner import
from parsi_io.modules.number_extractor import NumberExtractor
from .base import BaseTest


class TestNumberExtraction(BaseTest):
    def test_json(self):
        errors = []

        test_cases = self.get_testcases('parsi_io/test/testcases/TaskExtraction.json')
        o = NumberExtractor()
        for i in test_cases:
            predicted_answer = o.run(i['input'])
            correct_answer = i['output']

            for x1, x2 in zip(predicted_answer, correct_answer):
                self.assertListEqual(x1['span'], x2['span'])
                self.assertEquals(x1['value'], x2['value'])

class TaskExtraction(BaseTest):
    def run_test(self):
        errors = []
        test_cases = self.get_testcases('/parsi_io/test/testcases/TaskExtraction.json')
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

import json
from parsi_io.modules.task_extractor import TaskExtractor
def run(task_extractor, text, change: bool = False):
    task = task_extractor.extract(text, change)
    return task
def test_run():
    # Load the test cases from the JSON file
    with open('test_cases.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    task_extractor = TaskExtractor()
    for test_case in test_cases:
        input_text = test_case['input']['text']
        input_bool = test_case['input'].get('bool', False)  # Default to False if not present
        expected_output = json.dumps(test_case['output'], ensure_ascii=False, indent=2)
        output = run(task_extractor, input_text, input_bool)
        assert output.strip() == expected_output.strip(), f"Expected {expected_output}, but got {output}"
test_run()