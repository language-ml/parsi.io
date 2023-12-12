import json
from pathlib import Path

from parsi_io.modules.task_extractor.TaskRunner import TaskRunner
def test_run():
    with open(Path(__file__).parent / 'testcases/TaskExtraction.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    model = TaskRunner()
    for test_case in test_cases:
        input_text = test_case['input']['text']
        input_bool = test_case['input'].get('bool', False)  # Default to False if not present
        expected_output = json.dumps(test_case['output'], ensure_ascii=False, indent=2)
        output = model.run(input_text,input_bool)
        assert output.strip() == expected_output.strip(), f"Expected {expected_output}, but got {output}"
test_run()