
# Requirements:
## !pip install deplacy hazm
## !test -f resources-0.5.zip || curl -LO https://github.com/sobhe/hazm/releases/download/v0.5/resources-0.5.zip
## !test -d resources || ( mkdir -p resources && cd resources && unzip ../resources-0.5.zip )

import re
from collections import Counter
from __future__ import unicode_literals
import hazm
from hazm import *

class CauseEffectExtraction:
    def __init__(self):
        super().__init__()
        self.pos_patterns = [
            'چندان\s*[کچ]ه',
            'هم[ای]ن\s*که',
            'بلکه',
            '[آی]ن\s*که',
            'چنان\s*[کچ]ه',
            '(تا|از)\s*[اآ]ین\s*که',
            '[آا]ی?ن\s*جا\s*که',
            '[آا]ی?ن\s*گاه\s*که',
            'از\s*[آا]ی?ن\s*رو',
            'از\s*بس',
            'از وقتی',
            'از\s*بهر',
            'اکنون\s*که',
            'سبب' ,
            'باعث',
            'چرا(یی)?',
            'چرا\s*که',
            'متبوع',
            'موجب',
            'واسطه',
            'زیرا',
            'به\s*خاطر',
            'معلول',
            'نتیجه',
            'تابع',
            'مشروط',
            'در\s*اثر',
            'نتایج',
            'چون',
            'ع[و]امل',
            'رابطه',
            'مرتبط',
            'ارتباط',
            'از\s*(این|آن)\s*رو',
            'از\s*(این|آن)\s*(جهت|سو)\s*که',
            'به\s*(این|آن)\s*جهت',
            'به\s*جهت',
            '.*(منجر به|به دلا?یل|موجب|باعث|ناشی از|زیرا|چون|برآمده از|برامده از|منجربه).*',
            '.*(اگر|چنانچه|چنان چه|در صورت|درصورت).*',
            '(را نتیجه|رانتیجه).*(میدهند|میدهد|خواهند داد|خواهد داد|می دهد|می دهند|داد|داده|داده اند).*',
            '.*(دلایل|علل|عوامل|نتایج).*(میتوان|می توان).*(اشاره کرد|برشمرد|بر شمرد).*',
            '.*(منجر به|سبب|منجربه).*(می شوند|میشوند|میشود|می شود|شد|شوند|شود).*',
            '.*(دلا?یل|عل[تل]|عامل|از دلایل|از عوامل|از علل|نتیجه|از نتایج|به خاطر|چرایی).*(است|هست|هستند|میباشد|می باشد|میباشند|می باشند|بود|بودند|باشد|باشند)'
            ]
        self.neg_patterns = [
            '.*(علت|سبب|دلیل|باعث|عامل|نتیجه)\s*(از|به|با|در|برای).*'
            ]    
        self.tagger = POSTagger(model = 'resources/postagger.model')    
        self.TFlag = 'بله'
        self.FFlag = 'خیر'

    def run(self, text):
        found = False
        found_pattern = None

        for pattern in self.pos_patterns:
            if re.search(pattern,  text):
                found = True
                found_pattern = re.search(pattern, text).group()
                break

        for pattern in self.neg_patterns:
            if re.search(pattern,  text):
                found = False
                found_pattern = re.search(pattern, text).group()
                break 

        tagged = self.tagger.tag(word_tokenize(text))
        for i in range(len(tagged)):
            if found_pattern is not None:
                if tagged[i][0] == found_pattern and tagged[i][1] == 'N':
                    found = False
            try:
                if tagged[i][1] == 'V' and tagged[i+1][0] == 'تا':
                    found = True
                elif tagged[i+1][1] == 'V' and tagged[i][0] == 'تا':
                    found = True
            except:
                pass
        if found:
            return self.TFlag
        else:
            return self.FFlag

if __name__=='__main__':               
    model = CauseEffectExtraction()
    input_text = input()
    print(model.run(input_text))