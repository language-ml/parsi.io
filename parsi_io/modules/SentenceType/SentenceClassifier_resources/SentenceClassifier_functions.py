# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from hazm import *

import codecs
import re
import copy
import math


resources_path =  __file__.split('SentenceClassifier_functions.py')[0]

class _PersianSentenceType:
    QUESTION_MARK = '؟'
    UNDERLINE_MARK = '_'

    def __init__(self, vps, sentence):
        self.relational_phrases = None
        self.query_phrases_no_mark = None
        self.query_phrases = None
        self.imperative_verbs = None
        self.vps = vps
        self.sentence = sentence
        self.lemmatizer = Lemmatizer()
        self.load_data()
        self.relational_phrase_exists = False
        self.relational_phrase_start = None

    def load_data(self):
        self.imperative_verbs = set(verb.strip() for verb in codecs.open(resources_path+'imperative_verb.txt', encoding='utf-8', mode='rU').readlines())
        self.query_phrases = set(phrase.strip() for phrase in codecs.open(resources_path+'Query_phrases.txt', encoding='utf-8', mode='rU').readlines())
        self.query_phrases_no_mark = set(phrase.strip() for phrase in codecs.open(resources_path+'Query_phrases_no_mark.txt', encoding='utf-8',mode='rU').readlines())
        self.relational_phrases = set(phrase.strip() for phrase in codecs.open(resources_path+'relational_phrases.txt', encoding='utf-8', mode='rU').readlines())

    def remove_relational_phrase_from_vp(self, verb):
        if not self.relational_phrase_exists:
            return verb
        for rel in self.relational_phrases:
            verb = re.sub(pattern=f'(\s{rel}$)', string=verb, repl='')
        return verb
    

    def find_relational_phrase(self, end_sent):
        min_ind = math.inf
        for rel in self.relational_phrases:
            relation_loc = re.search(f'(^{rel}\s)|(\s{rel}\s)', self.sentence)
            if relation_loc is not None:
                if relation_loc.start() < end_sent:
                    min_ind = min(min_ind, relation_loc.start())
        if min_ind != math.inf:
            self.relational_phrase_exists = True
            self.relational_phrase_start = min_ind
            
class _PersianQuerySentenceDetector(_PersianSentenceType):
    def __init__(self, vps, sentence):
        super().__init__(vps, sentence)
        self.question_mark_exists = False
        self.question_mark_start = None
        self.query_phrase_exists = False
        self.query_phrase_start = 0


    def find_query_phrase_start(self):
        self.query_phrase_exists = True
        for phrase in self.query_phrases:
            phrase_loc = re.search(f'(^{phrase}\s)|(\s{phrase}\s)|(\s{phrase}\?)', self.sentence)
            if phrase_loc is not None:
                if phrase_loc.start() < self.question_mark_start:
                    self.query_phrase_start = phrase_loc.start()

    def find_query_phrases_no_question_mark(self):
        for phrase in self.query_phrases_no_mark:
            phrase_loc = re.search(f'(^{phrase}\s)|(\s{phrase}\s)|(\s{phrase})', self.sentence)
            if phrase_loc is not None:
                self.query_phrase_exists = True
                self.query_phrase_start = phrase_loc.start()
                break
        else:
            self.query_phrase_exists = False
            self.query_phrase_start = None

    def find_candidate_verbs(self):
        candidate = []
        for vp in self.vps:
            vp_loc = re.search(f'(^{vp}\s)|(\s{vp}\s)|(\s{vp}.?$)', self.sentence)
            if vp_loc is None:
                vp_loc = re.search(vp, self.sentence)
            if self.query_phrase_start <= vp_loc.start() < self.question_mark_start and vp not in ['باید']:
                candidate.append(self.remove_relational_phrase_from_vp(vp))

        if len(candidate) == 0:
            for vp in reversed(self.vps):
                vp_start = re.search(vp, self.sentence).start()
                if vp_start < self.question_mark_start:
                    return self.remove_relational_phrase_from_vp(vp)

        elif len(candidate) == 1:
            return candidate[0]
        else:
            if not self.relational_phrase_exists:
                return ' '.join(candidate)

            vps_before_relation = [vp for vp in candidate if
                                   re.search(vp, self.sentence).start() < self.relational_phrase_start]
            if len(vps_before_relation) != 0:
                return ' '.join(vps_before_relation)
            return candidate[-1]

    def query_sen(self):
        if _PersianSentenceType.QUESTION_MARK in self.sentence:
            self.question_mark_exists = True
            self.question_mark_start = re.search(_PersianSentenceType.QUESTION_MARK, self.sentence).start()
            self.find_query_phrase_start()
            self.find_relational_phrase(end_sent=self.question_mark_start)
            candidate_verb = self.find_candidate_verbs()
            return True, candidate_verb
        else:
            self.question_mark_start = len(self.sentence) - 1
            self.find_query_phrases_no_question_mark()
            if not self.query_phrase_exists:
                return False, None

            self.find_relational_phrase(end_sent=len(self.sentence) - 1)
            candidate_verb = self.find_candidate_verbs()
            return True, candidate_verb

            

