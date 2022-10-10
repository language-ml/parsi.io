# -*- coding: utf-8 -*-


from parsi_io.modules.SentenceType import SentenceClassifier
from base import BaseTest
import pandas as pd



class TestSentenceType(BaseTest):

    def test(self, dir_test='/testcases/SentenceType.json'):
        
        test_cases = self.get_testcases(dir_test)
        
        sent_detector = SentenceClassifier()
                
        tested_sents = 0
        err_counter = 0
        errors = []
        print('testing on test_dir ...')
        for row in test_cases:
            res = sent_detector.run(row['input'])
            res_type, res_verb = res['type'] , res['verb']
            true_type = row['outputs']['type']
            true_verb = row['outputs']['verb']
            if res_type != true_type or res_verb != true_verb:
                err_counter += 1
                errors.append([row['input'], [res_type , true_type] , [res_verb , true_verb]])
            tested_sents +=1
                
        print('error number: {err} from {true} sentences!'.format(err=err_counter,true=tested_sents))
        print('errors:',errors)