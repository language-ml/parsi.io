from parsi_io.modules.convert_number_to_text import ConvertNumberToText
from base import BaseTest

class TestConvertNumberToText(BaseTest):
    
    def run_test(self):

        test_cases = self.get_testcases('testcases/ConvertNumberToText.json')

        _object = ConvertNumberToText()

        test_counter = 0
        err_counter = 0
        errors = list()

        print('\n  [*] Testing ... ')

        for row in test_cases :

            output_res = _object.run(row['input'])

            if output_res != row['output'] :
                errors.append({ "input": row['input'], "output": row['output'] })
                err_counter += 1
            
            test_counter += 1
                
        success_number = int((test_counter - err_counter) * 100 / test_counter)
        print('\n  [*] success number: {n}% '.format(n=success_number))
        
        print('\n  [*] error number: {n}%   '.format(n=(100 - success_number)))

        if err_counter > 0 :
            print('\n  [!] errors:', errors)

        print('')


if __name__ == '__main__':
    TestConvertNumberToText().run_test()
