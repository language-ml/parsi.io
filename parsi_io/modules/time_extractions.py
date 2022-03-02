import os
import re

from parstdex import MarkerExtractor


class TimeExtraction(object):
    def __init__(self):
        # model initialization
        self.model = MarkerExtractor()

    def run(self, text):

        dict_time_extraction = {'Normalized_Sentence': '',
                                'Spans': [],
                                'Markers': [],
                                'Values': []}

        normalized_sentence, spans, values = self.model.time_value_extractor(text)

        dict_time_extraction['Normalized_Sentence'] = normalized_sentence
        dict_time_extraction['Spans'] = spans
        dict_time_extraction['Markers'] = [normalized_sentence[item[0]:item[1]] for item in spans]
        dict_time_extraction['Values'] = values

        return dict_time_extraction
		
		
### Test:
# def main():
#     t = TimeExtraction()
#     print(t.run("سلام ساعت ۸ شب می‌بینمت."))
#
#
# if __name__ == '__main__':
#     main()
