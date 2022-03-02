import re


class Normalizer:
    """
    Normalizer class is used to:
    - preprocess input files(preprocess_file)
    - normalized arabic alphabet into persian alphabet(normalize_alphabet)
    - normalize space - digit to word concatenation - comma and other spacial symbols
    - normalize_annotation method is used to normalize annotation files in utilities/annotation folder
    - normalize_cumulative method execute normalize alphabet and space consequently
    """
    ALPHABET_DICT = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی',
    }

    FA_NUMBERS = "۰|۱|۲|۳|۴|۵|۶|۷|۸|۹"
    EN_NUMBERS = "0|1|2|3|4|5|6|7|8|9"
    Symbols = ":|/|-"
    C_NUMBERS = FA_NUMBERS + "|" + EN_NUMBERS + "|" + Symbols

    def normalize_alphabet(self, text):
        pattern = "|".join(map(re.escape, self.ALPHABET_DICT.keys()))
        return re.sub(pattern, lambda m: self.ALPHABET_DICT[m.group()], str(text))

    def normalize_space(self, text):
        res = text.replace('،', '')
        res = ':'.join([i.lstrip().rstrip() for i in res.split(':')])
        res = '-'.join([i.lstrip().rstrip() for i in res.split('-')])
        res = '/'.join([i.lstrip().rstrip() for i in res.split('/')])
        res = ' ( '.join([i.lstrip().rstrip() for i in res.split('(')])
        res = ' ) '.join([i.lstrip().rstrip() for i in res.split(')')])
        res = '/'.join([i.lstrip().rstrip() for i in res.split('\\')])
        res = re.sub(fr'((?:{self.C_NUMBERS})+(\.(?:{self.C_NUMBERS})+)?)', r' \1 ', res)
        # res = res.replace('\u200c', '')
        res = ' '.join(res.split())
        res = res + ' .' if res[-1] != '.' else res
        return res

    @staticmethod
    def preprocess_file(path):
        with open(path, 'r', encoding="utf8") as file:
            text = file.readlines()
            text = text[1:]  # first line is empty
            text = [x.rstrip() for x in text]  # remove \n
            return text

    def normalize_annotation(self, path):
        text = self.preprocess_file(path)
        annotation_mark = "|".join(text)
        return annotation_mark

    def normalize_cumulative(self, text):
        res = self.normalize_alphabet(text)
        res = self.normalize_space(res)
        return res
