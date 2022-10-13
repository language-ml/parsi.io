import re

class Normalizer:
    """
    Normalizer class is used to:
    - normalized arabic alphabet into persian alphabet(normalize_alphabet)
    """
    ALPHABET_DICT = {
        'ك': 'ک',
        'ى': 'ی',
        'ي': 'ی',
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '–': '-'
    }

    def normalize(self, text):
        """
        normalizes arabic alphabet into persian alphabet
        :return:
        :type text: str
        """
        pattern = "|".join(map(re.escape, self.ALPHABET_DICT.keys()))
        return re.sub(pattern, lambda m: self.ALPHABET_DICT[m.group()], str(text))
