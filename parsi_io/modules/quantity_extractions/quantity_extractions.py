import json
import hazm
from .preprocessor import Preprocessor
from .helpers import *
from .unit_extractor import *
from .number_extractor import *
from .units_conversion import *
from pathlib import Path

path = Path(__file__).parent

class QuantityExtraction:
    def __init__(self, tagger=None, chunker=None, quantities_word_network=None, related_words_dict=None, preprocessor=None):
        if tagger:
            self.tagger = tagger
        else:
            self.tagger = hazm.POSTagger(model=str(path)+'/resources/hazm/postagger.model')

        if chunker:
            self.chunker = chunker
        else:
            self.chunker = hazm.Chunker(model=str(path)+'/resources/hazm/chunker.model')

        if quantities_word_network:
            self.quantities_word_network = quantities_word_network
        else:
            self.quantities_word_network = {}
            with open(str(path)+'/resources/dataset/quantities_word_network.json', 'r', encoding='utf-8') as file:
                self.quantities_word_network = json.load(file)

        if related_words_dict:
            self.related_words_dict = related_words_dict
        else:
            self.related_words_dict = {}
            with open(str(path)+'/resources/dataset/quantities_related_names.json', 'r', encoding='utf-8') as file:
                self.related_words_dict = json.load(file)

        if preprocessor:
            self.preprocessor = preprocessor
        else:
            self.preprocessor = Preprocessor()

    def run(self, text):
        text = self.preprocessor.preprocess(text)
        expressions = extract_expressions(text, self.tagger, self.chunker, self.related_words_dict)
        qualitative_expressions = extract_qualitative_expressions(text, self.tagger, self.quantities_word_network)
        results = expressions + qualitative_expressions
        results.sort(key=lambda x: x.span[0])
        return list(map(ExtractedQuantity.get_dict, results))
        
    def convert(self, question):
        return answer_conversion_question(question)
