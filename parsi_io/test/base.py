import json
import os
import unittest
from pathlib import Path


class BaseTest(unittest.TestCase):
    def get_testcases(self, addr):
        with open(Path(__file__).parent / addr, 'r', encoding="utf-8") as f:
            test_cases = json.load(f)
            return test_cases

    def run_test(self, obj, addr):
        errors = []
        test_cases = self.get_testcases(addr)
        for i in test_cases:
            your_answer = obj.run(i['input'])
            correct_answer = i['outputs']
            d = {k: (your_answer[k], correct_answer[k]) for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(i['id'], d[j][0], d[j][1]))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
