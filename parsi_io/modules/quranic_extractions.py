#In the name of Allah

import re
import json
import pickle
import pandas as pd
import time
import zipfile
import os
import numpy as np
from typing import Union
from tqdm import tqdm
#from tashaphyne.normalize import strip_tashkeel, strip_tatweel
from camel_tools.utils.normalize import normalize_alef_maksura_ar, normalize_teh_marbuta_ar, normalize_alef_ar, normalize_unicode
from camel_tools.utils.dediac import dediac_ar
from quranic_extraction.packages.tahzib import HadithTahzib
from itertools import groupby
from transformers import AutoModelForTokenClassification, AutoTokenizer


import pathlib
quranic_directory = pathlib.Path(__file__).parent / "quranic_extraction"



class QuranicExtraction(object):
    def __init__(self, model = 'excact',
                 precompiled_patterns = 'prebuilt',
                 filters = {"all_sw": False,
                                  "min_token_num": 0,
                                  "min_char_len_prop": 100,
                                  "idf_threshold": 0,
                                  "custom_bert_token_threshold": None,
                                  "consecutive_verses_priority": False,
                                  "use_camelbert": False},
                 parted = False,
                 camelbert_checkpoint = None,
                 single_words = [],
                 num_of_output_in_apprx_model = 20):
        '''
        Model initialization

        "precompiled_patterns" can be 'prebuilt', 'build_and_use' or 'off'
        "model" can be 'exact' or 'apprx'
        "consecutive_verses_priority": If two results x and y with different spans have the same surah number,
                                            whether to remove the other results with the y span or not.
        '''
        self.model_type = model
        self.filters = filters
        self.camelbert_checkpoint = camelbert_checkpoint
        self.AR_DIAC_CHARSET = list(u'\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670\u0640')
        with open(quranic_directory / "metadata/list.txt", 'r', encoding = "UTF-8") as f:
            self.stop_words = [self.normalize(word) for word in f.read().splitlines()]
        if self.model_type == 'exact':
            self.hadith_tahzib = HadithTahzib()
            self.puncs_regex = re.compile('([' + r'\-\.:!،<>؛؟»\]\)\}«\[\(\{\\\?,;()1234567890۰۱۲۳۴۵۶۷۸۹' + '])')
            self.alone_AR_DIAC_CHARSET = re.compile(F' [{"|".join(self.AR_DIAC_CHARSET)}]+ ')
            self.single_words = single_words
            if self.filters["idf_threshold"] != 0:
                # with open(quranic_directory / "pickles/idf_dict.pkl", 'rb') as f:
                #     self.idf_dict = pickle.load(f)
                with open(quranic_directory / "metadata/idf_dict.json", 'r') as f:
                    self.idf_dict = json.load(f)
            if self.camelbert_checkpoint:
                self.model = AutoModelForTokenClassification.from_pretrained(self.camelbert_checkpoint)
                self.tokenizer = AutoTokenizer.from_pretrained(self.camelbert_checkpoint)
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


    "Normalization functions"

    def norm_chars(self, text):
        text = self.substitute_alphabets(text)
        text = self.camel_normal(text)
        text = self.special_norm(text)
        #text = strip_tashkeel(text)
        #text = strip_tatweel(text)
        return text

    def replace_extra_chars(self, text, rep_by = ' ',
                            remove_extra_space = True,
                            replace_hamza_by_empty = True):
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


        # items = [
        #         (r'ۚ|ۖ|ۗ|ۚ|ۙ|ۘ', empty_char),
        #         (r':|;|«|؛|!|؟|٪|۩|۞|↙|«|»|_|¬' + "|" + "ء", rep_by),
        #         ('\r|\f|\u200c', rep_by),
        #         (r'•|·|●|·|・|∙|｡|ⴰ', rep_by),
        #         (r',|٬|٫|‚|，|،|،', rep_by),
        #         (u"\ufdf0|\ufdf1|\u2022", rep_by),
        #         (r'[A-Za-z]', rep_by),
        #         (r'( )+', r' '),
        #     ]
        empty_char = '' if replace_hamza_by_empty else 'ء'
        items = [
                (r'ۚ|ۖ|ۗ|ۚ|ۙ|ۘ', rep_by),
                (r':|;|«|؛|!|؟|٪|۩|۞|↙|«|»|_|¬', rep_by),
                #(r'ء', " ?"),
                (r'ء', empty_char),
                ('\r|\f|\u200c', rep_by),
                (r'•|·|●|·|・|∙|｡|ⴰ', rep_by),
                (r',|٬|٫|‚|，|،|،', rep_by),
                (u"\ufdf0|\ufdf1|\u2022", rep_by),
                (r'[A-Za-z]', rep_by),
                (r'( )+', r' '),
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
        #input_rplcd = self.tokenizer(input, remove_extra_space=False, split=False
        "These two are just replace extra chars with space, so input_rplcd has same char ind with input and"
        "same tokenization (with \S+) with input_normd"
        input_rplcd = self.replace_extra_chars(input, remove_extra_space = False, replace_hamza_by_empty = False)
        input_rplcd = re.sub(F' [{"|".join(self.AR_DIAC_CHARSET)}]+ ', lambda x: ' '*(len(x.group())), input_rplcd)
        #"input_rplcd_chNormd has different char ind with input BUT SAME tokenization with input_rplcd"
        #input_rplcd_chNormd = self.norm_chars(input_rplcd)
        
        #input_rplcd_spltd = []
        input_rplcd_splt_index = []
        for m in re.finditer(r'\S+', input_rplcd):
            #input_rplcd_spltd.append(m.group())
            input_rplcd_splt_index.append((m.start(), m.end()))
        # input_rplcd_chNormd_spltd = []
        # for m in re.finditer(r'\S+', input_rplcd_chNormd):
        #     input_rplcd_chNormd_spltd.append(m.group())
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
            if output['input_span'][0] in input_normd_splt_start_index:
                start_token = input_normd_splt_start_index.index(output['input_span'][0])
            else:
                start_token = self.get_smallest_element_ind_larger_than(input_normd_splt_start_index,
                                                                        output['input_span'][0])

            if output['input_span'][1] in input_normd_splt_end_index:
                end_token = input_normd_splt_end_index.index(output['input_span'][1])
            else:
                end_token = self.get_largest_element_ind_smaller_than(input_normd_splt_end_index,
                                                                      output['input_span'][1])

            intervals = input_rplcd_splt_index[start_token:end_token+1]
            output_bag[out_ind]['input_span'] = [intervals[0][0], intervals[-1][-1]]
            output_bag[out_ind]['extracted'] = input[intervals[0][0]: intervals[-1][-1]]

        return output_bag

    def normalize_for_camelbert(self, text):
        text = self.hadith_tahzib.normalize_alpha(text, dediac=True) #Replace chars and remove diacritics(not removing)
        text = self.hadith_tahzib.remove_all_tags(text) # Remove tags
        text = self.puncs_regex.sub(r' \1 ', text)
        return self.hadith_tahzib.remove_extra_space(text).strip()

    def align_and_get_span_for_camelbert(self, input, input_normd, output_bag, return_token_span = False):
        ""

        "These two are just replace extra chars with space, so input_rplcd has same char ind with input and"
        "same tokenization (with \S+) with input_normd"
        # input_rplcd = self.replace_extra_chars(input, remove_extra_space=False)
        # input_rplcd = re.sub(F' [{"|".join(self.AR_DIAC_CHARSET)}]+ ', lambda x: ' ' * (len(x.group())), input_rplcd)
        # input_normd_rplcd = self.replace_extra_chars(input_normd, remove_extra_space=False)
        # input_normd_rplcd = re.sub(F' [{"|".join(self.AR_DIAC_CHARSET)}]+ ',
        #                            lambda x: ' ' * (len(x.group())),
        #                            input_normd_rplcd)

        def replace_chars(text):
            text = self.hadith_tahzib.regex_all_tags.sub(lambda x: ' ' * (len(x.group())), text)
            text = self.puncs_regex.sub(r' ', text)
            text = self.alone_AR_DIAC_CHARSET.sub(lambda x: ' ' * (len(x.group())), text)
            return text

        input_rplcd = replace_chars(input)
        input_normd_rplcd = replace_chars(input_normd)

        input_rplcd_splt_index = []
        for m in re.finditer(r'\S+', input_rplcd):
            input_rplcd_splt_index.append((m.start(), m.end()))

        input_normd_rplcd_splt_start_index = []
        input_normd_rplcd_splt_end_index = []
        for m in re.finditer(r'\S+', input_normd_rplcd):
            input_normd_rplcd_splt_start_index.append(m.start())
            input_normd_rplcd_splt_end_index.append(m.end())

        input_splt_start_index = []
        input_splt_end_index = []
        for m in re.finditer(r'\S+', input):
            input_splt_start_index.append(m.start())
            input_splt_end_index.append(m.end())

        "Second solution"
        remove_inds = [] #remove results that are just contain puncs
        for out_ind, output in enumerate(output_bag):
            if output['input_span'][0] in input_normd_rplcd_splt_start_index:
                start_token = input_normd_rplcd_splt_start_index.index(output['input_span'][0])
            else:
                start_token = self.get_smallest_element_ind_larger_than(input_normd_rplcd_splt_start_index,
                                                                        output['input_span'][0])

            if output['input_span'][1] in input_normd_rplcd_splt_end_index:
                end_token = input_normd_rplcd_splt_end_index.index(output['input_span'][1])
            else:
                end_token = self.get_largest_element_ind_smaller_than(input_normd_rplcd_splt_end_index,
                                                                      output['input_span'][1])

            if start_token!=None and end_token!=None:
                intervals = input_rplcd_splt_index[start_token:end_token + 1]
                if intervals:
                    output_bag[out_ind]['input_span'] = [intervals[0][0], intervals[-1][-1]]
                    output_bag[out_ind]['extracted'] = input[intervals[0][0]: intervals[-1][-1]]
                    if return_token_span:
                        if output['input_span'][0] in input_splt_start_index:
                            start_token_in_input = input_splt_start_index.index(output['input_span'][0])
                        else:
                            start_token_in_input = self.get_largest_element_ind_smaller_than(input_splt_start_index,
                                                                                             output['input_span'][0])

                        if output['input_span'][1] in input_splt_end_index:
                            end_token_in_input = input_splt_end_index.index(output['input_span'][1])
                        else:
                            end_token_in_input = self.get_smallest_element_ind_larger_than(input_splt_end_index,
                                                                                           output['input_span'][1])
                        output_bag[out_ind]['input_token_span'] = [start_token_in_input, end_token_in_input + 1]
                else:
                    remove_inds.append(out_ind)
            else:
                remove_inds.append(out_ind)

        for rm_ind in sorted(remove_inds, reverse = True):
            del output_bag[rm_ind]

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

        # hamze_pattern = "(ء)"
        # hamze_repl = "(?:" + "ء" + "|" + "ا" + ")?"
        # -----> Hamze is removed in replace_extra_chars function

        alefAnySokoon_pattern = "(ف)" + "ا" + "(\w\u0652\S+)"
        alefAnySokoon_repl = "\\1" + "(?:" + "ا|" + ")" + "\\2"

        t_pattern = "(ة)"
        t_repl = "(?:" + "ة|ه|ت" + ")?"

        ayoha_pattern = "(ايها)"
        ayoha_repl = "\\1" + "?"
        for index in quran_df.index:
            "alefAnySokoon"
            new_verse = re.sub(alefAnySokoon_pattern, alefAnySokoon_repl, quran_df.loc[index]['text_norm'])
            "(remove sokoon)"
            new_verse = dediac_ar(new_verse)
            "وا"
            new_verse = re.sub(oo_pattern, oo_repl, new_verse)
            "ة"
            new_verse = re.sub(t_pattern, t_repl, new_verse)
            "ایها"
            new_verse = re.sub(ayoha_pattern, ayoha_repl, new_verse)
            "set new_verse in quran_df"
            quran_df.loc.__setitem__((index, ('text_norm')), new_verse)

    def special_regexitize_quran_df(self, quran_df):
        #quran_df.at["68##6", 'text_norm'] = "بايي?كم المفتون"
        quran_df.loc.__setitem__(("68##6", ('text_norm')), "بايي?كم المفتون")
        quran_df['text_norm'] = quran_df['text_norm'].replace("وو", "وو?", regex=True)
        quran_df['text_norm'] = quran_df['text_norm'].replace("يي", "يي?", regex=True)
        quran_df['text_norm'] = quran_df['text_norm'].replace("اا", "اا?", regex=True)

    def regexitize_qbigrambag(self, qbigram_bag):
        "Add regex patterns to quran bigrams"

        va_pattern1 = "(^" + "و" + " )"
        va_repl1 = "(?:^| )\\1?"
        va_pattern2 = "( " + "و" + "$)"
        va_repl2 = "\\1 ?"

        qbigram_bag_keys = list(qbigram_bag.keys())
        for key in qbigram_bag_keys:
            new_key = key
            #if " " in new_key:
            word1, word2 = new_key.split(" ")
            # else:
            #     word1, word2 = new_key, None
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

    def create_regexitize_qbigrambag(self, quran_df, filters, single_words):
        "Creating token bag"

        qbigram_bag = {}
        for ind in quran_df.index:
            temp = quran_df.loc[ind]['text_norm'].split(" ")
            for j in range(len(temp) - 1):
                if temp[j + 1] != 'و' and\
                   (not filters['all_sw'] or (not(temp[j] in self.stop_words and temp[j+1] in self.stop_words))):
                    bigram = temp[j] + " " + temp[j + 1]
                    try:
                        qbigram_bag[bigram].append((ind, j))
                    except:
                        qbigram_bag[bigram] = [(ind, j)]
                # elif temp[j + 1] in single_words:
                #     try:
                #         qbigram_bag[temp[j + 1]].append((ind, j))
                #     except:
                #         qbigram_bag[temp[j + 1]] = [(ind, j)]

        # for key, values in single_words.items():
        #     for val in values:
        #         try:
        #             qbigram_bag[val].append((ind, j))
        #         except:
        #             qbigram_bag[val] = [(ind, j)]
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

        self.special_regexitize_quran_df(self.quran_df)

        if save_compiled_patterns:
            with open(quranic_directory / "pickles/quran_df.pickle", 'wb') as f:
                pickle.dump(self.quran_df, f)

        self.qbigram_bag = self.create_regexitize_qbigrambag(self.quran_df, self.filters, self.single_words)
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

    def filter_res(self, res):
        remove_ind = []
        if self.filters['idf_threshold'] != 0:
            for ind in range(len(res)):
                extracted = res[ind]['extracted']
                extracted_normd = self.hadith_tahzib.heavy_normalize(extracted)
                extracted_normd_splt = extracted_normd.split()
                if sum([self.idf_dict[w] for w in extracted_normd_splt])/len(extracted_normd_splt) < self.filters['idf_threshold']:
                    remove_ind.append(ind)
        if self.filters['consecutive_verses_priority']:
            sorted_res = sorted([(ind, x) for ind, x in enumerate(res)], key=lambda x:x[1]['input_span'][0])
            sorted_res_grouped = [(k, list(v))
                                  for k, v in groupby(sorted_res, key=lambda x:x[1]['input_span'])]
            consecutive_verses = [[] for _ in range(len(sorted_res_grouped))]
            for from_gp_ind, (_, from_gp) in enumerate(sorted_res_grouped):
                for from_el in from_gp:
                    if from_el not in consecutive_verses[from_gp_ind]:
                        from_sura_num = from_el[1]['quran_id'].split('##')[0]
                        for to_gp_ind, (_, to_gp) in enumerate(sorted_res_grouped[from_gp_ind+1:], start=from_gp_ind+1):
                            for to_el in to_gp:
                                if from_sura_num == to_el[1]['quran_id'].split('##')[0]:
                                    if from_el not in consecutive_verses[from_gp_ind]:
                                        consecutive_verses[from_gp_ind].append(from_el)
                                    if to_el not in consecutive_verses[to_gp_ind]:
                                        consecutive_verses[to_gp_ind].append(to_el)
            for gp_ind in range(len(consecutive_verses)):
                if consecutive_verses[gp_ind] == []:
                    consecutive_verses[gp_ind].extend(sorted_res_grouped[gp_ind][1])
            remove_ind = set(remove_ind).union(
                set(range(len(res))).difference(set([el[0] for l in consecutive_verses for el in l]))
            )

        for i in sorted(remove_ind, reverse=True):
            del res[i]
        return res

    def break_to_subsequent_spans(self, l: list):
        segmented_list = [[l[0][0]]]
        # breakpoint()
        span_len = 1
        for x, label in l[1:]:
            if (x - span_len != segmented_list[-1][-1]) or (label == 1):
                segmented_list[-1].append(segmented_list[-1][-1] + span_len)
                segmented_list.append([x])
                span_len = 1
            else:
                span_len += 1
        segmented_list[-1].append(segmented_list[-1][-1] + span_len)
        return segmented_list

    def word_ind_to_char_ind(self, word_span: Union[list, tuple], input_list: list):
        extra = 1 if word_span[0] != 0 else 0
        start_ind = len(' '.join(input_list[:word_span[0]])) + extra # +1 for one space
        end_ind = len(' '.join(input_list[:word_span[1]]))
        return (start_ind, end_ind)

    def get_smallest_element_ind_larger_than(self, l, i):
        "l should be sorted in ascending order"
        for ind, el in enumerate(l):
            if el > i:
                return ind
        return None

    def get_largest_element_ind_smaller_than(self, l, i):
        "l should be sorted in ascending order"
        for ind, el in enumerate(l):
            if el > i:
                return ind - 1
        return len(l) - 1

    def get_camelbert_quranic_labels(self, input_text, return_token_span = True, custom_threshold = None):
        input_text_normd = self.normalize_for_camelbert(input_text)
        input_list_normd = input_text_normd.split(" ")
        tokenized_input = self.tokenizer(input_list_normd, truncation=True, is_split_into_words=True,
                                         max_length=512, return_tensors="pt")
        word_ids = tokenized_input.word_ids()
        output_logits = self.model(**tokenized_input)['logits'].detach()[0]
        tokens_label = []
        if custom_threshold:
            for row in output_logits:
                rs = np.argsort(row).tolist()
                if row[rs[-1]] - row[rs[-2]] < custom_threshold and rs[-1] == 0:
                    tokens_label.append(rs[-2])
                else:
                    tokens_label.append(rs[-1])
        else:
            tokens_label = np.argmax(output_logits, axis=1).tolist()
        tokens_label = list(tokens_label)
        predicted_quranic_words_idx = [(word_ids[idx], label) for idx, label in enumerate(tokens_label)
                                       if label != 0 and word_ids[idx] != None]
        unique_indexes = []
        for el in predicted_quranic_words_idx:
            if el not in unique_indexes:
                unique_indexes.append(el)
        predicted_quranic_words_idx = unique_indexes
        if len(predicted_quranic_words_idx) == 0:
            predicted_quranic_words_idx_segmented = []
        else:
            predicted_quranic_words_idx_segmented = self.break_to_subsequent_spans(predicted_quranic_words_idx)
        predicted_quranic_char_span = []
        for span in predicted_quranic_words_idx_segmented:
            predicted_quranic_char_span.append(self.word_ind_to_char_ind(span, input_list_normd))
        output = []
        for seg_ind in predicted_quranic_char_span:
            output.append({"input_span": (seg_ind[0], seg_ind[1])})

        output = self.align_and_get_span_for_camelbert(input_text, input_text_normd, output, return_token_span = True)

        return output

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
                        "Do not consider the result if its number of tokens are less than self.filters['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.filters['min_token_num'] and \
                           len(res_str) < len(self.quran_df.loc[id]['text_norm'])/self.filters['min_char_len_prop']:
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
        output_bag = self.filter_res(output_bag)
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

                        "Do not consider the result if its number of tokens are less than self.filters['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.filters['min_token_num'] and \
                                len(res_str) < len(self.quran_df.loc[id]['text_norm']) / self.filters['min_char_len_prop']:
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

                        "Do not consider the result if its number of tokens are less than self.filters['min_token_num']" \
                        "and its length (character length) is smaller than half of its verse length"
                        if len(res_str.split()) < self.filters['min_token_num'] and \
                                len(res_str) < len(self.quran_df.loc[id]['text_norm']) / self.filters['min_char_len_prop']:
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

        def get_result_pack(output, start_index_token, cover_cb_res_len, input_list):
            #output_token_len = output['input_token_span'][1] - output['input_token_span'][0]

            # input_seg = output['extracted']

            res_start_token_with_cover = start_index_token + output['input_token_span'][0] - cover_cb_res_len
            res_start_token_with_cover = res_start_token_with_cover if res_start_token_with_cover >= 0 else 0
            res_end_token_with_cover = start_index_token + output['input_token_span'][1] + cover_cb_res_len
            res_end_token_with_cover = res_end_token_with_cover \
                if res_end_token_with_cover <= len(input_list) else len(input_list)

            input_seg = ' '.join(input_list[res_start_token_with_cover:res_end_token_with_cover])

            input_seg_start_index = len(' '.join(input_list[:res_start_token_with_cover]))
            input_seg_start_index = input_seg_start_index + 1 if res_start_token_with_cover != 0 \
                                                              else input_seg_start_index # +1 for space

            input_normd_seg = self.normalize(input_seg)
            ress = self.extract_verse_exact(input_normd_seg, input_seg, self.use_precompiled_patterns,
                                            target_verses)

            # removing input_token_span key as it is not needed anymore
            del output['input_token_span']

            result_pack = {}
            result_pack["camelbert"] = output
            result_pack["regex_qe"] = []
            for res in ress:
                res["input_span"] = (res["input_span"][0] + input_seg_start_index,
                                     res["input_span"][1] + input_seg_start_index)
                # regex tool should recognize camel_bert output as ayah and fully covers its span, otherwise it will be
                # removed
                #if res["input_span"][0] <= output["input_span"][0] and output["input_span"][1] <= res["input_span"][1]:
                if self.have_overlap(res["input_span"], output["input_span"]):
                    result_pack["regex_qe"].append(res)
            return result_pack

        if self.model_type == 'exact':
            if self.filters["use_camelbert"]:
                jump_len = 152 #202
                camelbert_max_input_length = 512
                segment_len = 302 #402 # saving tokens for new tokens which are going to be
                                  # generated in the normalization step in
                                  # self.get_camelbert_quranic_labels
                #overlap_len = segment_len - jump_len
                cover_cb_res_len = 8

                input_list = text.split(" ")
                # input_text_normd = self.normalize_for_camelbert(text)
                # input_list_normd = input_text_normd.split(" ")
                # tokenized_input = self.tokenizer(input_list_normd, truncation=False, is_split_into_words=True,
                #                                  max_length=None, return_tensors="pt")
                results = []
                #if len(input_list_normd) < camelbert_max_input_length:
                if len(self.tokenizer(self.normalize_for_camelbert(text).split(" "),
                                      truncation=False, is_split_into_words=True, max_length=None,
                                      return_tensors="pt").data['input_ids'][0]) < camelbert_max_input_length:
                    predicted_quranic_segments = self.get_camelbert_quranic_labels(text, custom_threshold = self.filters["custom_bert_token_threshold"])
                    for output in predicted_quranic_segments:
                        # result_pack = {}
                        # result_pack["camelbert"] = output
                        # result_pack["regex_qe"] = []
                        # input_seg = output['extracted']
                        # input_normd_seg = self.normalize(input_seg)
                        # ress = self.extract_verse_exact(input_normd_seg, input_seg, self.use_precompiled_patterns,
                        #                                 target_verses)
                        # for res in ress:
                        #     #res["input_span"] = res["input_span"] + output["input_span"]
                        #     res["input_span"] = (res["input_span"][0] + output["input_span"][0],
                        #                          res["input_span"][1] + output["input_span"][0])
                        #     result_pack["regex_qe"].append(res)
                        result_pack = get_result_pack(output, 0, cover_cb_res_len, input_list)
                        results.append(result_pack)
                    return results
                else:
                    #for start_index_token in range(0, len(input_list), jump_len):
                    reached_last_segment = False
                    start_index_token = 0
                    while start_index_token < len(input_list) and not reached_last_segment:
                        input_text_segment = None
                        segment_len_try = segment_len
                        jump_len_try = jump_len
                        # while not input_text_segment or\
                        #   len(self.normalize_for_camelbert(input_text_segment).split(" ")) > camelbert_max_input_length:

                        while not input_text_segment or\
                          len(self.tokenizer(self.normalize_for_camelbert(input_text_segment).split(" "),
                                             truncation=False, is_split_into_words=True, max_length=None,
                                             return_tensors="pt").data['input_ids'][0]) > camelbert_max_input_length:
                            if input_text_segment:
                                segment_len_try -= 50
                                jump_len_try -= 50
                            if (start_index_token + segment_len_try < len(input_list)) and not reached_last_segment :
                                input_text_segment = ' '.join(input_list[start_index_token:
                                                                         start_index_token + segment_len_try])
                                #end_index_token = start_index_token + segment_len_try
                            else:
                                start_index_token = len(input_list) - segment_len_try
                                input_text_segment = ' '.join(input_list[start_index_token:])
                                #end_index_token = len(input_list)
                                reached_last_segment = True
                        # assert len(self.normalize_for_camelbert(input_text_segment).split(" ")) \
                        #      < camelbert_max_input_length
                        assert segment_len_try > 0 and jump_len_try > 0
                        predicted_quranic_segments = self.get_camelbert_quranic_labels(input_text_segment,
                                                                                       return_token_span = True)
                        segment_results = []
                        for output in predicted_quranic_segments:
                            # input_seg = output['extracted']
                            # input_normd_seg = self.normalize(input_seg)
                            # ress = self.extract_verse_exact(input_normd_seg, input_seg, self.use_precompiled_patterns,
                            #                                 target_verses)
                            # for res in ress:
                            #     res["input_span"] = (res["input_span"][0] + output["input_span"][0] + start_index,
                            #                          res["input_span"][1] + output["input_span"][1] + start_index)
                            #     segment_results.append(res)
                            start_index = len(' '.join(input_list[:start_index_token]))
                            start_index = start_index + 1 if start_index_token != 0 else start_index # +1 for space
                            output["input_span"] = (output["input_span"][0] + start_index,
                                                    output["input_span"][1] + start_index)
                            result_pack = get_result_pack(output, start_index_token, cover_cb_res_len, input_list)
                            segment_results.append(result_pack)
                        results.extend(segment_results)
                        start_index_token += jump_len_try


                    seen = set()
                    final_results = []
                    for d in results:
                        if d["camelbert"]["input_span"] not in seen:
                            seen.add(d["camelbert"]["input_span"])
                            final_results.append(d)
                    #results = pd.unique(results).tolist()
                    return final_results

            else:
                input_normd = self.normalize(text)
                return self.extract_verse_exact(input_normd, text, self.use_precompiled_patterns, target_verses)
        elif self.model_type == 'apprx':
            input_normd = self.normalize(text)
            return self.extract_verse_apprx(input_normd)

    def have_overlap(self, s1, s2):
        s1 = pd.Interval(*s1, closed="both")
        s2 = pd.Interval(*s2, closed="both")
        result = s1.overlaps(s2)

        if result:
            return True
        else:
            return False

# if __name__ == '__main__':
#     filters = {'all_sw': True, "min_token_num": 2, "min_char_len_prop": 50, "idf_threshold":0,
#                      "consecutive_verses_priority":True}
#     start = time.time()
#     model = QuranicExtraction(model = 'exact', precompiled_patterns='off', parted = False,
#                               filters = filters)
#     end = time.time()
#     print(F"Time: {end-start}")
#     #for sent in testCases:
#     while True:
#         #input_text = input('Please enter your input text: ')
#
#         input_text = "<quranic_text>وَ تَوٰاصَوْا بِالصَّبْرِ</quranic_text> <footnote>[البلد17]</footnote>"
#         #target_verses = input('Please enter target verses (enter nothing for no filter): ')
#         target_verses = None
#         #idf_threshold = input("Please enter idf_threshold: ")
#         #model.filters["idf_threshold"] = float(idf_threshold)
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


# if __name__ == '__main__':
#     filters = {'all_sw': True, "min_token_num": 2, "min_char_len_prop": 50, "idf_threshold":0,
#                      "consecutive_verses_priority":True, "use_camelbert": True, "custom_bert_token_threshold": None} #3.5} #3 to 5
#     camelbert_checkpoint = "/home/sahebi/hdd/hadith/parsi.io/parsi_io/modules/quranic_extraction/camelbert_model/try4_checkpoint-3500"
#     #camelbert_checkpoint = None
#
#     with open("/volumes/hdd/users/sahebi/hadith/parsi.io/parsi_io/modules/quranic_extraction/metadata/single_words.pkl", 'rb') as f:
#         list_of_single_words_QENormd = pickle.load(f)
#     start = time.time()
#     model = QuranicExtraction(model = 'exact', precompiled_patterns='off', parted = False, filters = filters,
#                               camelbert_checkpoint=camelbert_checkpoint)#, single_words = list_of_single_words_QENormd)
#     end = time.time()
#     print(F"Time: {end-start}")
#     #for sent in testCases:
#     while True:
#         #input_text = 'اَنَّ <innocent>اَلْحَسَنَ</innocent> وَ <innocent>اَلْحُسَيْنَ عَلَيْهِمَا اَلسَّلاَمُ</innocent> مَرِضَا فَعَادَهُمَا جَدُّهُمَا <innocent>رَسُولُ اَللَّهِ</innocent> وَ عَادَهُمَا عَامَّةُ اَلْعَرَبِ فَقَالُوا يَا <innocent>اَبَا اَلْحَسَنِ</innocent> لَوْ نَذَرْتَ لِوَلَدَيْكَ نَذْراً فَقَالَ عَلَيْهِ اَلسَّلاَمُ اِنْ بَرِئَ وَلَدَايَ مِمَّا بِهِمَا صُمْتُ ثَلاَثَةَ اَيَّامٍ شُكْراً لِلَّهِ تَعَالَي وَ قَالَتْ <innocent>فَاطِمَةُ</innocent> مِثْلَ ذَلِكَ وَ قَالَتْ جَارِيَتُهَا فِضَّةُ اِنْ بَرِئَ سَيِّدَايَ مِمَّا بِهِمَا صُمْتُ ثَلاَثَةَ اَيَّامٍ شُكْراً لِلَّهِ تَعَالَي عَزَّ وَ جَلَّ فَاُلْبِسَا اَلْعَافِيَةَ وَ لَيْسَ عِنْدَ <innocent>الِ مُحَمَّدٍ صَلَّي اَللَّهُ عَلَيْهِ وَ الِهِ</innocent> لاَ قَلِيلٌ وَ لاَ كَثِيرٌ فَاجَرَ <innocent>عَلِيٌّ عَلَيْهِ اَلسَّلاَمُ</innocent> نَفْسَهُ لَيْلَةً اِلَي اَلصُّبْحِ يَسْقِي نَخْلاً بِشَيْءٍ مِنْ شَعِيرٍ وَ اَتَي بِهِ اِلَي اَلْمَنْزِلِ فَقَسَمَتْ <innocent>فَاطِمَةُ س</innocent> اِلَي ثَلاَثَةٍ فَطَحَنَتْ ثُلُثاً وَ خَبَزَتْ مِنْهُ خَمْسَ اَقْرَاصٍ لِكُلِّ وَاحِدٍ مِنْهُمْ قُرْصٌ وَ صَلَّي <innocent>اَمِيرُ اَلْمُؤْمِنِينَ عَلَيْهِ اَلسَّلاَمُ</innocent> صَلاَةَ اَلْمَغْرِبِ مَعَ <innocent>رَسُولِ اَللَّهِ</innocent> ثُمَّ اَتَي اَلْمَنْزِلَ فَوَضَعَ اَلطَّعَامَ بَيْنَ يَدَيْهِ فَجَاءَ مِسْكِينٌ فَوَقَفَ بِالْبَابِ وَ قَالَ اَلسَّلاَمُ عَلَيْكُمْ يَا <innocent>اَهْلَ بَيْتِ مُحَمَّدٍ</innocent> مِسْكِينٌ مِنْ مَسَاكِينِ اَلْمُسْلِمِينَ اَطْعِمُونِي اَطْعَمَكُمُ اَللَّهُ مِنْ مَوَائِدِ اَلْجَنَّةِ فَسَمِعَهُ <innocent>عَلِيٌّ عَلَيْهِ اَلسَّلاَمُ</innocent> فَقَالَ اَطْعِمُوهُ حِصَّتِي فَقَالَتْ <innocent>فَاطِمَةُ عَلَيْهَا اَلسَّلاَمُ</innocent> كَذَلِكَ وَ اَلْبَاقُونَ كَذَلِكَ فَاَطْعِمُوهُ اَلطَّعَامَ وَ مَكَثُوا يَوْمَهُمْ وَ لَيْلَتَهُمْ لَمْ يَذُوقُوا اِلاَّ اَلْمَاءَ اَلْقَرَاحَ فَلَمَّا كَانَ اَلْيَوْمُ اَلثَّانِي طَحَنَتْ <innocent>فَاطِمَةُ عَلَيْهَا اَلسَّلاَمُ</innocent> ثُلُثاً اخَرَ وَ خَبَزَتْهُ وَ اَتَي <innocent>اَمِيرُ اَلْمُؤْمِنِينَ عَلَيْهِ اَلسَّلاَمُ</innocent> مِنْ صَلاَةِ اَلْمَغْرِبِ مَعَ <innocent>رَسُولِ اَللَّهِ صَلَّي اَللَّهُ عَلَيْهِ وَ الِهِ</innocent> فَوَضَعَ اَلطَّعَامَ بَيْنَ يَدَيْهِ فَاَتَي يَتِيمٌ مِنْ اَيْتَامِ اَلْمُهَاجِرِينَ وَ قَالَ اَلسَّلاَمُ عَلَيْكُمْ يَا <innocent>اَهْلَ بَيْتِ مُحَمَّدٍ</innocent> اَنَا يَتِيمٌ مِنْ اَيْتَامِ اَلْمُهَاجِرِينَ اُسْتُشْهِدَ وَالِدِي يَوْمَ اَلْعَقَبَةِ اَطْعِمُونِي اَطْعَمَكُمُ اَللَّهُ مِنْ مَوَائِدِ اَلْجَنَّةِ فَسَمِعَهُ <innocent>عَلِيٌّ</innocent> وَ <innocent>فَاطِمَةُ عَلَيْهَا اَلسَّلاَمُ</innocent> وَ اَلْبَاقُونَ فَاَطْعَمُوهُ اَلطَّعَامَ وَ مَكَثُوا يَوْمَيْنِ وَ لَيْلَتَيْنِ لَمْ يَذُوقُوا اِلاَّ اَلْمَاءَ اَلْقَرَاحَ فَلَمَّا كَانَ اَلْيَوْمُ اَلثَّالِثُ قَامَتْ <innocent>فَاطِمَةُ عَلَيْهَا اَلسَّلاَمُ</innocent> اِلَي اَلثُّلُثِ اَلْبَاقِي وَ طَحَنَتْهُ وَ خَبَزَتْهُ وَ صَلَّي <innocent>عَلِيٌّ عَلَيْهِ اَلسَّلاَمُ</innocent> مَعَ <innocent>اَلنَّبِيِّ</innocent> صَلاَةَ اَلْمَغْرِبِ ثُمَّ اَتَي اَلْمَنْزِلَ فَوَضَعَ اَلطَّعَامَ بَيْنَ يَدَيْهِ فَجَاءَ اَسِيرٌ فَوَقَفَ بِالْبَابِ وَ قَالَ اَلسَّلاَمُ عَلَيْكُمْ يَا <innocent>اَهْلَ بَيْتِ مُحَمَّدٍ</innocent> تَاْسِرُونَنَا وَ لاَ تُطْعِمُونَّا اَطْعَمَكُمُ اَللَّهُ مِنْ مَوَائِدِ اَلْجَنَّةِ فَاِنِّي اَسِيرُ <innocent>مُحَمَّدٍ صَلَّي اَللَّهُ عَلَيْهِ وَ الِهِ</innocent> فَسَمِعَهُ <innocent>عَلِيٌّ عَلَيْهِ اَلسَّلاَمُ</innocent> فَاثَرَهُ وَ اثَرُوهُ مَعَهُ وَ مَكَثُوا ثَلاَثَةَ اَيَّامٍ بِلَيَالِيهَا لَمْ يَذُوقُوا اِلاَّ اَلْمَاءَ اَلْقَرَاحَ فَلَمَّا كَانَ اَلْيَوْمُ اَلرَّابِعُ وَ قَدْ وَفَوْا بِنَذْرِهِمْ اَخَذَ <innocent>عَلِيٌّ عَلَيْهِ اَلسَّلاَمُ</innocent> <innocent>اَلْحَسَنَ</innocent> بِيَدِهِ اَلْيُمْنَي وَ <innocent>اَلْحُسَيْنَ</innocent> بِيَدِهِ اَلْيُسْرَي وَ اَقْبَلَ نَحْوَ <innocent>رَسُولِ اَللَّهِ صَلَّي اَللَّهُ عَلَيْهِ وَ الِهِ</innocent> وَ هُمْ يَرْتَعِشُونَ كَالْفِرَاخِ مِنْ شِدَّةِ اَلْجُوعِ فَلَمَّا بَصُرَ بِهِمُ <innocent>اَلنَّبِيُّ صَلَّي اللَّهُ عَلَيْهِ وَ الِهِ</innocent> قَالَ يَا <innocent>اَبَا اَلْحَسَنِ</innocent> مَا اَشَدَّ مَا يَسُوؤُنِي مَا اَرَي بِكُمْ اِنْطَلِقْ بِنَا اِلَي اِبْنَتِي <innocent>فَاطِمَةَ</innocent> فَانْطَلَقُوا اِلَيْهَا وَ هِيَ فِي مِحْرَابِهَا تُصَلِّي وَ قَدْ لَصِقَ بَطْنُهَا بِظَهْرِهَا مِنْ شِدَّةِ اَلْجُوعِ فَلَمَّا رَاهَا <innocent>اَلنَّبِيُّ صَلَّي اللَّهُ عَلَيْهِ وَ الِهِ</innocent> قَالَ وَا غَوْثَاهْ <innocent>اَهْلُ بَيْتِ مُحَمَّدٍ</innocent> يَمُوتُونَ جُوعاً فَهَبَطَ جَبْرَائِيلُ عَلَيهِ اَلسَّلاَمُ وَ قَالَ خُذْ يَا <innocent>مُحَمَّدُ</innocent> هَنَّاَكَ اَللَّهُ فِي <innocent>اَهْلِ بَيْتِكَ</innocent> قَالَ وَ مَا اخُذُ يَا جَبْرَائِيلُ قَالَ <quranic_text>هَلْ اَتيٰ عَلَي اَلْاِنْسٰانِ</quranic_text> <footnote>[الانسان1]</footnote> اِلَي اخِرِ اَلسُّورَةِ.'
#         target_verses = None #input('Please enter target verses (enter nothing for no filter): ')
#         #idf_threshold = input("Please enter idf_threshold: ")
#         #model.filters["idf_threshold"] = float(idf_threshold)
#         target_verses = target_verses.split(" ") if target_verses else None
#         #input('Input any character to process next test case.')
#         #input_text = sent
#         start = time.time()
#         input_list = input_text.split(" ")
#         result = model.run(input_text, target_verses = target_verses)
#         end = time.time()
#
#         if result:
#             print(F"Number of results: {len(result)}")
#             print(F"Time: {end - start}")
#             for x in result:
#                 print(x)
#         exit()


# while True:
#     input_str = input("Please enter your input: ")
#     input_list = input_str.split(" ")
#     tokenized_input = tokenizer(input_list, truncation=True, is_split_into_words=True, max_length=512,
#                                 return_tensors="pt")
#     word_ids = tokenized_input.word_ids()
#     output_logits = model(**tokenized_input)['logits'].detach()[0]
#     tokens_label = np.argmax(output_logits, axis=1).tolist()
#     predicted_quranic_words_idx = np.unique(
#         [word_ids[idx] for idx, label in enumerate(tokens_label) if label != 0 and word_ids[idx] != None])
#     if predicted_quranic_words_idx.size == 0:
#         predicted_quranic_words_idx_segmented = []
#     else:
#         predicted_quranic_words_idx_segmented = break_to_subsequent(predicted_quranic_words_idx)
#
#     # breakpoint()
#
#     print("\nPredicted:")
#     for sent_idxs in predicted_quranic_words_idx_segmented:
#         print(' '.join([input_list[idx] for idx in sent_idxs]))
#     if len(input_data['tokens']) > 512:
#         print('(Input length is longer than 512 tokens)')
#
#     print('\n')



# if __name__ == '__main__':
#     filters = {'all_sw': False, "min_token_num": 2, "min_char_len_prop": 50, "idf_threshold":0,
#                      "consecutive_verses_priority":False}
#     camelbert_checkpoint = "/home/sahebi/hdd/hadith/parsi.io/parsi_io/modules/quranic_extraction/camelbert_model/try4_checkpoint-4000"
#
#     start = time.time()
#     model = QuranicExtraction(model = 'exact', precompiled_patterns='off', parted = False,
#                               filters = filters, camelbert_checkpoint=camelbert_checkpoint)
#     end = time.time()
#     print(F"Time: {end-start}")
#
#     qe_on_hadiths = {}
#     main_dataset_hadith_path = "/volumes/hdd/datasets/hadith/dataset_hadith/main"
#     json_files = os.listdir(main_dataset_hadith_path)
#     for json_file in json_files:
#         json_addr = os.path.join(main_dataset_hadith_path, json_file)
#         hadith_obj = Hadith(json_addr, main_dataset_hadith_path)
#         input_text = hadith_obj.text
#         target_verses = None
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

