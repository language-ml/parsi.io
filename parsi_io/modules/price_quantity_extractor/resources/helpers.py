from .unit_extractor import *
from .number_extractor import *
import hazm
import nltk


class ExtractedQuantity:

    def __init__(self, qtype, amount, unit, item, marker, span, SI_amount, SI_unit):
        self.qtype = qtype
        self.amount = amount
        self.unit = unit
        self.item = item
        self.marker = marker
        self.span = span
        self.SI_amount = SI_amount
        self.SI_unit = SI_unit

    def get_dict(self):
        return {
            'type': self.qtype,
            'amount': self.amount,
            'unit': self.unit,
            'item': self.item,
            'marker': self.marker,
            'span': self.span,
            'SI_amount': self.SI_amount,
            'SI_unit': self.SI_unit,
        }


WS = WHITE_SPACE
NUM_CONNECTOR = join_patterns([rf'({WS})?(?:،|,)({WS})?', rf'{WS}و{WS}'])
NUM_SEQUENCE = rf'{NUM_IN_TEXT}(?:{NUM_CONNECTOR}{NUM_IN_TEXT})*'
NUM_UNIT = rf'{NUM_SEQUENCE}{WHITE_SPACE}{COMPLEX_UNIT}'

def extract_expressions(text, tagger, chunker, related_words_dict):

    def get_nth_chunk(text, n, tagger, chunker):
        tagged = tagger.tag(hazm.word_tokenize(text))
        chunks = chunker.parse(tagged)
        if len(chunks) > 0:
            return ' '.join([c[0] for c in chunks[n]])
        return ''
    
    result = []
    for match in re.finditer(NUM_UNIT, text):
        before_index = match.span()[0] - 1
        after_index = match.span()[1]
        if before_index >= 0 and re.match('\w', text[before_index]):
            continue
        if after_index < len(text) and re.match('\w', text[after_index]):
            continue
        before = text[:match.span()[0] - 1]
        after = text[match.span()[1]:]
        before_chunk = get_nth_chunk(before, -1, tagger, chunker)
        after_chunk = get_nth_chunk(after, 0, tagger, chunker)

        unit = extract_units(match.group())[0]
        quantity = unit_to_quantity(unit['object'])[0]
        numbers = extract_numbers(match.group())
        related_words = related_words_dict.get(quantity, [])
        pattern = join_patterns(related_words)

        before_matches = [matched for matched in re.finditer(pattern, before_chunk)]
        before_match = None
        span = list(match.span())
        did_preextend = False
        did_postextend = False
        if before_matches:
            before_match = before_matches[-1]
            span[0] = match.span()[0] - len(before_chunk) + before_match.span()[0] - 1
            did_preextend = True
        if not did_preextend:
            after_matches = [matched for matched in re.finditer(pattern, after_chunk)]
            after_match = None
            if after_matches:
                after_match = after_matches[0]
                span[1] = match.span()[1] + after_match.span()[1] + 1
                did_postextend = True

        item_word = ''
        if not did_postextend:
            tags = tagger.tag(hazm.word_tokenize(after_chunk))
            if tags and tags[0][1].startswith('N'):
                if len(tags) < 2 or not tags[1][1].startswith('V'):
                    item_word = tags[0][0]
                    item_match = re.search(item_word, after_chunk)
                    span[1] = match.span()[1] + item_match.span()[1] + 1
        
        res_amount = [item['value'] for item in numbers]
        SI_equiv = unit_to_SI_unit(unit['object'])
        SI_unit = str(SI_equiv.units)
        SI_coeff = SI_equiv.magnitude
        SI_amount = [SI_coeff * item for item in res_amount]
        marker = text[span[0]:span[1]]
        unit_str = unit['marker']

        result.append(
            ExtractedQuantity(
                quantity, 
                res_amount, 
                unit_str, 
                item_word, 
                marker, 
                span, 
                SI_amount, 
                SI_unit))
    return result

def tree_generator(sentence):
    grammar = r"""
        NADJ: {<N|Ne><ADV>*<AJ|AJe|ADV>}
    """
    return nltk.RegexpParser(grammar).parse(sentence)

def extract_qualitative_expressions(text, tagger, quantities_word_network):
    results = []
    for sentence in hazm.sent_tokenize(text):
        tags = tagger.tag(hazm.word_tokenize(sentence))
        tree = tree_generator(tags)
        last_index = 0
        for subtree in tree.subtrees():
            if subtree.label() == 'NADJ':
                try:
                    in_context_POS = subtree.leaves()[-1][1]
                    out_of_context_POS = tagger.tag([subtree.leaves()[-1][0]])[0][1]
                    if in_context_POS.startswith("ADV") and out_of_context_POS.startswith("ADV"):
                        continue
                    try:
                        quantity = quantities_word_network[subtree.leaves()[0][0]]
                    except KeyError:
                        y_count = -1
                        while subtree.leaves()[0][0][y_count] == 'ی':
                            y_count -= 1
                        if y_count == -1:
                            continue
                        quantity = quantities_word_network[subtree.leaves()[0][0][:y_count + 1]]
                    marker = ' '.join([s[0] for s in subtree.leaves()])
                    span = re.search(marker, text[last_index:]).span()
                    span = [span[0] + last_index, span[1] + last_index]
                    last_index = span[1]

                    SI_unit = quantity_to_SI_unit(quantity)
                    results.append(
                        ExtractedQuantity(
                            quantity, 
                            '', 
                            '', 
                            '', 
                            marker, 
                            span, 
                            '', 
                            SI_unit))
                except KeyError:
                    pass
    return results