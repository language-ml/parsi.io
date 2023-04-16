# Importing required libraries
from itertools import product
import hazm
import re
import math
import os

directory = os.path.abspath(os.path.join(__file__, "../.."))


class work_flow:
    def __init__(self):

        # List of next step words
        step_words = ['بعد هم', 'در اواخر کار', 'در اواخر طبخ', 'در نهایت', 'ابتدا', 'سپس',
                      'بعد از ان', 'لازم است', 'و بعد', 'در اخر', 'بعد از اینکه', 'حالا', 'بعد',
                      'در اخر هم', 'بعدش', 'در پایان', 'نهایتا', 'در ابتدا', 'در گام نخست',
                      'و بعد هم', 'در اواخر', 'در مرحله بعد', 'بنابراین']

        custom_before = ['ولی ', 'اما ', 'و ', '']
        custom_next = [' ولی', '']

        # List of reverse step words
        reverse_step_words = ['قبل از ان', 'اما قبل از ان', 'پیش از ان', 'اما پیش از ان', 'در مرحله قبل',
                              'اما در مرحله قبل', 'ولی قبلش', 'قبلش']

        gam_list = ['گام', 'در گام', 'مرحله', 'در مرحله']

        self.gam_dict = {
            'اول': 1,
            'دوم': 2,
            'سوم': 3,
            'چهارم': 4,
            'پنجم': 5,
            'ششم': 6,
            'هفتم': 7,
            'هشتم': 8,
            'نهم': 9
        }

        goal_words = ['ارزو', 'ارزوی', 'دستور', 'برنامه',
                      'نیت', 'مقصود', 'هدف', 'به منظور', 'جهت', 'برای']

        # Initializing Hazm library
        self.tagger = hazm.POSTagger(model=os.path.join(
            directory, 'quantity_extractions', 'resources', 'hazm', 'postagger.model'))
        tmp = []
        for e1, e2, e3 in product(custom_before, step_words, custom_next):
            tmp.append(e1+e2+e3)
        step_words = tmp

        step_words.sort(key=len, reverse=True)

        tmp = []
        for i in step_words:
            tmp.append('\s*'+i.replace(' ', '\s*')+'\s*')
        step_words = tmp

        tmp = []
        for e1, e2, e3 in product(custom_before, reverse_step_words, custom_next):
            tmp.append(e1+e2+e3)
        reverse_step_words = tmp

        reverse_step_words.sort(key=len, reverse=True)

        tmp = []
        for i in reverse_step_words:
            tmp.append('\s*'+i.replace(' ', '\s*')+'\s*')
        reverse_step_words = tmp

        # List of pattern for removing
        remove_patterns = [r'<CONJ>تا</CONJ>[^<>]*<ADV>[^<>]*</ADV>[^<>]*<N>[^<>]*</N>[^<>]*<V>[^<>]*</V>',
                           r'<CONJ>تا</CONJ>[^<>]*<AJ>[^<>]*</AJ>[^<>]*<V>[^<>]*</V>']

        # Loading the list of Persian stopwords
        stop_words = ['$', '\.', '،']

        tmp = []
        for i in stop_words:
            tmp.append('\s*'+i.replace(' ', '\s*')+'\s*')
        stop_words = tmp

        tmp = []
        for e1, e2 in product(gam_list, self.gam_dict.keys()):
            tmp.append(e1+' '+e2)
        gam_list = tmp

        tmp = []
        for e1, e2, e3 in product(custom_before, gam_list, custom_next):
            tmp.append(e1+e2+e3)
        gam_list = tmp

        gam_list.sort(key=len, reverse=True)

        tmp = []
        for i in gam_list:
            tmp.append('\s*'+i.replace(' ', '\s*')+'\s*')
        gam_list = tmp

        goal_words.sort(key=len, reverse=True)

        # Add other lists to stopwords
        stop_words += step_words
        stop_words += reverse_step_words
        stop_words += gam_list

        stop_words.sort(key=len, reverse=True)

        # Make regex from lists
        remove_patterns_re = '|'.join(remove_patterns)
        self.stop_words_re = '|'.join(stop_words)
        self.step_words_re = '|'.join(step_words)
        self.reverse_step_words_re = '|'.join(reverse_step_words)
        self.gams_re = '|'.join(gam_list)
        self.goal_re = '|'.join(goal_words)

        # Compile regex
        self.remove_re = re.compile(remove_patterns_re)

        self.clean_word_list = stop_words[:]
        self.clean_word_list += ['\\s+', 'باید', 'هم']

        self.clean_word_list.sort(key=len, reverse=True)

    def _extract_goal(self, text):
        pattern = rf'({self.goal_re})(.+?)(?={self.stop_words_re})'
        match = re.search(pattern, text)
        if match:
            goal_phrase = match.group(2)
            # remove any instance of pronouns from the goal phrase
            pronouns = ['من', 'تو', 'او', 'ما', 'شما', 'انها', 'ایشان']
            for pronoun in pronouns:
                goal_phrase = re.sub(r'\b' + pronoun + r'\b',
                                     '', goal_phrase).strip()
            # remove the goal pattern and any preceding text from the text
            text = re.sub(pattern, '', text, 1)
            for i in self.tagger.tag(hazm.word_tokenize(goal_phrase)):
                if i[1] == 'V':
                    goal_phrase = goal_phrase.replace(i[0], '')
            return {"goal": goal_phrase}, text
        else:
            return {"goal": None}, text

    def _extract_steps(self, text):
        return list(re.finditer(rf'({self.step_words_re})(.+?)(?={self.stop_words_re})', text))

    def _extract_reverse_steps(self, text):
        return list(re.finditer(rf'({self.reverse_step_words_re})(.+?)(?={self.stop_words_re})', text))

    def _spec_time(self, text):
        return list(re.finditer(rf'({self.gams_re})(.+?)(?={self.stop_words_re})', text))

    def _reorder_sentences(self, text):
        all_step_sorted = {}

        steps = self._extract_steps(text)
        steps = [(i, 0) for i in steps]
        reverse_steps = self._extract_reverse_steps(text)
        reverse_steps = [(i, 1) for i in reverse_steps]
        spec_time_steps = self._spec_time(text)
        spec_time_steps = [(i, 2) for i in spec_time_steps]
        all_step_unordered = steps+reverse_steps+spec_time_steps

        for i in all_step_unordered:
            for j in all_step_unordered:
                if i[0].span()[0] <= j[0].span()[0] and i[0].span()[1] >= j[0].span()[1] and i != j:
                    all_step_unordered.remove(j)

        all_step_unordered.sort(key=lambda x: x[0].span()[0])

        for c, i in enumerate(all_step_unordered):
            if i[1] == 2:
                curent_text = i[0].group()
                tmp = [curent_text.find(j) if curent_text.find(
                    j) != -1 else math.inf for j in self.gam_dict.keys()]
                tmp2 = list(self.gam_dict.keys())
                all_step_sorted[self.gam_dict[tmp2[tmp.index(
                    min(tmp))]]] = curent_text
                all_step_unordered.remove(i)

        c = list(range(1, len(all_step_unordered)+1))
        for i in range(len(all_step_unordered)):
            if all_step_unordered[i][1] == 1:
                c[i] = c[i-1]-1
                for j in range(len(c)):
                    if i != j:
                        if c[j] <= c[i]:
                            c[j] -= 1
        dict_for_sort = {}

        for i, j in zip(list(range(1, len(all_step_unordered)+1)), sorted(c)):
            dict_for_sort[j] = i
        c = [dict_for_sort[i] for i in c]

        for i in sorted(all_step_sorted.keys()):
            for j in range(len(c)):
                if c[j] >= i:
                    c[j] += 1
        for counter, i in enumerate(c):
            all_step_sorted[i] = all_step_unordered[counter][0].group()

        return all_step_sorted

    def _preprocess(self, text):
        text = text.replace('آ', 'ا')
        return text

    def _clean(self, text):
        tmp = '|'.join(self.clean_word_list)
        text = re.sub(rf'^({tmp}|\s+)+', '', text)
        text = re.sub(rf'({tmp}|\s+)+$', '', text)
        return text

    def run(self, text):
        text = self._preprocess(text)
        text = self.tagger.tag(hazm.word_tokenize(text))
        text = ' '.join(["<"+t+">"+w+"</"+t+">" for w, t in text])
        for i in self.remove_re.findall(text):
            text = text.replace(i, '')
        text = re.sub('<[^>]*>', '', text)
        text = self._extract_goal(text)

        out = {}

        out['goal'] = text[0]['goal']
        tmp = self._reorder_sentences(text[1])
        for i in tmp:
            tmp[i] = self._clean(tmp[i])
        for i in sorted(tmp):
            out[str(i)] = tmp[i]
        return out
