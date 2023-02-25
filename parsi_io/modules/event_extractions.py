from parsi_io.modules.event_extractor.event_extractions import EventExtractor


class EventExtraction(object):
    def __init__(self):
        # model initialization
        self.model = EventExtractor()

    def run(self, text, mode=0):
        return self.model.run(text, mode=mode)