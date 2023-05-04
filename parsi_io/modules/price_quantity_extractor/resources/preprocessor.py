import json
import hazm
import re
from pathlib import Path

path = Path(__file__).parent

class Preprocessor:

    def __init__(self):
        file_path = str(path)+'/dataset/informal_numbers.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            self.informal_numbers_dict = json.load(file)

    def preprocess(self, text):
        text = self.normalize(text)
        text = self.fix_hamza(text)
        text = self.fix_arabic_ta(text)
        text = self.fix_arabic_ye(text)
        text = self.fix_half_space_ye(text)
        text = self.fix_single_ye(text)
        text = self.fix_informal_numbers(text)
        return text

    def normalize(self, text):
        normalizer = hazm.Normalizer()
        return normalizer.normalize(text)
    
    def fix_hamza(self, text):
        return text.replace('ء', '')
    
    def fix_arabic_ta(self, text):
        return text.replace('ة', 'ه')

    def fix_arabic_ye(self, text):
        return text.replace('ي', 'ی')

    def fix_half_space_ye(self, text):
        return text.replace('\u200cی ', ' ')
    
    def fix_single_ye(self, text):
        return text.replace(' ی ', ' ')

    def fix_informal_numbers(self, text):
        for informal_num, formal_num in self.informal_numbers_dict.items():
            to_be_replaced_words_spans = []
            for match in re.finditer(informal_num, text):
                before_index = match.span()[0] - 1
                after_index = match.span()[1]
                if before_index >= 0 and re.match('\w', text[before_index]):
                    continue
                if after_index < len(text) and re.match('\w', text[after_index]):
                    continue
                to_be_replaced_words_spans.append(match.span())
            for span in to_be_replaced_words_spans:
                text = text[:span[0]] + formal_num + text[span[1]:]
        return text