#In the name of Allah

import re
import pickle
import pandas as pd
import time
import zipfile
import os
from tqdm import tqdm
#from tashaphyne.normalize import strip_tashkeel, strip_tatweel
from camel_tools.utils.normalize import normalize_alef_maksura_ar, normalize_teh_marbuta_ar, normalize_alef_ar, normalize_unicode
from camel_tools.utils.dediac import dediac_ar

import pathlib
quranic_directory = pathlib.Path(__file__).parent / "quranic_extractions"



class QuranicExtraction(object):
    def __init__(self, model = 'excact',
                 precompiled_patterns = 'prebuilt',
                 dont_consider = {"all_sw": False, "min_token_num": 0, "min_char_len_prop": 2},
                 parted = False,
                 num_of_output_in_apprx_model = 20):
        '''
        Model initialization

        "precompiled_patterns" can be 'prebuilt', 'build_and_use' or 'off'
        "model" can be 'exact' or 'apprx'
        '''
        self.model_type = model
        self.dont_consider = dont_consider
        with open(quranic_directory / "metadata\list.txt", 'r', encoding = "UTF-8") as f:
            self.stop_words = [self.normalize(word) for word in f.read().splitlines()]

        if self.model_type == 'exact':
            if precompiled_patterns != 'prebuilt':
                if precompiled_patterns == 'build_and_use':
                    self.initialize_from_scratch(create_compiled_patterns=True, save_compiled_patterns=True, parted = parted)
                    self.use_precompiled_patterns = True
                elif precompiled_patterns == 'off':
                    self.initialize_from_scratch(create_compiled_patterns=False, save_compiled_patterns=False, parted = parted)
                    self.use_precompiled_patterns = False
            else:
                "Load previously normalized quran"
                with open(quranic_directory / "pickles/quran_df.pickle", 'rb') as f:
                    self.quran_df = pickle.load(f)

                "Load previously normalized qbigram_bag"
                with open(quranic_directory / "pickles/qbigram_bag.pickle", 'rb') as f:
                    self.qbigram_bag = pickle.load(f)

                "Load previously compiled qbigram patterns"
                with open(quranic_directory / "pickles/qbigram_compiled.pickle", 'rb') as f:
                    self.qbigram_compiled = pickle.load(f)

                "Load previously compiled verses patterns"
                print("Loading verses_rules_compiled.pickle. This can take a while...")
                if not os.path.exists(quranic_directory / 'pickles/verses_rules_compiled.pickle'):
                    with zipfile.ZipFile(quranic_directory / 'pickles/verses_rules_compiled.zip', 'r') as zip_ref:
                        zip_ref.extractall(quranic_directory / 'pickles/')
                with open(quranic_directory / "pickles/verses_rules_compiled.pickle", 'rb') as f:
                    self.verses_rules_compiled = pickle.load(f)

                self.use_precompiled_patterns = True
        elif self.model_type == 'apprx':
            "Load and normalize quran"
            self.quran_df = pd.read_csv(quranic_directory / 'data/Quran.txt', sep="##|\t", names=['sore', 'aye', 'text'], engine='python')
            self.quran_df['text_norm'] = self.quran_df['text'].apply(lambda x: self.normalize(x))

            "Hyper Parameters"
            self.CHAR_DIFF_FACTOR = 1
            self.TUPLE_SIMILARITY_FACTOR = 4

            self.AYE_LEN_FACTOR = 0.1

            self.SAME_AYE_THRESHOLD = num_of_output_in_apprx_model
            self.SAME_AYE_RATIO = 1.3
            self.MIN_ACCEPT_SIMILARITY = 6

            self.ayes = self.quran_df.to_dict(orient='records')

            self.wordsMap = {}
            for i in range(len(self.ayes)):
                ayeWords = set()
                ayeWords.update(self.ayes[i]['text_norm'].split())
                for word in ayeWords:
                    if word not in self.wordsMap:
                        self.wordsMap[word] = {'tuples': self.get_tuples(word), 'ayes': set()}
                    self.wordsMap[word]['ayes'].add(i)

            stems = ['من', 'ان', 'ما', 'قول', 'فی', 'قال', 'لا', 'کان', 'الا', 'وما', 'ولا', 'یا', 'لم', 'عن', 'علیٰ',
                     'قد', 'اذا']
            for stem in stems:
                if stem in self.wordsMap:
                    self.wordsMap[stem]['ayes'] = set()
        self.AR_DIAC_CHARSET = list(u'\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640')

    "Normalization functions"

    def norm_chars(self, text):
        text = self.substitute_alphabets(text)
        text = self.camel_normal(text)
        text = self.special_norm(text)
        #text = strip_tashkeel(text)
        #text = strip_tatweel(text)
        return text

    def replace_extra_chars(self, text, rep_by = ' ', remove_extra_space = True):
        #text = re.sub(r"http\S+", "", text)
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # chinese char
                                   u"\U00002702-\U000027B0"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\U00010000-\U0010ffff"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u200d"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\ufe0f"  # dingbats
                                   u"\u3030"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(rep_by, text)

        empty_char = ' '
        items = [
                (r'ۚ|ۖ|ۗ|ۚ|ۙ|ۘ', empty_char),
                (r':|;|«|؛|!|؟|٪|۩|۞|↙|«|»|_|¬' + "|" + "ء", rep_by),
                ('\r|\f|\u200c', rep_by),
                (r'•|·|●|·|・|∙|｡|ⴰ', rep_by),
                (r',|٬|٫|‚|，|،|،', rep_by),
                (u"\ufdf0|\ufdf1|\u2022", rep_by),
                (r'( )+', r' ')
            ]
        if not remove_extra_space:
            del items[-1]
        for item in items:
            text = re.sub(item[0], item[1], text)

        replacing_words = '[!%#$,\.`~!\^&\*()-+={}\[\]|\\//:;\"\'\<,\>?؛۱۲۳۴۵۶۷۸۹۰1234567890«:؛»@]'
        text = text.translate(str.maketrans(replacing_words, len(replacing_words) * ' '))
        return text

    def camel_normal(self, text, remove_sokoon = True, normalize_hamzeAlef = True):
        text = normalize_alef_maksura_ar(text)
        #text = normalize_teh_marbuta_ar(text)

        if not normalize_hamzeAlef:
            _ALEF_NORMALIZE_AR_RE = re.compile(u'[\u0671\u0622]')
            text = _ALEF_NORMALIZE_AR_RE.sub(u'\u0627', text)
        else:
            text = normalize_alef_ar(text)

        if not remove_sokoon:
            AR_DIAC_CHARSET = frozenset(u'\u064b\u064c\u064d\u064e\u064f\u0650\u0651'
                                        u'\u0670\u0640')
            _DIAC_RE_AR = re.compile(u'[' +
                                     re.escape(u''.join(AR_DIAC_CHARSET)) +
                                     u']')
            text = _DIAC_RE_AR.sub(u'', text)
        else:
            text = dediac_ar(text)

        return text

    def substitute_alphabets(self, text):
        items = [
            (r"ٰا", r"ا"),
            (r"ئ|أ", r"ا"),
            #(r'ء', 'ئ'),
            (r"ﺐ|ﺏ|ﺑ", r"ب"),
            (r"ﭖ|ﭗ|ﭙ|ﺒ|ﭘ", r"پ"),
            (r"ﭡ|ٺ|ٹ|ﭞ|ٿ|ټ|ﺕ|ﺗ|ﺖ|ﺘ", r"ت"),
            (r"ﺙ|ﺛ", r"ث"),
            (r"ﺝ|ڃ|ﺠ|ﺟ", r"ج"),
            (r"ڃ|ﭽ|ﭼ", r"چ"),
            (r"ﺢ|ﺤ|څ|ځ|ﺣ", r"ح"),
            (r"ﺥ|ﺦ|ﺨ|ﺧ", r"خ"),
            (r"ڏ|ډ|ﺪ|ﺩ", r"د"),
            (r"ﺫ|ﺬ|ﻧ", r"ذ"),
            (r"ڙ|ڗ|ڒ|ڑ|ڕ|ﺭ|ﺮ", r"ر"),
            (r"ﺰ|ﺯ", r"ز"),
            (r"ﮊ", r"ژ"),
            (r"ݭ|ݜ|ﺱ|ﺲ|ښ|ﺴ|ﺳ", r"س"),
            (r"ﺵ|ﺶ|ﺸ|ﺷ", r"ش"),
            (r"ﺺ|ﺼ|ﺻ", r"ص"),
            (r"ﺽ|ﺾ|ﺿ|ﻀ", r"ض"),
            (r"ﻁ|ﻂ|ﻃ|ﻄ", r"ط"),
            (r"ﻆ|ﻇ|ﻈ", r"ظ"),
            (r"ڠ|ﻉ|ﻊ|ﻋ", r"ع"),
            (r"ﻎ|ۼ|ﻍ|ﻐ|ﻏ", r"غ"),
            (r"ﻒ|ﻑ|ﻔ|ﻓ", r"ف"),
            (r"ﻕ|ڤ|ﻖ|ﻗ", r"ق"),
            (r"ﮚ|ﮒ|ﮓ|ﮕ|ﮔ", r"گ"),
            (r"ﻝ|ﻞ|ﻠ|ڵ", r"ل"),
            (r"ﻡ|ﻤ|ﻢ|ﻣ", r"م"),
            (r"ڼ|ﻦ|ﻥ|ﻨ", r"ن"),
            (r"ވ|ﯙ|ۈ|ۋ|ﺆ|ۊ|ۇ|ۏ|ۅ|ۉ|ﻭ|ﻮ|ؤ", r"و"),
            (r"ﻬ|ھ|ﻩ|ﻫ|ﻪ|ۀ|ە|ہ", r"ه"),
            (r"ڭ|ﻚ|ﮎ|ﻜ|ﮏ|ګ|ﻛ|ﮑ|ﮐ|ڪ|ک", r"ك"),
            (r"ﭛ|ﻯ|ۍ|ﻰ|ﻱ|ﻲ|ں|ﻳ|ﻴ|ﯼ|ې|ﯽ|ﯾ|ﯿ|ێ|ے|ى|ی|یٰ", r"ي"),
        ]
        for item in items:
            text = re.sub(item[0], item[1], text)
        return text

    def special_norm(self, text):
        items = [
            (r"داود", r"داوود")
        ]
        for item in items:
            text = re.sub(item[0], item[1], text)
        return text

    def normalize(self, text, remove_sokoon = True, normalize_hamzeAlef = True):
        if not text or not isinstance(text, str):
            return ""
        #text = self.removeLink(text)
        #text = re.sub(r'[^\w\s]', '', str(text).strip())
        #text = strip_tashkeel(text)
        #text = strip_tatweel(text)
        text = self.replace_extra_chars(text)
        text = self.substitute_alphabets(text)
        text = self.camel_normal(text, remove_sokoon, normalize_hamzeAlef)
        text = self.special_norm(text)
        text = re.sub(r'( )+', r' ', text)
        return text.strip()

    def align_and_get_span(self, input, input_normd, output_bag):
        #input_rplcd = self.tokenizer(input, remove_extra_space=False, split=False)
        ""
        "input_rplcd has same char ind with input"
        input_rplcd = self.replace_extra_chars(input, remove_extra_space = False)
        input_rplcd = re.sub(F' [{"|".join(self.AR_DIAC_CHARSET)}]+ ', lambda x: ' '*(len(x.group())), input_rplcd)
        "input_rplcd_chNormd has different char ind with input BUT SAME toknization with input_rplcd"
        input_rplcd_chNormd = self.norm_chars(input_rplcd)
        
        input_rplcd_spltd = []
        input_rplcd_splt_index = []
        for m in re.finditer(r'\S+', input_rplcd):
            input_rplcd_spltd.append(m.group())
            input_rplcd_splt_index.append((m.start(), m.end()))
        input_rplcd_chNormd_spltd = []
        for m in re.finditer(r'\S+', input_rplcd_chNormd):
            input_rplcd_chNormd_spltd.append(m.group())
        input_normd_splt_start_index = []
        input_normd_splt_end_index = []
        for m in re.finditer(r'\S+', input_normd):
            input_normd_splt_start_index.append(m.start())
            input_normd_splt_end_index.append(m.end())

        "First solution"
        # output_bag = sorted(output_bag, key=lambda x: x['input_span'][1] - x['input_span'][0], reverse=True)
        # for out_ind, output in enumerate(output_bag):
        #     input_normd_span = output['input_span']
        #
        #     "A quranic piece of normalized input"
        #     input_normd_qp = input_normd[input_normd_span[0]:input_normd_span[1]]
        #
        #     input_normd_qp_spltd = input_normd_qp.split()
        #     for start_ind, inp_rplcd_chNormd_token in enumerate(input_rplcd_chNormd_spltd):
        #         if inp_rplcd_chNormd_token == input_normd_qp_spltd[0]:
        #             flag = True
        #             for c_ind, inp_nrmd_qp_tkn in enumerate(input_normd_qp_spltd):
        #                 if input_rplcd_chNormd_spltd[start_ind + c_ind] != inp_nrmd_qp_tkn:
        #                     flag = False
        #             if flag :
        #                 input_rplcd_chNormd_spltd[start_ind:start_ind + c_ind+1] = (c_ind+1) * "*"
        #                 intervals = input_rplcd_splt_index[start_ind:start_ind + c_ind+1]
        #                 output_bag[out_ind]['input_span'] = [intervals[0][0], intervals[-1][-1]]
        #                 output_bag[out_ind]['extracted'] = input[intervals[0][0]: intervals[-1][-1]]
        #                 break
        #     if not flag:
        #         raise Exception('Error in align_and_get_span')
        #
        # output_bag = sorted(output_bag, key=lambda x: x['input_span'][0])

        "Second solution"
        for out_ind, output in enumerate(output_bag):
            start_token = input_normd_splt_start_index.index(output['input_span'][0])
            end_token = input_normd_splt_end_index.index(output['input_span'][1])

            intervals = input_rplcd_splt_index[start_token:end_token+1]
            output_bag[out_ind]['input_span'] = [intervals[0][0], intervals[-1][-1]]
            output_bag[out_ind]['extracted'] = input[intervals[0][0]: intervals[-1][-1]]

        return output_bag


    "'Exact method' functions"

    def rule_maker(self, verse, qbigram_text, index):
        "Find the input bigrams in the text of the Quran"

        sentencelist = verse.split(" ")
        rule = "(?:"
        neet_to_handle_va = False
        for j in range(0, index):
            without_last_space = True if qbigram_text[:8] == F'(?:^| ){va}' else False
            left_regexd, neet_to_handle_va = self.regexitize_verse(" ".join(sentencelist[j:index]),
                                                              without_last_space=without_last_space)
            rule = rule + "(?:" + left_regexd + ")|"
        # before_bigram = F'(^|{va}|{va} | )' if neet_to_handle_va else ''
        # before_bigram = F'(?:(?:\\b{va} ?)|\\b)' if neet_to_handle_va else ''
        rule = rule + ")(?:" + (qbigram_text[2:] if neet_to_handle_va else qbigram_text) + ")("

        va_end_bigram = True if qbigram_text[-3:] == F'{va} ?' else False
        after_bigram = '' if va_end_bigram else ' '
        for j in range(len(sentencelist), index + 2, -1):
            right_regexd, _ = self.regexitize_verse(" ".join(sentencelist[index + 2:j]), va_before=va_end_bigram,
                                               without_last_space=True, without_last_va=True)
            rule = rule + '(?:' + after_bigram + right_regexd + ')|'
        rule = rule + ')'
        return rule

    def rule_maker_parted(self, verse, qbigram_text, index):
        "Find the input bigrams in the text of the Quran"

        sentencelist = verse.split(" ")
        rule_left = "(?:"
        without_last_space = True if qbigram_text[:8] == F'(?:^| ){va}' else False
        for j in range(0, index):
            left_regexd = self.regexitize_verse_parted(" ".join(sentencelist[j:index]), without_last_space=without_last_space)
            #before_bigram = F'(^|{va}|{va} | )' if neet_to_handle_va else ''
            #before_bigram = F'(?:\\b{va} ?)' if neet_to_handle_va else ''
            #rule_left = ")(?:" + before_bigram if neet_to_handle_va else rule_left
            #rule_left = "|(?:" + left_regexd + before_bigram + ")" + rule_left
            rule_left = rule_left + "(?:" + left_regexd + ")|"
        rule_left = None if index == 0 else rule_left[:-1] + ")$"


        rule_right = "^(?:"
        va_end_bigram = True if qbigram_text[-3:] == F'{va} ?' else False
        after_bigram = '' if va_end_bigram else ' '
        for j in range(len(sentencelist), index + 2, -1):
            right_regexd = self.regexitize_verse_parted(" ".join(sentencelist[index + 2:j]), va_before=va_end_bigram,
                                                        without_last_space=True, remove_last_va=True)
            rule_right = rule_right + '(?:' + after_bigram + right_regexd + ')|'
        rule_right = None if len(sentencelist) == index + 2 else rule_right[:-1] + ')'

        return rule_left, rule_right

    def regexitize_quran_df(self, quran_df):
        "Add regex patterns to quran verses"

        "Get regextized verbs that need 'alef?' pattern"
        verbs_needs_alef_patt = self.get_verbs_needs_alef_patt()

        oo_pattern = F"{verbs_needs_alef_patt}"
        # oo_repl = "\\1"+"ا"
        oo_repl = "\\1" + "ا" + "?"

        # hamze_pattern1 = "(ئ|أ|إ)"
        # # hamze_pattern = "(" + "(ء|ئ|أ)" + "\w+" + "|" + "\w+" + "(ء|ئ|أ)" + ")"
        # hamze_repl1 = "(?:" + "ا|ء|ئ" + ")"
        #
        # hamze_pattern2 = "([^|])" + "(ء)"
        # hamze_repl2 = "\\1(?:" + "|ا|ء|ئ" + ")"

        hamze_pattern = "(ء)"
        hamze_repl = "(?:" + "ء" + "|" + "ا" + ")?"

        alefAnySokoon_pattern = "(ف)" + "ا" + "(\w\u0652\S+)"
        alefAnySokoon_repl = "\\1" + "(?:" + "ا|" + ")" + "\\2"

        hamze_pattern = "(ة)"
        hamze_repl = "(?:" + "ة|ه|ت" + ")?"

        for index in quran_df.index:
            "alefAnySokoon"
            new_verse = re.sub(alefAnySokoon_pattern, alefAnySokoon_repl, quran_df.loc[index]['text_norm'])
            "(remove sokoon)"
            new_verse = dediac_ar(new_verse)
            "وا"
            new_verse = re.sub(oo_pattern, oo_repl, new_verse)
            "hamze"
            new_verse = re.sub(hamze_pattern, hamze_repl, new_verse)

            "set new_verse in quran_df"
            quran_df.loc.__setitem__((index, ('text_norm')), new_verse)



    def regexitize_qbigrambag(self, qbigram_bag):
        "Add regex patterns to quran bigrams"

        va_pattern1 = "(^" + "و" + " )"
        va_repl1 = "(?:^| )\\1?"
        va_pattern2 = "( " + "و" + "$)"
        va_repl2 = "\\1 ?"

        qbigram_bag_keys = list(qbigram_bag.keys())
        for key in qbigram_bag_keys:
            new_key = key
            word1, word2 = new_key.split(" ")
            if 'و' == word1:
                new_key.replace(" ", " \\b")
                new_key = new_key + "\\b"
                new_key = re.sub(va_pattern1, va_repl1, new_key)
            elif 'و' == word2:
                new_key.replace(" ", "\\b ")
                new_key = "\\b" + new_key
                new_key = re.sub(va_pattern2, va_repl2, new_key)
            else:
                new_key.replace(" ", "\\b \\b")
                new_key = "\\b" + new_key + "\\b"

            qbigram_bag[new_key] = qbigram_bag.pop(key)

    def regexitize_verse(self, verse, va_before=False, without_last_space=False, without_last_va=False):
        "Add regex patterns to list of quranic words"

        qlist = verse.split(" ")
        regexd_verse = ""
        for ind in range(len(qlist)):
            if 'و' == qlist[ind] and ind == 0 and len(qlist) > 1:
                regexd_verse += "\\b" + "و" + " ?"
                va_before = True
            elif 'و' == qlist[ind] and ind == len(qlist) - 1:
                # va_before = True
                # pass
                if not without_last_va:
                    #regexd_verse += "\\b" + "و" + " ?"
                    #va_before = True
                    regexd_verse += "\\b" + "و" + "\\b "
            elif 'و' == qlist[ind]:
                regexd_verse += "\\b" + "و" + " ?"
                va_before = True
            else:
                regexd_verse += ('\\b' if not va_before else '') + qlist[ind] + "\\b "
                va_before = False
        if without_last_space and not va_before:
            regexd_verse = regexd_verse[:-1]
        return regexd_verse, va_before

    def regexitize_verse_parted(self, verse, va_before=False, without_last_space=False, remove_last_va = False):
        "Add regex patterns to list of quranic words"

        qlist = verse.split(" ")
        regexd_verse = ""
        for ind in range(len(qlist)):
            if 'و' == qlist[ind]:
                if ind == len(qlist)-1 and remove_last_va:
                    continue
                else:
                    regexd_verse += "\\b" + "و" + " ?"
                    va_before = True
            else:
                regexd_verse += ('\\b' if not va_before else '') + qlist[ind] + "\\b "
                va_before = False
        if without_last_space and not va_before:
            regexd_verse = regexd_verse[:-1]
        return regexd_verse

    def get_verbs_needs_alef_patt(self):
        # verbs_needs_alef = ['ملاقو', 'تتلو', 'یتلو', 'یدعو', 'یعفو', 'واولو', 'اولو', 'امرو', 'ویعفو', 'تبو', 'اندعو',
        #                     'باسطو', 'تبلو', 'اشکو', 'ادعو', 'لتتلو', 'یمحو', 'ندعو', 'ساتلو', 'یرجو', 'وادعو', 'اتلو',
        #                     'نتلو', 'لتنو', 'ترجو', 'مهلکو', 'لیربو', 'یربو', 'لتارکو', 'لذایقو', 'صالو', 'ویرجو',
        #                     'کاشفو', 'لیبلو', 'ونبلو', 'ونبلو', 'مرسلو', 'تدعو', 'لصالو']

        verbs_needs_alef = ['ملاقو', 'تتلو', 'يتلو', 'يدعو', 'يعفو', 'واولو', 'اولو', 'امرو', 'ويعفو', 'تبو', 'اندعو',
                            'باسطو', 'تبلو', 'اشكو', 'ادعو', 'لتتلو', 'يمحو', 'ندعو', 'ساتلو', 'يرجو', 'وادعو', 'اتلو',
                            'نتلو', 'لتنو', 'ترجو', 'مهلكو', 'ليربو', 'يربو', 'لتاركو', 'لذايقو', 'صالو', 'ويرجو',
                            'كاشفو', 'ليبلو', 'ونبلو', 'ونبلو', 'مرسلو', 'تدعو', 'لصالو']
        verbs_needs_alef_patt = "("
        for el in verbs_needs_alef:
            verbs_needs_alef_patt += F"\\b{el}\\b|"
        verbs_needs_alef_patt = verbs_needs_alef_patt[:-1] + ")"
        return verbs_needs_alef_patt

    def create_regexitize_qbigrambag(self, quran_df, dont_consider):
        "Creating token bag"

        qbigram_bag = {}
        for ind in quran_df.index:
            temp = quran_df.loc[ind]['text_norm'].split(" ")
            for j in range(len(temp) - 1):
                if temp[j + 1] != 'و' and\
                   (not dont_consider['all_sw'] or (not(temp[j] in self.stop_words and temp[j+1] in self.stop_words))):
                    bigram = temp[j] + " " + temp[j + 1]
                    try:
                        qbigram_bag[bigram].append((ind, j))
                    except:
                        qbigram_bag[bigram] = [(ind, j)]

        "Add regex patterns to qbigram_bag"
        self.regexitize_qbigrambag(qbigram_bag)

        return qbigram_bag

    def initialize_from_scratch(self, create_compiled_patterns=False, save_compiled_patterns=False, parted = False):
        "Initialize regex patterns and data from scratch"

        global va
        va = "و"

        "Read quranic data"
        quran_df_index = pd.read_csv(quranic_directory / 'data/Quran.txt', names=['id', 'text'], sep="\t")['id']
        self.quran_df = pd.read_csv(quranic_directory / 'data/Quran.txt', sep="##|\t", names=['surah', 'verse', 'text'],
                               engine='python')
        self.quran_df.index = quran_df_index



        "Normalize quran"
        self.quran_df['text_norm'] = self.quran_df['text'].apply(lambda x: self.normalize(x, remove_sokoon = False))

        "Add regex patterns to quran_df: Sokoon will be removed in here"
        self.regexitize_quran_df(self.quran_df)


        if save_compiled_patterns:
            with open(quranic_directory / "pickles/quran_df.pickle", 'wb') as f:
                pickle.dump(self.quran_df, f)

        self.qbigram_bag = self.create_regexitize_qbigrambag(self.quran_df, self.dont_consider)
        if save_compiled_patterns:
            with open(quranic_directory / "pickles/qbigram_bag.pickle", 'wb') as f:
                pickle.dump(self.qbigram_bag, f)

        if create_compiled_patterns:
            "Create qbigrams_compiled"
            qbigram_bag_keys = list(self.qbigram_bag.keys())
            self.qbigram_compiled = []
            for qbigram in qbigram_bag_keys:
                self.qbigram_compiled.append(re.compile(qbigram))
        if save_compiled_patterns:
            with open(quranic_directory / "pickles/qbigram_compiled.pickle", 'wb') as f:
                pickle.dump(self.qbigram_compiled, f)

        "Create verses_rules_compiled"
        if create_compiled_patterns:
            qbigram_found_list = []
            for qc in self.qbigram_compiled:
                qbigram_found_list.append([qc.pattern, self.qbigram_bag[qc.pattern]])
            self.verses_rules_compiled = {}
            print("Compiling regex patterns for verses...")
            for qbigram in tqdm(qbigram_found_list):
                for inner_tup in qbigram[1]:
                    id, index = inner_tup
                    qbigram_text = qbigram[0]
                    verse = self.quran_df.loc[id]['text_norm']
                    if parted:
                        rule_left, rule_right = self.rule_maker_parted(verse, qbigram_text, index)
                        self.verses_rules_compiled[F'{id}-{index}-l'] = re.compile(rule_left) if rule_left else None
                        self.verses_rules_compiled[F'{id}-{index}-r'] = re.compile(rule_right) if rule_right else None
                    else:
                        rule = self.rule_maker(verse, qbigram_text, index)
                        self.verses_rules_compiled[F'{id}-{index}'] = re.compile(rule)
        if save_compiled_patterns:
            if parted:
                with open(quranic_directory / 'pickles/verses_rules_compiled_parted.pickle', 'wb') as f:
                    pickle.dump(self.verses_rules_compiled, f)
            else:
                with open(quranic_directory / 'pickles/verses_rules_compiled.pickle', 'wb') as f:
                    pickle.dump(self.verses_rules_compiled, f)

    def extract_verse_exact(self, input_normd, input, use_precompiled_patterns=True, target_verses = None):
        "re.find on all the quranic regexitized bigram and input bigram"
        mask_qbigrams = []
        if target_verses:
            for qb in self.qbigram_bag.keys():
                verses = [self.qbigram_bag[qb][i][0] for i in range(len(self.qbigram_bag[qb]))]
                mask_qbigrams.append(any([id in target_verses for id in verses]))
        else:
            mask_qbigrams = len(self.qbigram_bag.keys()) * [True]
        qbigram_found_list = []
        if use_precompiled_patterns:
            for ind, qc in enumerate(self.qbigram_compiled):
                if mask_qbigrams[ind] and qc.search(input_normd):
                    qbigram_found_list.append([qc.pattern, self.qbigram_bag[qc.pattern]])
        else:
            qbigram_bag_keys = list(self.qbigram_bag.keys())
            for ind, qbigram in enumerate(qbigram_bag_keys):
                if mask_qbigrams[ind] and re.search(qbigram, input_normd):
                    qbigram_found_list.append([qbigram, self.qbigram_bag[qbigram]])
        output_bag = []
        covered_input_index = []
        delete_new = False
        for qbigram in qbigram_found_list:
            for inner_tup in qbigram[1]:
                id, index = inner_tup
                if target_verses and id not in target_verses:
                    continue
                if use_precompiled_patterns:
                    matches = list(self.verses_rules_compiled[F'{id}-{index}'].finditer(input_normd))
                else:
                    qbigram_text = qbigram[0]
                    verse = self.quran_df.loc[id]['text_norm']
                    rule = self.rule_maker(verse, qbigram_text, index)
                    matches = list(re.finditer(rule, input_normd))
                if len(matches) != 0:
                    for match in matches:
                        res_str = input_normd[match.regs[0][0]:match.regs[0][1]]
                        "Do not consider the result if its number of tokens are less than self.dont_consider['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.dont_consider['min_token_num'] and \
                           len(res_str) < len(self.quran_df.loc[id]['text_norm'])/self.dont_consider['min_char_len_prop']:
                            continue
                        if (res_str[-1] == ' ') and (res_str[0] != ' '):
                            new_range = [match.regs[0][0], match.regs[0][1] - 1]
                        elif (res_str[-1] != ' ') and (res_str[0] == ' '):
                            new_range = [match.regs[0][0] + 1, match.regs[0][1]]
                        elif (res_str[-1] == ' ') and (res_str[0] == ' '):
                            new_range = [match.regs[0][0] + 1, match.regs[0][1] - 1]
                        else:
                            new_range = [match.regs[0][0], match.regs[0][1]]

                        case_ind = 0
                        while case_ind < len(covered_input_index) and len(covered_input_index) != 0:
                            case = covered_input_index[case_ind]
                            if (case[0] <= new_range[0] and new_range[1] < case[1]) or (
                                    case[0] < new_range[0] and new_range[1] <= case[1]):
                                delete_new = True
                                break
                            elif (new_range[0] <= case[0] and case[1] < new_range[1]) or (
                                    new_range[0] < case[0] and case[1] <= new_range[1]):
                                del covered_input_index[case_ind]
                                del output_bag[case_ind]
                            elif new_range[0] == case[0] and case[1] == new_range[1]:
                                if output_bag[case_ind]['quran_id'] == id:
                                    delete_new = True
                                    break
                                else:
                                    case_ind += 1
                            else:
                                case_ind += 1
                        if delete_new:
                            delete_new = False
                            continue

                        res = {'input_span':[new_range[0],new_range[1]],
                               'extracted': input_normd[new_range[0]:new_range[1]],
                               'quran_id':id,
                               'verse': self.quran_df.loc[id]['text']}
                        covered_input_index.append(new_range)
                        output_bag.append(res)

        output_bag = self.align_and_get_span(input, input_normd, output_bag)
        return output_bag

    def extract_verse_exact2(self, input_normd, input, use_precompiled_patterns=True):
        "re.find on all the quranic regexitized bigram and input bigram"

        output_bag = []
        covered_input_index = []
        delete_new = False
        if use_precompiled_patterns:
            for qc in self.qbigram_compiled:
                bigram_matches = list(qc.finditer(input_normd))
                for bigram_match in bigram_matches:
                    bspan = bigram_match.span()
                    for inner_tup in self.qbigram_bag[qc.pattern]:
                        id, vindex = inner_tup
                        match_left = self.verses_rules_compiled[F'{id}-{vindex}-l'].search(input_normd[:bspan[0]]) if self.verses_rules_compiled[F'{id}-{vindex}-l'] else None
                        match_right = self.verses_rules_compiled[F'{id}-{vindex}-r'].search(input_normd[bspan[1]:]) if self.verses_rules_compiled[F'{id}-{vindex}-r'] else None
                        if match_left:
                            span_left = match_left.span()[0]
                        else:
                            span_left = bspan[0]
                        if match_right:
                            span_right = bspan[1] + match_right.span()[1]
                        else:
                            span_right = bspan[1]

                        res_str = input_normd[span_left:span_right]

                        "Do not consider the result if its number of tokens are less than self.dont_consider['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.dont_consider['min_token_num'] and \
                                len(res_str) < len(self.quran_df.loc[id]['text_norm']) / self.dont_consider['min_char_len_prop']:
                            continue
                        if (res_str[-1] == ' ') and (res_str[0] != ' '):
                            new_range = [span_left, span_right - 1]
                        elif (res_str[-1] != ' ') and (res_str[0] == ' '):
                            new_range = [span_left + 1, span_right]
                        elif (res_str[-1] == ' ') and (res_str[0] == ' '):
                            new_range = [span_left + 1, span_right - 1]
                        else:
                            new_range = [span_left, span_right]

                        case_ind = 0
                        while case_ind < len(covered_input_index) and len(covered_input_index) != 0:
                            case = covered_input_index[case_ind]
                            if (case[0] <= new_range[0] and new_range[1] < case[1]) or (
                                    case[0] < new_range[0] and new_range[1] <= case[1]):
                                delete_new = True
                                break
                            elif (new_range[0] <= case[0] and case[1] < new_range[1]) or (
                                    new_range[0] < case[0] and case[1] <= new_range[1]):
                                del covered_input_index[case_ind]
                                del output_bag[case_ind]
                            elif new_range[0] == case[0] and case[1] == new_range[1]:
                                if output_bag[case_ind]['quran_id'] == id:
                                    delete_new = True
                                    break
                                else:
                                    case_ind += 1
                            else:
                                case_ind += 1
                        if delete_new:
                            delete_new = False
                            continue

                        res = {'input_span': [new_range[0], new_range[1]],
                               'extracted': input_normd[new_range[0]:new_range[1]],
                               'quran_id': id,
                               'verse': self.quran_df.loc[id]['text']}
                        covered_input_index.append(new_range)
                        output_bag.append(res)
        else:
            qbigram_bag_keys = list(self.qbigram_bag.keys())
            for qbigram in qbigram_bag_keys:
                bigram_matches = re.finditer(qbigram, input_normd)
                for bigram_match in bigram_matches:
                    bspan = bigram_match.span()
                    for inner_tup in self.qbigram_bag[qbigram]:
                        id, vindex = inner_tup
                        verse = self.quran_df.loc[id]['text_norm']
                        rule_left, rule_right = self.rule_maker_parted(verse, qbigram, vindex)
                        match_left = re.search(rule_left, input_normd[:bspan[0]]) if rule_left else None
                        match_right = re.search(rule_right, input_normd[bspan[1]:]) if rule_right else None
                        if match_left:
                            span_left = match_left.span()[0]
                        else:
                            span_left = bspan[0]
                        if match_right:
                            span_right = bspan[1] + match_right.span()[1]
                        else:
                            span_right = bspan[1]

                        res_str = input_normd[span_left:span_right]

                        "Do not consider the result if its number of tokens are less than self.dont_consider['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.dont_consider['min_token_num'] and \
                                len(res_str) < len(self.quran_df.loc[id]['text_norm']) / self.dont_consider['min_char_len_prop']:
                            continue
                        if (res_str[-1] == ' ') and (res_str[0] != ' '):
                            new_range = [span_left, span_right - 1]
                        elif (res_str[-1] != ' ') and (res_str[0] == ' '):
                            new_range = [span_left + 1, span_right]
                        elif (res_str[-1] == ' ') and (res_str[0] == ' '):
                            new_range = [span_left + 1, span_right - 1]
                        else:
                            new_range = [span_left, span_right]

                        case_ind = 0
                        while case_ind < len(covered_input_index) and len(covered_input_index) != 0:
                            case = covered_input_index[case_ind]
                            if (case[0] <= new_range[0] and new_range[1] < case[1]) or (
                                    case[0] < new_range[0] and new_range[1] <= case[1]):
                                delete_new = True
                                break
                            elif (new_range[0] <= case[0] and case[1] < new_range[1]) or (
                                    new_range[0] < case[0] and case[1] <= new_range[1]):
                                del covered_input_index[case_ind]
                                del output_bag[case_ind]
                            elif new_range[0] == case[0] and case[1] == new_range[1]:
                                if output_bag[case_ind]['quran_id'] == id:
                                    delete_new = True
                                    break
                                else:
                                    case_ind += 1
                            else:
                                case_ind += 1
                        if delete_new:
                            delete_new = False
                            continue

                        res = {'input_span': [new_range[0], new_range[1]],
                               'extracted': input_normd[new_range[0]:new_range[1]],
                               'quran_id': id,
                               'verse': self.quran_df.loc[id]['text']}
                        covered_input_index.append(new_range)
                        output_bag.append(res)

        output_bag = self.align_and_get_span(input, input_normd, output_bag)
        return output_bag


    "'Apprx. method' functions"

    def sort_words(self, w1, w2):
        if len(w1) > len(w2):
            temp = w1
            w1 = w2
            w2 = temp
        return (w1, w2)

    def char_count_diff(self, w1, w2):
        diffChar = 0
        chrs = set()
        chrs.update(list(w1))
        chrs.update(list(w2))
        for chr in chrs:
            diffChar += abs(w1.count(chr) - w2.count(chr))
            if w2.count(chr) == 0 or w1.count(chr) == 0:
                diffChar += 1

        return diffChar

    def get_tuples(self, word):
        if word in self.wordsMap:
            return self.wordsMap[word]['tuples']

        tuples = {}
        word_len = len(word)
        for i in range(word_len):
            for j in range(i + 1, word_len):
                tuple = word[i] + word[j]
                if tuple not in tuples:
                    tuples[tuple] = 0
                tuples[tuple] += 1
                if j == i + 1 and tuple == 'ال':
                    tuples[tuple] -= 0.5

        self.wordsMap[word] = {'tuples': tuples, 'ayes': set()}
        return tuples

    def same_tuple_count(self, w1, w2):
        len_w1 = len(w1)
        len_w2 = len(w2)
        sameTuple = 0

        w1_tuples = self.get_tuples(w1)
        w2_tuples = self.get_tuples(w2)

        for tuple in w1_tuples:
            if tuple in w2_tuples:
                sameTuple += w1_tuples[tuple] + w2_tuples[tuple]

        return sameTuple

    def words_similarity(self, w1, w2):
        (w1, w2) = self.sort_words(w1, w2)
        sameTupleCount = self.same_tuple_count(w1, w2)
        charDiff = self.char_count_diff(w1, w2)
        res = (self.TUPLE_SIMILARITY_FACTOR * sameTupleCount - self.CHAR_DIFF_FACTOR * charDiff) / (len(w1) + len(w2))

        if w1 == w2:
            return max(res, 3, len(w1))

        return res

    def check_aye_similarity(self, aye, senteces_words):
        aye_words = aye['text_norm'].split()
        result = 0

        len_aye_words = len(aye_words)
        len_senteces_words = len(senteces_words)

        for i in range(len_aye_words):
            for j in range(len_senteces_words):
                s = 0
                k = 0
                while i + k < len_aye_words and j + k < len_senteces_words:
                    sim = self.words_similarity(aye_words[i + k], senteces_words[j + k])
                    if sim < 0.1:
                        break
                    k += 1
                    s += sim
                if k > 0:
                    s += k * 1.5
                    if s > result:
                        result = s
        return result

    def extract_verse_apprx(self, sentence):
      ayat = set()
      result = {}
      normalizedWords = sentence.split(' ')
      for word in normalizedWords:
        if word not in self.wordsMap:
          continue
        for inx in self.wordsMap[word]['ayes']:
          if inx in result:
            continue
          result[inx] = self.check_aye_similarity(self.ayes[inx], normalizedWords)  - len(self.ayes[inx]['text_norm'].split()) * self.AYE_LEN_FACTOR
      sortedIndexes = sorted(result, key=result.get, reverse=True)[:self.SAME_AYE_THRESHOLD]
      if len(sortedIndexes)> 0:
        maxValue = result[sortedIndexes[0]]
        if len(sortedIndexes) > self.SAME_AYE_THRESHOLD and result[sortedIndexes[self.SAME_AYE_THRESHOLD]] * self.SAME_AYE_RATIO > maxValue:
          return
        for inx in sortedIndexes:
          if maxValue > result[inx] * self.SAME_AYE_RATIO or (len(normalizedWords) > 1 and result[inx] < self.MIN_ACCEPT_SIMILARITY):
            break
          ayat.add((self.ayes[inx]['text'], str(self.ayes[inx]['sore']) +"##"+ str(self.ayes[inx]['aye']), round(result[inx], 2)))
      ayat = [{'verse': res[0], 'quran_id': res[1], 'score': res[2]} for res in ayat]
      return ayat


    def run(self, text, target_verses = None):
        "Run the model"

        "Normalize input"
        input_normd = self.normalize(text)

        if self.model_type == 'exact':
            return self.extract_verse_exact(input_normd, text, self.use_precompiled_patterns, target_verses)
        elif self.model_type == 'apprx':
            return self.extract_verse_apprx(input_normd)

# if __name__ == '__main__':
#
#     dont_consider = {'all_sw': True, "min_token_num": 4, "min_char_len_prop": 2}
#     start = time.time()
#     model = QuranicExtraction(model = 'exact', precompiled_patterns='off', parted = False, dont_consider = dont_consider)
#     end = time.time()
#     print(F"Time is {end-start}")
#     #for sent in testCases:
#     while True:
#         input_text = input('Please enter your input text: ')
#         target_verses = input('Please enter target verses (enter nothing for no filter): ')
#         target_verses = target_verses.split(" ") if target_verses else None
#         #input('Input any character to process next test case.')
#         #input_text = sent
#         start = time.time()
#         result = model.run(input_text, target_verses = target_verses)
#         end = time.time()
#         if result:
#             print(F"Number of results: {len(result)}")
#             print(F"Time: {end - start}")
#             for x in result:
#                 print(x)