class _ImperativeVerbDetectorRes:
    def __init__(self, imperative, positive, original_verb):
        self.imperative = imperative
        self.positive = positive
        self.original_verb = original_verb

    def is_imperative(self):
        return self.imperative

    def is_positive(self):
        return self.positive

    def group(self):
        return self.original_verb

class _PersianImperativeSentenceDetector(_PersianSentenceType):
    
    def __init__(self, vps, sentence):
        super().__init__(vps, sentence)


    def __normalize_imperative_verb(self, verb):
        normalize_verbs = [verb]
        pattern = re.compile('^[ب|ن|م]')
        if pattern.match(verb):
            norm_verb = verb
            if norm_verb.endswith('ید'):
                norm_verb = norm_verb[:-2]
            if norm_verb.endswith('ی'):
                normalize_verbs.append(copy.deepcopy(norm_verb))
                norm_verb = norm_verb[:-1]
            elif norm_verb.endswith('ئ'):
                normalize_verbs.append(copy.deepcopy(norm_verb))
                norm_verb = norm_verb[:-1]
                
            if norm_verb.startswith('ی'):
                norm_verb = norm_verb[1:]
            if norm_verb.startswith('ن'):
                normalize_verbs.append(copy.deepcopy(norm_verb))
            norm_verb = norm_verb[1:]
            if norm_verb[0] == 'ا':
                norm_verb = f'آ{norm_verb[1:]}'
            normalize_verbs.append(norm_verb)
        elif verb.endswith('ید'):
            normalize_verbs.append(verb[:-2])
        return normalize_verbs

    def __detect_verb_type(self, target_verb, verb_lem, original_verb):
        if target_verb.startswith('نن') and not verb_lem.startswith('نن'):
            return _ImperativeVerbDetectorRes(imperative=True, positive=False, original_verb=original_verb)
        elif target_verb.startswith('م') and not verb_lem.startswith('م'):
            return _ImperativeVerbDetectorRes(imperative=True, positive=False, original_verb=original_verb)
        elif target_verb.startswith('ن') and not verb_lem.startswith('ن'):
            return _ImperativeVerbDetectorRes(imperative=True, positive=False, original_verb=original_verb)
        else:
            return _ImperativeVerbDetectorRes(imperative=True, positive=True, original_verb=original_verb)

    def is_verb_imperative(self, vp):
        original_verb = vp
        target_verb = vp.split()[-1]
        verb_lem = self.lemmatizer.lemmatize(target_verb).split('#')
        if len(verb_lem) > 1:
            verb_lem = verb_lem[1]
        if verb_lem == 'است':
            return _ImperativeVerbDetectorRes(imperative=False, positive=None, original_verb=original_verb)

        if target_verb in self.imperative_verbs:
            return _ImperativeVerbDetectorRes(imperative=True, positive=True, original_verb=original_verb)

        for verb_norm in self.__normalize_imperative_verb(target_verb):
            if verb_lem == verb_norm:
                return self.__detect_verb_type(target_verb, verb_lem, original_verb)

        return _ImperativeVerbDetectorRes(imperative=False, positive=None, original_verb=original_verb)

    def find_candidate_verbs(self):
        candidate = []
        for vp in self.vps:
            vp_loc = re.search(f'(^{vp}\s)|(\s{vp}\s)|(\s{vp}.?$)', self.sentence)
            if vp_loc is None:
                vp_loc = re.search(vp, self.sentence)
            if vp_loc.start() <= self.relational_phrase_start:
                res = self.is_verb_imperative(vp)
                if res.is_imperative() and vp not in ['باید']:
                    candidate.append(res)
                else:
                    return []
        if len(candidate) == 0:
            res = self.is_verb_imperative(self.vps[-1])
            if res.is_imperative():
                return [res]
        return candidate

    def imperative_sen(self):
        self.find_relational_phrase(end_sent=len(self.sentence) - 1)
        if not self.relational_phrase_exists:
            for vp in self.vps:
                res = self.is_verb_imperative(vp)
                if not res.is_imperative():
                    return False, None, None
            self.relational_phrase_start = len(self.sentence) - 1

        candidate = self.find_candidate_verbs()
        if len(candidate) == 0:
            return False, None, None
        return True, candidate[-1].is_positive(), ' '.join([i.group() for i in candidate])
    
    
