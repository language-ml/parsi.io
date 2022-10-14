import stanza
import spacy_stanza
import re
import json
import pandas as pd

from spacy.tokens import Span
from spacy import displacy, load
from spacy.symbols import VERB, NOUN, AUX, ADV, ADP
from resources import MarketDictionary
from dadmatools.models.normalizer import Normalizer as N1
from hazm import Normalizer as N2
from spacy.matcher import Matcher

SYMBOL = "SYMBOL"
CORP = "CORP"
EVENT = "EVENT"
ANALYSE = "ANALYSE"
ANNOUNCE = "ANNOUNCE"
CHARACTERS = "CHARACTERS"

TRANSLATE = {
    SYMBOL: "نماد",
    CORP: "شرکت",
    EVENT: "واقعه",
    ANNOUNCE: "اعلان",
    ANALYSE: "تحلیل",
    CHARACTERS: "شخصیت",
}

class StockMarketEventExtractor():

    def __init__(self):
        self.stanza_nlp = load("./resources/stanza-spacy-model")
        ## loading market dictionary
        df = MarketDictionary.get_symbols()
        events = MarketDictionary.get_events()
        announcements = MarketDictionary.get_announcements()
        characters = MarketDictionary.get_characters()
        analyse = MarketDictionary.get_analyses()

        symbols = df["Symbol"].tolist()
        self.symbols = list(map(lambda x: x.replace(".", "\\."), symbols))

        corporations = df["Corp"].tolist()
        self.corporations = list(map(lambda x: x.replace(".", "\\."), corporations))


        ## normalizer
        self.normalizer1 = N1(
            full_cleaning=False,
            unify_chars=True,
            refine_punc_spacing=True,
            remove_extra_space=True,
            remove_puncs=False,
            remove_html=False,
            remove_stop_word=False,
            replace_email_with="<EMAIL>",
            replace_number_with=None,
            replace_url_with="<URL",
            replace_mobile_number_with="<MOBILE_NUMBER>",
            replace_emoji_with="<EMOJI>",
            replace_home_number_with="<HOME_NUMBER>",
        )
        self.normalizer2 = N2()


        ## self.matcher and patterns
        self.matcher: Matcher = Matcher(self.stanza_nlp.vocab, validate=True)

        self.add_patterns(self.matcher, events, "EVENT")
        self.add_patterns(self.matcher, analyse, "ANALYSE")
        self.add_patterns(self.matcher, announcements, "ANNOUNCE")
        self.add_patterns(self.matcher, characters, "CHARACTERS")


    ### functions
    def add_patterns(self, matcher, keywords, class_name):
        keyword_patterns = []
        r = "(ی|ای|یی|ها|هایی|های)?"
        for keyword in keywords:
            keyword_tokens = self.stanza_nlp.tokenizer(keyword)

            pre_det = ["این", "هر", "چند", "چندین", "آن", "همین", "همان", "چنین", "چنین"]
            if len(keyword_tokens) == 1:
                token1_keyword = keyword_tokens[0].text
                pattern = [
                    {"TEXT": {"IN": pre_det}, "OP": "?"},
                    {"TEXT": {"REGEX": rf"\b{token1_keyword}{r}\b"}},
                    {"TEXT": {"IN": ["ای", "ی", "ها", "های", "هایی"]}, "OP": "?"},
                ]

            elif len(keyword_tokens) == 2:
                token1_keyword = keyword_tokens[0].text
                token2_keyword = keyword_tokens[1].text
                pattern = [
                    {"TEXT": {"IN": pre_det}, "OP": "?"},
                    {"TEXT": {"REGEX": rf"\b{token1_keyword}{r}\b"}},
                    {"TEXT": {"IN": ["ای", "ی", "ها", "های", "هایی"]}, "OP": "?"},
                    {"TEXT": {"IN": pre_det}, "OP": "?"},
                    {"TEXT": {"REGEX": rf"\b{token2_keyword}{r}\b"}},
                    {"TEXT": {"IN": ["ای", "ی", "ها", "های", "هایی"]}, "OP": "?"},
                ]

            keyword_patterns.append(pattern)

        matcher.add(class_name, keyword_patterns, greedy="LONGEST")

    def convert_subtree_to_str(self, token, remove_ADP=False, is_parent=True):
        extracted_event = ""
        start = None
        end = None
        for x in token.subtree:
            if x.dep_ == "case" and start is None and is_parent:
                continue
            if x.pos == ADV:
                continue
            if remove_ADP and x.pos == ADP and is_parent:
                if x.head.text == token.text:
                    if not start is None:
                        print(
                            "WARNING ------------------> check the convert subtree to str"
                        )
                    continue

            extracted_event += str(x) + " "
            if start is None:
                start = x.idx
            end = x.idx + len(x.text)

        extracted_event = extracted_event[:-1]
        return extracted_event, start, end


    def create_output(self, OUTPUT, output_type, marker, span, **kwargs):
        persian_output_type = TRANSLATE[output_type]
        defaults = {
            "type": persian_output_type,
            "marker": marker,
            "span": span,
        }
        OUTPUT[output_type].append({**defaults, **kwargs})

        return {**defaults, **kwargs}


    def concat_tokens(self, tokens):
        concat = ""
        start = None
        end = None
        for token in tokens:
            if start is None:
                start = token.idx
            substring, s, e = self.convert_subtree_to_str(token, is_parent=False)
            end = e
            concat += substring + " "
        concat = concat[:-1]
        return concat, start, end


    def get_root_string(self, main_noun):
        left_childs = list(
            filter(lambda x: not x.dep_ in ["cop", "nsubj"], main_noun.lefts)
        )
        right_childs = list(
            filter(lambda x: not x.dep_ in ["cop", "nsubj"], main_noun.rights)
        )
        extracted_event = ""
        start = None
        end = None
        if left_childs:
            substring, s, e = concat_tokens(left_childs)
            if start is None:
                start = s
            end = e
            extracted_event += substring + " "
        extracted_event += main_noun.text
        if start is None:
            start = main_noun.idx
        end = main_noun.idx + len(main_noun.text)

        if right_childs:
            substring, s, e = concat_tokens(right_childs)
            extracted_event += " " + substring
            end = e
        return extracted_event, start, end

    def set_ents(self, symbols, corporations, doc, matcher, text):
        symbols_expression = "|".join(symbols)
        corporation_expression = "|".join(corporations)

        symbol_spans = list(
            map(
                lambda match: doc.char_span(*match.span(), label=SYMBOL),
                re.finditer(symbols_expression, text),
            )
        )

        symbol_spans = list(filter(lambda span: span is not None, symbol_spans))

        corporation_spans = list(
            map(
                lambda match: doc.char_span(*match.span(), label=CORP),
                re.finditer(corporation_expression, text),
            )
        )

        corporation_spans = list(filter(lambda span: span is not None, corporation_spans))

        term_spans = list(
            map(
                lambda match: Span(
                    doc, match[1], match[2], label=self.stanza_nlp.vocab.strings[match[0]]
                ),
                self.matcher(doc),
            )
        )

        term_spans = list(filter(lambda span: span is not None, term_spans))

        spans = symbol_spans + corporation_spans + term_spans
        doc.set_ents(spans)

        with doc.retokenize() as retokenizer:
            attrs = {"POS": "NOUN"}
            for span in symbol_spans:
                retokenizer.merge(span, attrs)

        with doc.retokenize() as retokenizer:
            attrs = {"POS": "NOUN"}
            for span in corporation_spans:
                retokenizer.merge(span, attrs)

        with doc.retokenize() as retokenizer:
            attrs = {"POS": "NOUN"}
            for span in term_spans:
                retokenizer.merge(span, attrs)

        return doc

    def find_symbols_and_corporations(self, doc, OUTPUT):
        symbol_ents = list(filter(lambda ent: ent.label_ == SYMBOL, doc.ents))

        for symbol_ent in symbol_ents:
            token = symbol_ent[0]
            start = token.idx
            end = token.idx + len(token.text)
            self.create_output(OUTPUT, SYMBOL, token.text, (start, end))

        corporation_ents = list(filter(lambda ent: ent.label_ == CORP, doc.ents))

        for corporation_ent in corporation_ents:
            token = corporation_ent[0]
            start = token.idx
            end = token.idx + len(token.text)
            self.create_output(OUTPUT, CORP, token.text, (start, end))

    def find_events(self, doc, OUTPUT):
        term_ents = list(filter(lambda ent: ent.label_ not in [SYMBOL, CORP], doc.ents))

        for term_ent in term_ents:
            token = term_ent[0]
            if token.dep_ == "compound:lvc":
                if token.head.pos == VERB:
                    subject = None
                    for child in token.head.children:
                        if child.dep_ == "nsubj":
                            subject, start_subj, end_subj = self.convert_subtree_to_str(child)
                            break
                        else:
                            print("NOT IMP - child dep is: ", child.dep_)
                            pass
                    else:
                        print("didn't found any subj")
                        pass

                    token_string, start, end = self.convert_subtree_to_str(token)
                    end = token.head.idx + len(token.head.text)
                    extracted_event = token_string + " " + token.head.text
                    if subject:
                        self.create_output(
                            OUTPUT,
                            token.ent_type_,
                            extracted_event,
                            (start, end),
                            subject=subject,
                            span_subject=(start_subj, end_subj),
                        )
                    else:
                        self.create_output(
                            OUTPUT, token.ent_type_, extracted_event, (start, end)
                        )
                else:
                    extracted_event, start, end = self.convert_subtree_to_str(token)
                    self.create_output(OUTPUT, token.ent_type_, extracted_event, (start, end))

            elif token.dep_ == "nmod" or token.dep_ == "amod":
                main_noun = token
                while (
                    main_noun.dep_ == "nmod" or main_noun.dep_ == "amod"
                ) and main_noun.head.pos == NOUN:
                    main_noun = main_noun.head
                if main_noun.pos != NOUN:
                    print("WARNING ------------------> check code in else: dep = nmod amod")
                    continue

                if main_noun.dep_ == "root":
                    children = list(main_noun.children)
                    for child in children:
                        if child.dep_ == "cop" and child.pos == AUX:
                            extracted_event, start, end = self.get_root_string(main_noun)
                            self.create_output(
                                OUTPUT, token.ent_type_, extracted_event, (start, end)
                            )
                            break
                    else:
                        # TODO: this is of no use
                        extracted_event, start, end = self.get_root_string(main_noun)
                        self.create_output(
                            OUTPUT, token.ent_type_, extracted_event, (start, end)
                        )

                else:
                    extracted_event, start, end = self.convert_subtree_to_str(
                        main_noun, remove_ADP=True
                    )
                    self.create_output(OUTPUT, token.ent_type_, extracted_event, (start, end))

            elif token.dep_ == "root":
                extracted_event, start, end = self.get_root_string(token)
                self.create_output(OUTPUT, token.ent_type_, extracted_event, (start, end))

            else:
                extracted_event, start, end = self.convert_subtree_to_str(token, remove_ADP=True)
                self.create_output(OUTPUT, token.ent_type_, extracted_event, (start, end))


    def has_intersection(self, first, second):
        if first[0] < second[0]:
            if first[1] < second[0]:
                return False
            else:
                return True
        else:
            if first[0] > second[1]:
                return False
            else:
                return True


    def combine(self, first, second, text):
        start = min(first["span"][0], second["span"][0])
        end = max(first["span"][1], second["span"][1])
        new_span = (start, end)
        new_marker = text[start:end]
        return new_span, new_marker


    def remove_type_overlap(self, match_list, text):
        n = len(match_list)
        if n == 0:
            return []
        i = 0
        j = 1
        while i < n and j < n:
            first = match_list[i]
            second = match_list[j]
            if self.has_intersection(first["span"], second["span"]):
                new_span, new_marker = combine(first, second, text)
                match_list[i]["span"] = new_span
                match_list[i]["marker"] = new_marker
                match_list[j] = None
            else:
                i = j
            j += 1

        match_list = list(filter(lambda x: not x is None, match_list))
        return match_list


    def remove_span_overlap(self, OUTPUT, text):
        for key in OUTPUT.keys():
            OUTPUT[key] = self.remove_type_overlap(OUTPUT[key], text)
        return OUTPUT


    def print_output(self, OUTPUT, text):
        for key in OUTPUT.keys():
            for o in OUTPUT[key]:
                print(json.dumps(o, ensure_ascii=False, indent=2))


    def run(self, *texts):
        for text_index, text in enumerate(texts):
            OUTPUT = {
                SYMBOL: [],
                CORP: [],
                EVENT: [],
                ANNOUNCE: [],
                ANALYSE: [],
                CHARACTERS: [],
            }

            text = self.normalizer1.normalize(text)
            text = self.normalizer2.normalize(text)

            print(
                f"---------------------------- input {text_index}----------------------------------------------"
            )
            print(f"Normalized input: {text}")

            doc = self.stanza_nlp(text)

            doc = self.set_ents(self.symbols, self.corporations, doc, self.matcher, text)

            self.find_symbols_and_corporations(doc, OUTPUT)

            self.find_events(doc, OUTPUT)

            OUTPUT = self.remove_span_overlap(OUTPUT, text)
            self.print_output(OUTPUT, text)

