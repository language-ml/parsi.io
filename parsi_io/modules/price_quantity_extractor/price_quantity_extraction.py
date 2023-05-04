import itertools
import json
import hazm
from resources.preprocessor import Preprocessor
from resources.helpers import *
from resources.unit_extractor import *
from resources.number_extractor import *
from resources.units_conversion import *
from pathlib import Path

path = Path(__file__).parent

class PriceAndQuantityExtraction:
    def __init__(self, tagger=None, chunker=None, quantities_word_network=None, related_words_dict=None, preprocessor=None, normalizer=None):
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

        if normalizer:
            self.normalizer = normalizer
        else:
            self.normalizer = hazm.Normalizer()

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

        self.acceptable_types = json.load(open(str(path)+'/resources/dataset/acceptable_unit_types.json'))
        self.price_unitlist = json.load(open(str(path)+'/resources/dataset/price_units.json'))
        self.products_list = json.load(open(str(path)+'/resources/dataset/products_v2.json'))

        self.PRICE_UNITS = join_patterns(self.price_unitlist)
        self.PRODUCTS = join_patterns(self.products_list)

    def initial_extractor(self, text):
        text = self.preprocessor.preprocess(text)
        expressions = extract_expressions(text, self.tagger, self.chunker, self.related_words_dict)
        qualitative_expressions = extract_qualitative_expressions(text, self.tagger, self.quantities_word_network)
        results = expressions + qualitative_expressions
        results.sort(key=lambda x: x.span[0])
        return list(map(ExtractedQuantity.get_dict, results))
        
    def convert(self, question):
        return answer_conversion_question(question)
    
    def sent_normalizer(self, text):
        words = [self.normalizer.normalize(w) for w in text.split()]
        return hazm.sent_tokenize(' '.join(words))[0]

    def get_product_object(self, price_output):
        return {
            'product_name': '',
            'product_name_span': '',
            'product_amount': None,
            'product_unit': '',
            'price_amount': price_output['price'],
            'price_marker': price_output['price_mark'],
            'price_unit': price_output['price_unit']
        }

    # price extractor
    def price_and_unit_extractor(self, sentence):
        numbers = extract_numbers(sentence)
        span_list = []
        for num in numbers:
            span_list.append(num['span'])

        # make span lists flatten
        if len(span_list) > 0:
            span_list = list(itertools.chain.from_iterable(span_list))
            del span_list[0]
            span_list.append(-1)

        price_unit_list = []
        for i in range(0, len(span_list), 2):
            # span_list[i] and span_list[i+1] is the span between each unit tuple in whole the sentence
            findPriceUnit = re.search(
                rf"^\s*{self.PRICE_UNITS}", sentence[span_list[i]:span_list[i+1]])
            if findPriceUnit:
                price_unit_list.append({'price': numbers[i//2]['value'],
                                        'price_mark':  numbers[i//2]['marker'],
                                        'price_span': numbers[i//2]['span'],
                                        'price_unit': findPriceUnit.group().strip(),
                                        'price_unit_span': (findPriceUnit.span()[0]+span_list[i],
                                                            findPriceUnit.span()[1]+span_list[i])})
        return price_unit_list
    

    # preprocess the input sentence for removing special chars and some modifications
    def preprocess(self, input_string: str):
        input_string = re.sub("(^هر\s)", "یک ", input_string)
        input_string = re.sub("(\sهر\s)", " یک ", input_string)
        input_string = re.sub("(\sهر$)", " یک", input_string)
        input_string = re.sub("(\sساعته$)", " ساعت ", input_string)
        input_string = re.sub("(\sساعته\s)", " ساعت  ", input_string)
        input_string = re.sub("(\sروزی\s)", " یک روز ", input_string)
        input_string = re.sub("(\sماهی\s)", " یک ماه ", input_string)
        input_string = re.sub("(\sدانه ای\s)", " یک دانه ", input_string)
        input_string = re.sub("(\sکیسه ای\s)", " یک کیسه ", input_string)
        input_string = re.sub("(\sبشکه ای\s)", " یک بشکه ", input_string)
        input_string = re.sub("(\sلیتری\s)", " یک لیتر ", input_string)
        input_string = re.sub("(\sگرمی\s)", " یک گرم ", input_string)
        input_string = re.sub("(\sستی\s)", " یک ست ", input_string)
        input_string = re.sub("(\sکیلویی\s)", " یک کیلو ", input_string)
        input_string = re.sub("(\sشانه ای\s)", " یک شانه ", input_string)
        input_string = re.sub("(\sپرسی\s)", " یک پرس ", input_string)
        input_string = re.sub("(\sسهمی\s)", " یک سهم ", input_string)
        input_string = re.sub("(\sدستگاهی\s)", " یک دستگاه ", input_string)
        input_string = re.sub("(\sکلمه ای\s)", " یک کلمه ", input_string)
        input_string = re.sub("(\sنفری\s)", " یک نفر ", input_string)
        input_string = re.sub("(\sمتری\s)", " یک متر ", input_string)
        input_string = re.sub("(\sتومانی\s)", " تومان ", input_string)
        input_string = re.sub("(\sتومنی\s)", " تومان ", input_string)
        input_string = re.sub("(\sتومن\s)", " تومان ", input_string)
        input_string = re.sub("(\sدلاری\s)", " دلار ", input_string)
        input_string = re.sub("(\sریالی\s)", " ریال ", input_string)
        input_string = re.sub("(\sپوندی\s)", " پوند ", input_string)
        input_string = re.sub("(\sدونه\s)", " دانه ", input_string)
        return input_string
    
    # extracts units that come after numbers
    def custom_unit_extractor(self, input_sentence: str):
        initial_results = self.initial_extractor(input_sentence)
        results = []
        for object in initial_results:
            if object["type"].strip() in self.acceptable_types:
                results.append({k: object[k] for k in object if k in [
                            "amount", "unit", "item", "span"]})
        for object in results:
            object["amount"] = object["amount"][0]
            if int(object["amount"]) == object["amount"]:
                object["amount"] = int(object["amount"])
            if input_sentence[object['span'][0]] == ' ':
                object['span'][0] += 1
            if len(object['item']) > 0:
                object['item_span'] = []
                object['item_span'].append(object['span'][1] - len(object['item']))
                object['item_span'].append(object['span'][1])
                object['span'][1] -= (len(object['item']) + 1)
        return results

    def join_patterns(self, patterns, grouping=False):
        return '(' + ('?:' if not grouping else '') + '|'.join(patterns) + ')'


    def get_striped_span(self, re_match, sentence):
        span = list(re_match.span())
        if sentence[span[0]] == ' ':
            span[0] += 1
        if sentence[span[1]-1] == ' ':
            span[1] -= 1
        return span

    def final_extractor(self, input_string: str):
        results = []
        input_string = self.preprocess(input_string)
        price_and_unit_list = self.price_and_unit_extractor(input_string)
        # find spans before prices
        search_product_span_list = []
        for idx, data in enumerate(price_and_unit_list):
            if idx == 0:
                search_product_span_list.append(0)
                search_product_span_list.append(
                    price_and_unit_list[idx]['price_span'][0])
                continue
            search_product_span_list.append(
                price_and_unit_list[idx-1]['price_unit_span'][1])
            search_product_span_list.append(
                price_and_unit_list[idx]['price_span'][0])
        # for price outputs and call unit and product extractor
        for i in range(0, len(search_product_span_list), 2):
            product_object = self.get_product_object(price_and_unit_list[i//2])
            temp_sentence = input_string[search_product_span_list[i]:search_product_span_list[i+1]]
            founded_units = self.custom_unit_extractor(temp_sentence)
            founded_products = re.finditer(rf"(\s{self.PRODUCTS}\s)|(^{self.PRODUCTS}\s)|(^{self.PRODUCTS}$)|(\s{self.PRODUCTS}$)", temp_sentence)
            distances = []
            for unit in founded_units:
                span = unit['span']
                # to remove item from span of unit with a single space
                nearest_product = None
                nearest_product_distance = None
                for product in founded_products:
                    product_span = self.get_striped_span(product, temp_sentence)
                    if product_span[0] >= span[1] or product_span[1] <= span[0]:
                        distance = product_span[0] - \
                            span[1] if product_span[0] >= span[1] else span[0] - product_span[1]
                        if nearest_product_distance is None or distance < nearest_product_distance:
                            nearest_product_distance = distance
                            nearest_product = product
                if nearest_product is not None:
                    distances.append(
                        [unit, nearest_product, nearest_product_distance])
            final_product = None
            final_unit = None
            if len(distances) > 0:
                temp_result = distances[0]
                for item in distances[1:]:
                    if item[2] < temp_result[2]:
                        temp_result = item
                final_product = temp_result[1]
                final_unit = temp_result[0]
            else:
                temp_products = list(founded_products)
                nearest_product = None
                for product in temp_products:
                    if nearest_product is None or nearest_product.span()[1] > product.span()[1]:
                        nearest_product = product
                if nearest_product is not None:
                    final_product = nearest_product
                elif len(founded_units) > 0:
                    for unit_index in range(len(founded_units)-1, -1, -1):
                        unit = founded_units[unit_index]
                        if len(unit['item']) > 0:
                            final_unit = unit
                            break
            if final_product is None and final_unit is None:
                continue
            if final_product is not None:
                product_object['product_name'] = final_product.group().strip()
                product_object['product_name_span'] = self.get_striped_span(final_product, temp_sentence)
                product_object['product_name_span'][0] += search_product_span_list[i]
                product_object['product_name_span'][1] += search_product_span_list[i]
                if final_unit is None:
                    product_object['product_unit'] = 'عدد'
                    product_object['product_amount'] = 1
            if final_unit is not None:
                product_object['product_unit'] = final_unit['unit']
                product_object['product_amount'] = final_unit['amount']
                if final_product is None:
                    product_object['product_name'] = final_unit['item']
                    product_object['product_name_span'] = final_unit['item_span']
                    product_object['product_name_span'][0] += search_product_span_list[i]
                    product_object['product_name_span'][1] += search_product_span_list[i]
            results.append(product_object)
        return results

    def run(self, text):
        sentence = self.sent_normalizer(text)
        result = {}
        result['products_list'] = self.final_extractor(sentence)
        return result


if __name__ == '__main__':
    input_text = input()
    model = PriceAndQuantityExtraction()
    print(model.run(input_text))