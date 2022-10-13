from parsanonymizer.utils.normalizer import Normalizer
from parsanonymizer.utils.pattern_to_regex import Patterns
from parsanonymizer.utils.spans import create_spans
from parsanonymizer.utils.spans import merge_spans

from parstdex import Parstdex

class Model(object):
    def __init__(self):
        # Normalizer: convert arabic YE and KAF to persian ones.
        self.normalizer = Normalizer()
        # Patterns: patterns to regex generator
        self.regexes = Patterns().regexes
        with open ('regexes.txt', 'w', encoding='utf-8-sig') as f:
            for key in self.regexes.keys():
                f.write(f'{key}\n\n')
                for regex in self.regexes[key]:
                    f.write(f'{regex}\n')
                f.write('\n')
        self.parstdex_model = Parstdex()
        test = self.parstdex_model.extract_span('')

        super(Model, self).__init__()

    def extract_span(self, text: str):

        time_spans = self.parstdex_model.extract_span(text)
        

        # apply normalizer on input text
        text = self.normalizer.normalize(text)

        # Create spans
        spans = create_spans(self.regexes, text)
        spans = merge_spans(spans, text)
        spans = {**spans,**time_spans}

        return spans
