from parstdex import Parstdex


class TimeExtraction(object):
    def __init__(self):
        # model initialization
        self.model = Parstdex()

    def run(self, text):
        result = {}

        spans = self.model.extract_span(text)
        result['spans'] = spans

        markers = self.model.extract_marker(text)
        result['markers'] = markers

        values = self.model.extract_value(text)
        result['values'] = values

        ners = self.model.extract_ner(text)
        result['ner'] = ners

        return result
