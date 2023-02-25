from dataclasses import replace
import re
from pathlib import Path

samples = """
میخورد
می رفت
میرفت
نمیرفت داشتندمیرفتند
میآجیدم داشتیممیخوردیم
داشتیمیخوردی آراسته است نمیرفتهاست
نرفتهاند آراستهاست
داشتهاست میآراستهاست داشتهاممیرفتهام
داشتهمیرفته نمیآراسته بوده ام
می آزرده بوده اند خواهمخورد
رفتهبودم نمیرفتهبودیم
داشتممیرفتهبودم
داشتم میرفته بودم
رفتهبودهام
میرفتهبودهام
داشتهایم می رفته بودهایم
نمیروبم میروبم نمی روبم
دارد نمی روبد
خواهیمرفت رفتهباشد
می رفته باشم نرفته بوده باشد
میرفته بوده باشد
"""

HALF_SPACE = '\u200c'
SPACE = ' '
SPACE_OR_HALF = f'[{HALF_SPACE}{SPACE}]*'
WORD_BOUNDARY = f"[{SPACE}\W{HALF_SPACE}]"    


class verbProcessing:
        
    
    def fixVerbs(self, text):

        all_verbs = Path.read_text(Path.cwd() / 'PVC/Data/TXT/all_verbs.txt', encoding="utf-8").split('\n')
        # text = self.remove_double_space(text)

        for item in all_verbs:
            
            if not item:
                continue

            verb, tag1, tag2, tag3 = item.split(',')

            # todo: fix آ کلاه دار
            contains = verb.replace(" ","") in text.replace(" ","").replace(HALF_SPACE,"")

            if not contains:
                continue

            # this will match all verbs even if there is no space between characters
            fixed_verb = verb.replace(" ", SPACE_OR_HALF)

            regex = f"{WORD_BOUNDARY}{fixed_verb}{WORD_BOUNDARY}"
            for item in re.finditer(regex, text):
                start, end = item.start(),item.end()
                result = text[start:end]

                if tag1 == 'PAST' and tag2 =='INDICATIVE':
                    # آزردم آزردی آزرد 
                    if tag3 == 'SIMPLE':
                        continue
                    # می آزردم
                    if tag3 == 'IMPERFECTIVE':
                        result=re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+)', r'\1'+HALF_SPACE+r'\2', text[start:end])

                    if tag3 == 'PROGRESSIVE':
                    # داشتم نمی رفتم
                        result=re.sub(f'(داشت)(یم|ید|ند|ی|م)?{SPACE_OR_HALF}(نمی|می){SPACE_OR_HALF}(\w+)', r'\1\2 \3'+HALF_SPACE+r'\4', text[start:end])
                
                    if tag3 == 'NARRATIVE':
                    # رفته ام
                        result = re.sub(f'(\w+){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)', r'\1'+HALF_SPACE+r'\2', text[start:end])

                    if tag3 == 'NARRATIVE_IMPERFECTIVE':
                    # نمی رفته ام
                        result = re.sub(f'(نمی|می)(\w+)(ایم|اید|اند|ام|ای|است)', r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3', text[start:end])
                        
                    if tag3 == 'NARRATIVE_PROGRESSIVE':
                    # داشته ام می رفته ام
                        result = re.sub(f'(داشته){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)?{SPACE_OR_HALF}(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)?',
                        r'\1'+HALF_SPACE+r'\2 \3'+HALF_SPACE+r'\4'+HALF_SPACE+r'\5', text[start:end])

                    if tag3 == 'PRECEDENT':
                        # رفته بودم
                        result = re.sub(f'(\w+){SPACE_OR_HALF}(بود)(ند|ید|یم|ی|م)?', r'\1'+HALF_SPACE+r'\2\3', text[start:end])

                    if tag3 == 'PRECEDENT_IMPERFECTIVE':    
                        # نمی رفته بودیم
                        result = re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+)(بود)(ند|ید|یم|ی|م)?', r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3\4', text[start:end])

                    if tag3 == 'PRECEDENT_PROGRESSIVE':
                        # داشتم می رفته بودم
                        result = re.sub(f'(داشت)(یم|ید|ند|ی|م)?{SPACE_OR_HALF}(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(بود)(ند|ید|یم|ی|م)?',
                        r'\1\2 \3'+HALF_SPACE+r'\4'+HALF_SPACE+r'\5\6', text[start:end])

                    if tag3 == 'PRECEDENT_NARRATIVE':
                        # رفته بوده ام
                        result = re.sub(f'(\w+){SPACE_OR_HALF}(بوده){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)',
                        r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3', text[start:end])
                    
                    if tag3 == 'PRECEDENT_NARRATIVE_IMPERFECTIVE':
                        # می رفته بوده ام
                        result = re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(بوده){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)',
                        r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3'+HALF_SPACE+r'\4', text[start:end])

                    if tag3 == 'PRECEDENT_NARRATIVE_PROGRESSIVE':
                        # داشته ایم می رفته بوده ایم
                        result = re.sub(f'(داشته){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)?{SPACE_OR_HALF}(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(بوده){SPACE_OR_HALF}(ایم|اید|اند|ام|ای|است)?',
                        r'\1'+HALF_SPACE+r'\2 \3'+HALF_SPACE+r'\4'+HALF_SPACE+r'\5'+HALF_SPACE+r'\6', text[start:end])

                if tag1 == 'PRESENT' and tag2 == 'INDICATIVE':
                    if tag3 =='SIMPLE':
                        continue
                    
                    if tag3 == 'IMPERFECTIVE':
                        # می روبم
                        result=re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+)', r'\1'+HALF_SPACE+r'\2', text[start:end])

                    if tag3 == 'PROGRESSIVE':
                        # دارد نمی روبد
                        result = re.sub(f'(دار)(یم|ید|ند|ی|م|د){SPACE_OR_HALF}(نمی|می){SPACE_OR_HALF}(\w+)',
                        r'\1\2 \3'+HALF_SPACE+r'\4', text[start:end])
                    
                if tag1 == 'FUTURE' and tag2 == 'INDICATIVE' and tag3 == 'SIMPLE':
                    # خواهم رفت
                    result = re.sub(f'(ن)?(خواه)(یم|ید|ند|ی|م|د){SPACE_OR_HALF}(\w+)', r'\1\2\3 \4', text[start:end])

                if tag1 == 'PRESENT' and (tag2 =='SUBJUNCTIVE' or tag2 =='IMPERATIVE') and tag3 == 'SIMPLE':
                    # نرویم
                    continue

                if tag1 == 'PAST' and (tag2 == 'SUBJUNCTIVE' or tag2 =='IMPERATIVE'):
                    if tag3 == 'NARRATIVE':
                        # رفته باشم
                        result = re.sub(f'(\w+){SPACE_OR_HALF}(باش)(یم|ید|ند|ی|م|د)', r'\1'+HALF_SPACE+r'\2\3', text[start:end])

                    if tag3 == 'NARRATIVE_IMPERFECTIVE':
                        # می رفته باشم
                        result = re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(باش)(یم|ید|ند|ی|م|د)',
                        r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3\4', text[start:end])

                    if tag3 == 'PRECEDENT_NARRATIVE':
                        # نرفته بوده باشد
                        result = re.sub(f'(\w+){SPACE_OR_HALF}(بوده){SPACE_OR_HALF}(باش)(یم|ید|ند|ی|م|د)',
                        r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3\4', text[start:end])

                    if tag3 == 'PRECEDENT_NARRATIVE_IMPERFECTIVE':
                        # می رفته بوده باشد
                        result = re.sub(f'(نمی|می){SPACE_OR_HALF}(\w+){SPACE_OR_HALF}(بوده){SPACE_OR_HALF}(باش)(یم|ید|ند|ی|م|د)',
                        r'\1'+HALF_SPACE+r'\2'+HALF_SPACE+r'\3'+HALF_SPACE+r'\4\5', text[start:end])
                  

                text = text[:start] + result + text[end:]

        return text
