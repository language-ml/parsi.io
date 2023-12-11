import json
from parsi_io.modules.task_extractor.TaskRunner import TaskRunner
def run(task_extractor, text, change: bool = False):
    task = task_extractor.extract(text, change)
    return task
def test_run():
    # Load the test cases from the JSON file
    with open('test_cases.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    model = TaskRunner()
    for test_case in test_cases:
        input_text = test_case['input']['text']
        input_bool = test_case['input'].get('bool', False)  # Default to False if not present
        expected_output = json.dumps(test_case['output'], ensure_ascii=False, indent=2)
        output = model.run(input_text,input_bool)
        assert output.strip() == expected_output.strip(), f"Expected {expected_output}, but got {output}"
test_run()