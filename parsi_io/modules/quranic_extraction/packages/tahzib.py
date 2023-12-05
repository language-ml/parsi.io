from __future__ import unicode_literals
import regex
import codecs
import fnmatch
import os
import re
from hazm import *
from bleach import clean
from camel_tools.utils.normalize import normalize_unicode
from camel_tools.utils.normalize import normalize_alef_maksura_ar
from camel_tools.utils.normalize import normalize_alef_ar
from camel_tools.utils.normalize import normalize_alef_bw
from camel_tools.utils.normalize import normalize_teh_marbuta_ar
from camel_tools.utils.dediac import dediac_ar

PATH = os.path.dirname(__file__)


def normalize_arabic(sentence):
    # Normalize alef variants to 'ا'
    sent_norm = normalize_unicode(sentence)

    sent_norm = normalize_alef_bw(sent_norm)
    # Normalize alef variants to 'ا'
    sent_norm = normalize_alef_ar(sentence)

    # Normalize alef maksura 'ى' to yeh 'ي'
    sent_norm = normalize_alef_maksura_ar(sent_norm)

    # Normalize teh marbuta 'ة' to heh 'ه'
    # sent_norm = normalize_teh_marbuta_ar(sent_norm)
    return sent_norm


class HadithTahzib(object):

    def __init__(self):
        # arabic
        self._init_alphabet_norm()
        self._init_innocent_salams()
        self._init_regexitized_innocent_salams()
        # farsi
        self.fa_normalizer = Normalizer()
        # # arabic_erab
        self.erab = {"F": u"\u064B",  # tanvin fathe
                     "N": u"\u064C",  # tanvin zammeh
                     "K": u"\u064D",  # tanvin kasreh
                     "a": u"\u064E",  # fathe
                     "u": u"\u064F",  # zammeh
                     "i": u"\u0650",  # kasreh
                     "~": u"\u0651",  # tashdid
                     "o": u"\u0652",  # sokon
                     "^": u"\u0653",  # mad
                     "#": u"\u0654",  # hamzeh
                     "`": u"\u0670"}  # alef kharejeh

    def fix_tashdid_erab(self, a_text):
        if self.erab["~"] in a_text:
            new_text = ''
            for i, ch in enumerate(a_text):
                if i > 0 and ch == self.erab["~"]:
                    if a_text[i-1] in self.erab.values():
                        # # change erab and tashdid place
                        new_text = f'{new_text[:-1]}{self.erab["~"]}{a_text[i-1]}'
                    else:
                        new_text = f'{new_text}{ch}'
                else:
                    new_text = f'{new_text}{ch}'
            return new_text
        else:
            return a_text

    def heavy_process_hadith(self, text):
        text = self.heavy_normalize(text)
        return self.replace_ent_texts(text)

    def _init_innocent_salams(self):
        # patterns
        self.sin = ['سَلاَمُ اَللَّهِ عَلَيْهِمَا', 'سلام الله علیهما', 'سلام الله علیها', 'سلام الله عليها',
                    'سلام الله علیه', 'سلام الله عليه']
        self.sad = ['صَلَّى اَللَّهُ عَلَيْهِ وَ آلِهِ وَ سَلَّمَ', 'صَلَوَاتُ اَللَّهِ عَلَيْهِمْ أَجْمَعِينَ',
                    'صَلَوَاتُ اَللَّهِ وَ سَلاَمُهُ عَلَيْهِ', 'صَلَوَاتُ اَللَّهِ عَلَيْهِ وَ آلِهِ',
                    'صَلََّى اللََّهُ عَلَيْهِ وَ آلِهِ', 'صَلَّى اَللَّهُ عَلَيْهِ وَ آلِهِ',
                    'صَلَّى اللَّهُ عَلَيْهِ وَ آلِهِ', 'صَلَّى اللَّهِ عَلَيهِ وَ آلِهِ',
                    'صَلَوَاتُ اَللَّهِ عَلَيْهِمْ', 'صَلَوَاتُ اَللَّهُ عَلَيْهِمْ', 'صَلَوَاتُ اللَّهِ عَلَيْهِمْ',
                    'صَلَوَاتُ اَللَّهِ عَلَيْهَا', 'صَلَوَاتُ اَللَّهِ عَلَيهِم', 'صَلَوَاتُ اَللَّهِ عَلَيْهِ',
                    'صَلَوَاتُ اللهِ عَلَيْهِمْ', 'صَلَوَاتُ اللَّهِ عَلَيْهِ', 'صلى الله علیه و آله و سلم',
                    'صَلَّى اَللَّهُ عَلَيْهِ', 'صلوات الله علیهم أجمعین', 'صلوات الله و سلامه علیه',
                    'صلَّى اللِّه عليه و آله', 'صلّى اللّه عليه و آله', 'صلوات الله علیه و آله', 'صلى الله علیه و آله',
                    'صلوات اللّه عليهم', 'صلوات الله علیهم', 'صلوات الله علیها', 'صلوات الله علیه', 'صلوات الله عليه',
                    'صلى الله علیه']
        self.ayn = ['عَلَيْهِمُ اَلصَّلاَةُ وَ اَلسَّلاَمُ', 'عَلَيْهِ اَلصَّلاَةُ وَ اَلسَّلاَمُ',
                    'عَلَيْهِ وَ آلِهِ اَلسَّلاَمُ', 'علیه آلاف التحیة و السلام', 'عليه آلاف التحية و السلام',
                    'عَلَيْهِمَا اَلسَّلاَمُ', 'عَلَيْهِمَا السَّلاَم ُ', 'عَلَيْهِمَا السَّلاَمُ',
                    'عَلَيْهِمُ اَلسَّلاَمَ', 'عَلَيْهِمُ اَلسَّلاَمُ', 'عَلَيْهَا اَلسَّلاَمُ',
                    'عَلَيْهِمُ السَّلَامُ', 'عَلَيْهِمُ السَّلاَمُ', 'علیهم الصلاة و السلام', 'عَلَيْهَا السَّلاَمُ',
                    'عَلَيْهَا السَّلَامُ', 'عَلَيْهِم السَّلاَمُ', 'عَلَيهِمُ السَّلاَمُ', 'علیه الصلاة و السلام',
                    'عَلَيْهِ اَلسَّلاَمُ', 'عَلَيْهِ السَّلاَمُ', 'عَلَيْهِ السَّلَامُ', 'علیه و آله السلام',
                    'علیهما السلام ', 'عجل الله فرجه', 'عليهما السلام', 'علیهما السلام', 'علیهم السلام', 'عليهم السلام',
                    'عليها السلام', 'علیها السلام', 'علیه السلام', 'عليه السلام', 'عليه سلام', 'علیه سلام']


        self.sin = list(set([self.heavy_normalize(x) for x in self.sin]))
        self.sin.sort(key=len)
        self.sin = self.sin[::-1]

        self.sad = list(set([self.heavy_normalize(x) for x in self.sad]))
        self.sad.sort(key=len)
        self.sad = self.sad[::-1]

        self.ayn = list(set([self.heavy_normalize(x) for x in self.ayn]))
        self.ayn.sort(key=len)
        self.ayn = self.ayn[::-1]

        self.regex_sin = re.compile('|'.join(self.sin))
        self.regex_sad = re.compile('|'.join(self.sad))
        self.regex_ayn = re.compile('|'.join(self.ayn))

    def _init_regexitized_innocent_salams(self):
        self.AR_DIAC_CHARSET_patt = "(?:\u064b|\u064c|\u064d|\u064e|\u064f|\u0650|\u0651|\u0652|\u0670|\u0640)*"
        # temp = self.alpha_regex['\u0627'].pattern
        # ht.alpha_regex['\u0627'] = re.compile(temp +"|\u0625|\u0623|\u0671|\u0622")
        self.alpha_regex_2 = {}
        for (ch_norm, pattern) in self.alpha_regex.items():
            rep_pat = "(?:" + ch_norm + "|" + pattern.pattern + ")"
            self.alpha_regex_2[ch_norm] = re.compile(rep_pat)
        temp = self.alpha_regex['\u0627'].pattern
        rep_pat = "(?:" + '\u0627' + "|" + temp + "|\u0625|\u0623|\u0671|\u0622" + ")"
        self.alpha_regex_2['\u0627'] = re.compile(rep_pat)

        sin_salam = ['سَلاَمُ اَللَّهِ عَلَيْهِمَا', 'سلام الله علیهما', 'سلام الله علیها', 'سلام الله عليها',
                     'سلام الله علیه', 'سلام الله عليه']
        sad_salam = ['صَلَّى اَللَّهُ عَلَيْهِ وَ آلِهِ وَ سَلَّمَ', 'صَلَوَاتُ اَللَّهِ عَلَيْهِمْ أَجْمَعِينَ',
                     'صَلَوَاتُ اَللَّهِ وَ سَلاَمُهُ عَلَيْهِ', 'صَلَوَاتُ اَللَّهِ عَلَيْهِ وَ آلِهِ',
                     'صَلََّى اللََّهُ عَلَيْهِ وَ آلِهِ', 'صَلَّى اَللَّهُ عَلَيْهِ وَ آلِهِ',
                     'صَلَّى اللَّهُ عَلَيْهِ وَ آلِهِ', 'صَلَّى اللَّهِ عَلَيهِ وَ آلِهِ',
                     'صَلَوَاتُ اَللَّهِ عَلَيْهِمْ', 'صَلَوَاتُ اَللَّهُ عَلَيْهِمْ', 'صَلَوَاتُ اللَّهِ عَلَيْهِمْ',
                     'صَلَوَاتُ اَللَّهِ عَلَيْهَا', 'صَلَوَاتُ اَللَّهِ عَلَيهِم', 'صَلَوَاتُ اَللَّهِ عَلَيْهِ',
                     'صَلَوَاتُ اللهِ عَلَيْهِمْ', 'صَلَوَاتُ اللَّهِ عَلَيْهِ', 'صلى الله علیه و آله و سلم',
                     'صَلَّى اَللَّهُ عَلَيْهِ', 'صلوات الله علیهم أجمعین', 'صلوات الله و سلامه علیه',
                     'صلَّى اللِّه عليه و آله', 'صلّى اللّه عليه و آله', 'صلوات الله علیه و آله', 'صلى الله علیه و آله',
                     'صلوات اللّه عليهم', 'صلوات الله علیهم', 'صلوات الله علیها', 'صلوات الله علیه', 'صلوات الله عليه',
                     'صلى الله علیه', 'صلوات الله عليه و اله و سلم']
        ayn_salam = ['عَلَيْهِمُ اَلصَّلاَةُ وَ اَلسَّلاَمُ', 'عَلَيْهِ اَلصَّلاَةُ وَ اَلسَّلاَمُ',
                     'عَلَيْهِ وَ آلِهِ اَلسَّلاَمُ', 'علیه آلاف التحیة و السلام', 'عليه آلاف التحية و السلام',
                     'عَلَيْهِمَا اَلسَّلاَمُ', 'عَلَيْهِمَا السَّلاَم ُ', 'عَلَيْهِمَا السَّلاَمُ',
                     'عَلَيْهِمُ اَلسَّلاَمَ', 'عَلَيْهِمُ اَلسَّلاَمُ', 'عَلَيْهَا اَلسَّلاَمُ',
                     'عَلَيْهِمُ السَّلَامُ', 'عَلَيْهِمُ السَّلاَمُ', 'علیهم الصلاة و السلام', 'عَلَيْهَا السَّلاَمُ',
                     'عَلَيْهَا السَّلَامُ', 'عَلَيْهِم السَّلاَمُ', 'عَلَيهِمُ السَّلاَمُ', 'علیه الصلاة و السلام',
                     'عَلَيْهِ اَلسَّلاَمُ', 'عَلَيْهِ السَّلاَمُ', 'عَلَيْهِ السَّلَامُ', 'علیه و آله السلام', 'علیه‏السلام',
                     'علیهما السلام ', 'عجل الله فرجه', 'عليهما السلام', 'علیهما السلام', 'علیهم السلام',
                     'عليهم السلام', 'عليها السلام', 'علیها السلام', 'علیه السلام', 'عليه السلام', 'عليه سلام',
                     'علیه سلام', 'علیهماالسلام', 'عليه‏السلام', 'عليهم‏السلام']

        sin_salam_regexd = [self.regexitize_term(w, insert_dash_b=False) for w in sin_salam]
        sad_salam_regexd = [self.regexitize_term(w, insert_dash_b=False) for w in sad_salam]
        ayn_salam_regexd = [self.regexitize_term(w, insert_dash_b=False) for w in ayn_salam[:-2]]
        ayn_salam_regexd.extend(
            [self.regexitize_term(x, insert_dash_b=False, normalize_before=False) for x in ayn_salam[-2:]])

        self.sin_salam_regex = re.compile("(" + "|".join(sin_salam_regexd) + ")")
        self.sad_salam_regex = re.compile("(" + "|".join(sad_salam_regexd) + ")")
        self.ayn_salam_regex = re.compile("(" + "|".join(ayn_salam_regexd) + ")")

    def heavy_normalize(self, text, remove_punc=False, remove_hamza=False, remove_salams=False):
        text = self.normalize_alpha(text, dediac=True)
        text = self.remove_all_tags(text)
        text = ' '.join(re.findall(self.punc_regex, text))
        text = self._remove_non_arabic(text)
        text = ''.join([i for i in text if not i.isdigit()])
        text = self.regex_all_puncs.sub('', text) if remove_punc else text
        text = text.replace('ء', '') if remove_hamza else text
        if remove_salams:
            text = self.sin_salam_regex.sub('', text)
            text = self.sad_salam_regex.sub('', text)
            text = self.ayn_salam_regex.sub('', text)
        return self.remove_extra_space(text).strip()

    def join_punctuation(self, text, af_characters=[',', '?', '،', '!', ';', '؟', '»', ':', '.', '؛'],
                         bf_characters=['«'], split_by_puncs=False):
        if split_by_puncs:
            temp = af_characters + bf_characters
            puncs = '|'.join(list(set(temp)))
            puncs = re.sub("([\[\(\)\]])", '\\\\\\1', puncs)
            puncs_reg = re.compile("([" + puncs + "])")
            seq = re.split(puncs_reg, text)
            # seq = [x.strip(' ') for x in seq if x.strip() != '']
        else:
            seq = text.split()
        af_characters = set(af_characters)
        bf_characters = set(bf_characters)
        results = []
        attach_to_next = ""
        for idx, current in enumerate(seq):
            if current in af_characters and idx > 0:
                # set_trace()
                res = results[-1].rstrip()
                results[-1] = F"{res}{attach_to_next}{current}"
                attach_to_next = ""
            elif current in bf_characters:
                attach_to_next = current
            else:
                crrn = current.lstrip() if attach_to_next else current
                results.append(F"{attach_to_next}{crrn}")
                attach_to_next = ""
        # return ' '.join(results)
        return ''.join(results)

    def normalize_beta(self, text):
        # fix some problematic characters
        text = text.replace('_', ' ')
        text = text.replace('‏', ' ')
        text = text.replace('ئ', 'ى')
        return text

    def normalize_alpha(self, text, dediac=True):
        # Normalize alef variants to 'ا'
        text = normalize_unicode(text)
        #text = normalize_alef_bw(text)
        # Normalize alef maksura 'ى' to yeh 'ي'
        text = normalize_alef_maksura_ar(text)
        # Normalize alef variants to 'ا'
        text = normalize_alef_ar(text)
        # Normalize teh marbuta 'ة' to heh 'ه'
        text = normalize_teh_marbuta_ar(text)
        # remove diac
        if dediac:
            text = dediac_ar(text)
            # normalize_alpha
        for alternative, regx in self.alpha_regex.items():
            text = re.sub(regx, alternative, text)
        return text

    def _init_alphabet_norm(self):

        self.alpha_regex = dict()
        self.non_arabic = re.compile(
            "[^0-9\u0600-\u06ff\u0750-\u077f\ufb50-\ufbc1\ufbd3-\ufd3f\ufd50-\ufd8f\ufd50-\ufd8f\ufe70-\ufefc\uFDF0-\uFDFD.0-9\s.,!?;،:؛»«؟]+")
        self.regex_tags = re.compile("([^<>]*?)(?=[^>]*?<)")
        self.regex_spaces = re.compile("\s\s+")

        self.regex_blank = re.compile("  +")
        self.regex_xad = re.compile('­')
        self.regex_little_alef = re.compile("ٰ")
        self.all_bracket_space = re.compile("(?<=\[)( *)|( *)(?=\[)|( *)(?=\])|(?<=\])( *)")
        self.in_bracket_space = re.compile("(?<=\[)( *)|( *)(?=\])")
        self.book_in_bracket_in_splitted = re.compile("(\s*\[.*\s*\]\s*)")
        self.book_in_bracket_in_hadith_start_dot = re.compile("(?<=\.)\s*.{,4}\s*،\s*(?=\[)")
        self.book_in_bracket_in_hadith_start_comma = re.compile("(?<=،)\s*.{,4}\s*،\s*(?=\[)")

        self.regex_all_tags = re.compile("<[^>]+>|\\n+")
        self.num_regex = re.compile(r'[0-9]+')
        self.punc_regex = re.compile(r"[\w']+|[.,!?;،:؛»«؟]")  # ???

        # self.regex_element_by_tag = regex.compile("[\"\'_<>.,!?;،:؛»«؟]*" + "<([^>]+)>.*?<\/\\1>"+
        #                                           "[\"\'_<>.,!?;،:؛»«؟]*"
        #                                           + "|(?<=</[^>]+>|^).*?(?=<[^>]+>|$)")
        # '[\"\'_.,!?;،:؟«»؛]*<([^>]+)>.*?<\/\\1>'
        # self.regex_element_by_tag = regex.compile("(<[^>]+>[^<]*?<\/[^>]+>[\"\'_.,!?:،؛»«؟]*)")
        self.regex_element_by_tag = regex.compile("(<([^>]+)>.*?<\/\\2>[\"\'_.,!?:،؛»«؟]*)")

        self.regex_all_puncs = re.compile("[\"\'_<>.,!?;،:()؛»«؟]")
        self.all_puncs = [',', '?', '،', '!', ';', '؟', '»', ':', '.', '؛', ')', ']', '«', '[', '(', '"', "'", "_", ">",
                          "<", ">", '-']

        self.regex_non_closed_ending_tag = re.compile("(<([^\/>]+)>[^<]*?$)")
        self.regex_non_opened_starting_tag = re.compile("^([^<]*?</([^>]+)>)")
        self.in_footnote_tag = re.compile("<footnote>([\s\S]*?)</footnote>")

        self.regex_is_tag_name = re.compile("^[A-Za-z0-9_-]+$")

        self.regex_wordPuncBracket = re.compile(r"[^<>]*\s*[.,!?;،:؛»«؟]?\s*\[[^<>]*\]\s*[.,!?;،:؛»«؟]?\s*")
        # self.regex_in_bracket_with_prev_space = re.compile("\s*\[[\s\S]*\]")
        self.regex_in_bracket_begin_or_end_with_space = re.compile("^\[[\s\S]*\]\s*|\s*\[[\s\S]*\]$")

        self.last_innocent = re.compile("(<innocent>(?!.*<innocent>).*</innocent>)")
        self.problematic_innocent = re.compile('(<innocent>.*(<innocent>.*</innocent>).*</innocent>)')
        items = [
            (r"ٰا" + "|" + r"ئ|أ", r"ا"),
            # (r"ئ|أ", r"ا"),
            # (r'ء', 'ئ'),
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
            #(r"ވ|ﯙ|ۈ|ۋ|ﺆ|ۊ|ۇ|ۏ|ۅ|ۉ|ﻭ|ﻮ|ؤ|وو", r"و"),
            (r"ވ|ﯙ|ۈ|ۋ|ﺆ|ۊ|ۇ|ۏ|ۅ|ۉ|ﻭ|ﻮ|ؤ|و", r"و"),
            (r"ﻬ|ھ|ﻩ|ﻫ|ﻪ|ۀ|ە|ہ|ة", r"ه"),
            (r"ڭ|ﻚ|ﮎ|ﻜ|ﮏ|ګ|ﻛ|ﮑ|ﮐ|ڪ|ک", r"ك"),
            (r"ﭛ|ﻯ|ۍ|ﻰ|ﻱ|ﻲ|ں|ﻳ|ﻴ|ﯼ|ې|ﯽ|ﯾ|ﯿ|ێ|ے|ى|ی|یٰ", r"ي"),
        ]

        for x, y in items:
            self.alpha_regex[y] = re.compile(x)

        compile_patterns = lambda patterns: [(re.compile(pattern), repl) for pattern, repl in patterns]
        punc_after = r'\-\.:!،؛؟»\]\)\}«\[\(\{\\'
        self.punctuation_add_spacing_patterns = compile_patterns([
            ('"([^\n"]+)"', r' " \1 " '),  # add space before and after quotation
            ('([' + punc_after + '])', r' \1'),  # add space before
            ('([' + punc_after + '])', r'\1 '),  # add space after
            ('([' + punc_after + '])([^ ' + punc_after + '\d۰۱۲۳۴۵۶۷۸۹])', r'\1 \2'),  # put space after . and :
            ('(' + '\d+' + ')', r' \1 ')
            # ('([' + punc_after + '])([^ ' + punc_after + '])', r'\1 \2'),
            # ('([^ ' + punc_after + '])([' + punc_after + '])', r'\1 \2'),
        ])

        # self.punctuation_normalize_space_patterns = compile_patterns(
        #     [('\s+'+'(['+punc+'])', r"\1") for punc in self.all_puncs])
        # self.punctuation_normalize_space_patterns2 = compile_patterns(
        #     [('([' + punc + '])'+'\s', r"\1") for punc in self.all_puncs])

        self.tag_p1 = dict()
        self.tag_p2 = dict()
        self.tag_p3 = dict()
        self.tag_p4 = dict()
        for tag in ['quranic_text', 'narrators', 'innocent', 'footnote', 'difference', 'NL', 'teller']:
            self.tag_p1[tag] = re.compile(F"\s*<{tag}>\s*")
            self.tag_p2[tag] = re.compile(F"\s*</{tag}>\s*")
            self.tag_p3[tag] = re.compile(F"[^>]<{tag}>")
            self.tag_p4[tag] = re.compile(F"</{tag}>[^<]")

        self.regex_ayah_address = re.compile("<footnote>(.*?)</footnote>")
        self.regex_ayah_text = re.compile("<quranic_text>(.*?)</quranic_text>")
        self.regex_innocent_text = re.compile("<innocent>(.*?)</innocent>")

    def _remove_non_arabic(self, text):
        return re.sub(self.non_arabic, ' ', text).strip()

    def remove_non_arabic_from_text(self, text):
        """
            remove non-arabic from texts
        """
        for x in set(re.findall(self.regex_tags, text)):
            if x != ' ':
                text = text.replace(x, self._remove_non_arabic(x))
        return text

    def remove_extra_space(self, text):
        return re.sub(self.regex_spaces, " ", text)

    def remove_blank_char(self, text):
        return re.sub(self.regex_blank, " ", text)

    def remove_all_tags(self, text):
        return re.sub(self.regex_all_tags, ' ', text)

    def regexitize_term(self, term, insert_dash_b=True, normalize_before=True):
        if type(term) == tuple:
            not_bef, term, not_aft = term
            not_bef = self.regexitize_term(not_bef) if not_bef else ""
            not_aft = self.regexitize_term(not_aft) if not_aft else ""
        else:
            not_bef = ""
            not_aft = ""
        if normalize_before:
            norm_term = self.heavy_normalize(term)
        else:
            norm_term = term
        char_list = list(norm_term)
        char_list = [x + self.AR_DIAC_CHARSET_patt for x in char_list]
        norm_term = ''.join(char_list)
        for (ch_norm, pattern) in self.alpha_regex_2.items():
            norm_term = pattern.sub(pattern.pattern, norm_term)
        if insert_dash_b:
            norm_term = "\\b" + norm_term + "\\b"

        norm_term = F"(?<!{not_bef}[a-zA-z0-9_<>.,!?;،:؛»«؟ ]*){norm_term}" if not_bef else norm_term

        norm_term += F"(?![a-zA-z0-9_<>.,!?;،:؛»«؟ ]*{not_aft})" if not_aft else ''

        return norm_term

    def get_compiled_regex_from_mentions(self, mentions, insert_dash_b=True, normalize_before=True):
        mentions_regexs = [self.regexitize_term(w, insert_dash_b, normalize_before) for w in mentions]
        total_mentions_regex = regex.compile("(" + "|".join(mentions_regexs) + ")")
        return total_mentions_regexn

    @staticmethod
    def check_attr(tag, name, value):
        return True

    def remove_tags_exceptions(self, src, allowed=['a']):
        # ToDo: add regular expression to add extra space before and after tags
        return clean(src, tags=allowed, strip=True, attributes=self.check_attr, strip_comments=True)

    def replace_ent_texts(self, text):
        # TODO not to remove diac
        text = re.sub(self.regex_sin, ' س ', text)
        text = re.sub(self.regex_sad, ' ص ', text)
        text = re.sub(self.regex_ayn, ' ع ', text)
        return self.remove_extra_space(text)

    @staticmethod
    def recursive_glob(treeroot, pattern):
        '''
        :param treeroot: the path to the directory
        :param pattern:  the pattern of files
        :return:
        '''
        results = []
        for base, dirs, files in os.walk(treeroot):
            good_files = fnmatch.filter(files, pattern)
            results = [f'{base}/{f}' for f in good_files]
        return results

    def remove_words(self, words, remove_duplicate=False):  # , remove_puncs = False):
        selected_words = []
        selected_words_ind = []
        for ind, word in enumerate(words):
            normd_word = self.heavy_normalize(word)
            if normd_word not in selected_words:
                selected_words.append(normd_word)
                selected_words_ind.append(ind)
        return [words[i] for i in selected_words_ind]

    # def split_elements(self, xml, join_punc = True):
    #     temp = [match.group() for match in list(self.regex_element_by_tag.finditer(xml))]
    #     res = []
    #     for el in temp:
    #         if '</' not in el:
    #             res.extend(el.split())
    #         else:
    #             res.append(el)
    #     return res

    def split_elements(self, xml):
        """
        get a xml text as input and return a list of words and also quran parts entity
        """
        split = self.regex_element_by_tag.split(xml)
        split = [x for x in split if x not in ['', ' '] and not self.regex_is_tag_name.search(x)]
        res = []
        ind = 0
        while ind < len(split):
            el = split[ind]
            if el == '' or self.regex_is_tag_name.search(el):
                pass
            elif "<quranic_text>" in el:
                if ind + 1 < len(split) and ("<footnote>" in split[ind + 1]):
                    res.append(split[ind] + ' ' + split[ind + 1])
                    ind += 1
                else:
                    res.append(el)
                # elif ind+2 < len(split) and ("<footnote>" in split[ind+2]):
                #     res.append(split[ind]+' '+split[ind+2])
                #     ind+=2
            elif '</' not in el:
                res.extend(el.split())
            else:
                res.append(el)
            ind += 1
        return res

    # def split_elements(self, xml, mentions):
    #     elements = split_elements(xml)

    def punctuation_add_spacing(self, text):
        for pattern, repl in self.punctuation_add_spacing_patterns:
            text = pattern.sub(repl, text)
        return text

    # def punctuation_normalize_space_in_text(self, text):
    #     for pattern, repl in self.punctuation_normalize_space_patterns2:
    #         text = pattern.sub(repl, text)
    #     for pattern, repl in self.punctuation_normalize_space_patterns:
    #         text = pattern.sub(repl, text)
    #     for p in [',', '?', '،', '!', ';', '؟', '»', ':', '.', '؛', ')', ']', '«', '[', '(', '"', "'", '-']:
    #         text = text.replace(p, f'{p} ')
    #     # for pattern, repl in self.punctuation_normalize_space_patterns3:
    #     #     text = pattern.sub(repl, text)
    #     return text

    def remove_in_footnote_tag_spaces(self, xml):
        return self.in_footnote_tag.sub(lambda x: x.group().replace(" ", ""), xml)

    def segments_postprocessing(self, segs, join_punc=False):
        af_c = [',', '?', '،', '!', ';', '؟', '»', ':', '.', '؛', ']']
        bf_c = ['[', '«']
        if join_punc:
            segs_corr = [self.join_punctuation(
                self.clean_text_tag(
                    self.join_punctuation(
                        self.remove_in_footnote_tag_spaces(x),
                        af_characters=af_c, bf_characters=bf_c)),
                af_characters=af_c, bf_characters=bf_c) for x in segs]
        else:
            segs_corr = [self.clean_text_tag(self.remove_in_footnote_tag_spaces(x)) for x in segs]
        return segs_corr

    def get_token_index_of_segment_with_postprocessing(self, segs):
        segs_split = [x.split() for x in self.segments_postprocessing(segs)]
        x = 0
        start_seg_ind = []
        for i in range(len(segs_split)):
            start_seg_ind.append(x)
            x += len(segs_split[i])
        return start_seg_ind

    def clean_text_tag(self, text, normalize=False):

        # allowed = ['original_text','quranic_text','narrators','innocent','footnote', 'difference', 'NL']

        text = text.replace('\n', ' ')
        # remove non-arabic
        # text = Hadith.tahzib.remove_non_arabic_from_text(text)

        # replace
        text = self.replace_ent_texts(text)

        # allowed = ['quranic_text','innocent','footnote']
        allowed = ['quranic_text', 'narrators', 'innocent', 'footnote', 'difference', 'NL', 'teller']
        for tag in allowed:
            text = re.sub(self.tag_p1[tag], F" <{tag}>", text)
            text = re.sub(self.tag_p2[tag], F"</{tag}> ", text)
            # text = re.sub(self.tag_p3[tag] , F" <{tag}>", text)
            # text = re.sub(self.tag_p4[tag], F"</{tag}> ", text)

        # remove
        if normalize:
            return self.fa_normalizer.normalize(self.remove_extra_space(text))
        else:
            return self.remove_extra_space(text)
