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
        '.*(دلا?یل|عل[تل]|عامل|از دلایل|از عوامل|از علل|نتیجه|از نتایج|به خاطر|چرایی).*(است|هست|هستند|میباشد|می باشد|میباشند|می باشند|بود|بودند|باشد|باشند)',
        '(را نتیجه|رانتیجه).*(میدهند|میدهد|خواهند داد|خواهد داد|می دهد|می دهند|داد|داده|داده اند).*',
        '.*(منجر به|به دلا?یل|موجب|باعث|ناشی از|زیرا|چون|برآمده از|برامده از|منجربه).*',
        '.*(دلایل|علل|عوامل|نتایج).*(میتوان|می توان).*(اشاره کرد|برشمرد|بر شمرد).*',
        '.*(منجر به|سبب|منجربه).*(می شوند|میشوند|میشود|می شود|شد|شوند|شود).*',
        '.*(اگر|چنانچه|چنان چه|در صورت|درصورت).*',
        'به دلیل',
        'به دلایل' ,
        'دلیل',
        'به علت'
        'علت',
        'از\s*(این|آن)\s*(جهت|سو)\s*که',
        '(از|تا)\s*(ا|آ)ین\s*که',
        'به\s*(این|آن)\s*جهت',
        '[آا]ی?ن\s*گاه\s*که',
        'از\s*(این|آن)\s*رو',
        '[آا]ی?ن\s*جا\s*که',
        'از\s*[آا]ی?ن\s*رو',
        'چندان\s*[کچ]ه',
        'هم[ای]ن\s*که',
        'چنان\s*[کچ]ه',        
        'اکنون\s*که',
        'به\s*خاطر',
        'از\s*بهر',
        'چرا\s*که',
        'چرا(یی)?', 
        'در\s*اثر',
        'به\s*جهت',
        'از\s*بس',
        'از وقتی',
        'ع[و]امل',
        'ارتباط', 
        'متبوع',
        'واسطه',
        'معلول',
        'نتیجه',
        'مشروط',
        'نتایج',
        'رابطه',
        'مرتبط',
        'بلکه',
        'سبب' ,
        'باعث',        
        'موجب',        
        'زیرا',        
        'تابع',        
        'چون'        
            ]
        self.neg_patterns = [
            '.*(علت|معلول|سبب|دلیل|باعث|عامل|نتیجه)\s*(از|به|با|در|برای).*'
            ]    
        self.tagger = POSTagger(model = 'resources/postagger.model')    
        self.TFlag = 'بله'
        self.FFlag = 'خیر'

    def run(self, text):
        found = False
        found_pattern = None
        output_flag = self.FFlag
        output_marker = None
        output_marker_span = None

        for idx, pattern in enumerate(self.pos_patterns):          
            if re.search(pattern,  text):              
              if idx < 6:
                found = True
                output_flag = self.TFlag
                continue
              else:
                if(idx >5 and idx<11 and not found == True):
                  continue
                found = True
                output_flag = self.TFlag
                found_pattern = re.search(pattern, text).group()
                output_marker = found_pattern                
                for i in re.finditer(pattern, text):
                  output_marker_span = list(i.span()) 
                break

        for pattern in self.neg_patterns:
            if re.search(pattern,  text):
                found = False
                output_flag = self.FFlag
                found_pattern = re.search(pattern, text).group()
                output_marker = None
                output_marker_span = None
                break 

        tagged = self.tagger.tag(word_tokenize(text))
        for i in range(len(tagged)):
            if found_pattern is not None:
                if tagged[i][0] == found_pattern and tagged[i][1] == 'N':
                    found = False
                    output_flag = self.FFlag
            try:
                if tagged[i][1] == 'V' and tagged[i+1][0] == 'تا':
                    found = True
                    output_flag = self.TFlag
                    output_marker = 'تا'                
                    for i in re.finditer(output_marker, text):
                      output_marker_span = list(i.span())
                elif tagged[i+1][1] == 'V' and tagged[i][0] == 'تا':
                    found = True
                    output_flag = self.TFlag
                    output_marker = 'تا'
                    for i in re.finditer(output_marker, text):
                      output_marker_span = list(i.span())
            except:
                pass
        if output_marker_span:
          output_marker_span = ('[' + ', '.join([str(x) for x in output_marker_span]) + ']')        
        result_chain = [output_flag,output_marker,output_marker_span]             
        return result_chain

if __name__=='__main__':               
    model = CauseEffectExtraction()
    input_text = input()
    print(model.run(input_text))