from base import BaseTest
from parsi_io.modules.vehicle_movement_extractions import VehicleMovementExtraction


class TestVehicleMovementExtractor(BaseTest):    
    def run_test(self):
        errors = []
        test_cases = self.get_testcases('/parsi_io/test/testcases/VehicleMovementExtraction.json')
        obj = VehicleMovementExtraction()

        for i in test_cases:
            your_answer = obj.run(i['input'])[0]
            correct_answer = i['outputs'][0]
            d = {k: (your_answer[k], correct_answer[k]) for k in your_answer if k in correct_answer and your_answer[k] != correct_answer[k]}
            for j in d:
                errors.append('Input {0}: your answer is {1} correct answer is {2}'.format(i['id'], d[j][0], d[j][1]))
        assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))


if __name__ == '__main__':
    TestVehicleMovementExtractor().run_test()