class _PersianOtherSentenceDetector(_PersianSentenceType):
    def __init__(self, vps, sentence):
        super().__init__(vps, sentence)

    def find_candidate_verbs(self):
        candidate = []
        for vp in self.vps:
            vp_loc = re.search(f'(^{vp}\s)|(\s{vp}\s)|(\s{vp}.?$)', self.sentence)
            if vp_loc is None:
                vp_loc = re.search(vp, self.sentence).start()

            if vp_loc.start() <= self.relational_phrase_start and vp not in ['باید']:
                candidate.append(self.remove_relational_phrase_from_vp(vp))

        if len(candidate) == 0:
            return [self.vps[-1]]

        return candidate

    def main_verb(self):
        if len(self.vps) == 0:
            return "هیچ فعلی شناسایی نشد"

        self.find_relational_phrase(end_sent=len(self.sentence) - 1)
        if not self.relational_phrase_exists:
            return ' '.join(self.vps)

        return ' '.join(self.find_candidate_verbs())


            
        
class SentenceClassifier:
      
    def __init__(self):
        
        self.tagger = POSTagger(model=resources_path+'postagger.model')
        self.chunker = Chunker(model=resources_path+'chunker.model')
        
    def _extract_vps(self, sentence):
        tokens = word_tokenize(sentence)
        tags = self.tagger.tag(tokens)
        tag_words = tree2brackets(self.chunker.parse(tags))
        vps = re.findall('\[[^\]]* VP\]', tag_words)
        for i in range(len(vps)):
            vps[i] = vps[i][1:-4].strip()
            vps[i] = vps[i].replace(_PersianSentenceType.UNDERLINE_MARK, ' ')
        return vps

    def run(self, sentence):
        vps = self._extract_vps(sentence)
        query_detector = _PersianQuerySentenceDetector(vps=vps, sentence=sentence)
        is_query, vp = query_detector.query_sen()
        if is_query:
            return { 'type':'پرسشی','verb':  vp}
        imperative_detector = _PersianImperativeSentenceDetector(vps=vps, sentence=sentence)
        is_imperative, is_positive, vp = imperative_detector.imperative_sen()
        if is_imperative:
            if is_positive:
                return { 'type':'امری مثبت','verb':  vp} 
            return { 'type':'امری منفی','verb':  vp}

        other_detector = _PersianOtherSentenceDetector(vps=vps, sentence=sentence)
        vp = other_detector.main_verb()
        return { 'type':'سایر','verb':  vp}



    


            
            
          
'''
how to use:
    sent_detector = SentenceClassifier()
    sentences = list(sent.strip() for sent in codecs.open('./sentences.txt', encoding='utf-8', mode='rU').readlines())
    counter = 1
    for sent in sentences:
        result = sent_detector.run(sent)
        print(f'sentence {counter} : {sent}')
        print('type : {s_type}'.format(s_type = result["type"]))
        print('verb : {s_verb}'.format(s_verb  =result["verb"]))
        print('*------------*------------*------------*------------*------------*------------*------------*------------*')
        counter = counter + 1
'''
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
