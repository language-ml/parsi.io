import logging
import re
import os
import hazm
import nltk
import functools
import operator
from zeep import Client
from requests.auth import HTTPBasicAuth
from requests import Session
from zeep.transports import Transport
import re
from hazm import *
import os
import gdown
from parstdex import Parstdex
from parsi_io.modules.number_extractor import NumberExtractor
from parsi_io.modules.cause_effect_extractions import CauseEffectExtraction
from parsi_io.constants import postagger_path
from pathlib import Path


class Utils:

  def __init__(self, username="", token=""):
    self.base_dir = Path(os.getcwd()) / "parsi_io"
    self.wsdl_sense_service = 'http://nlp.sbu.ac.ir:8180/WebAPI/services/SenseService?WSDL'
    self.wsdl_synset_service = 'http://nlp.sbu.ac.ir:8180/WebAPI/services/SynsetService?WSDL'
    self.time_extractor = Parstdex()
    self.check_pos_tag(postagger_path)
    self.names, self.places = self.load_files()
    self.live_patterns = self.names + ["من", "تو", "او", "ما", "شما", "آن ها", "آنها", "دوست", "رفیق", "همسایه", "همکار", "دشمن"]
    self.normalizer = hazm.Normalizer()
    self.use_farsnet = False
    if username != "" and token != "":
      try:
        self.create_farsnet_session(username, token)
        self.use_farsnet = True
        self.token = token
        self.username = username
      except Exception:
        print("could not connect to farsnet")

    self.questionable_poses = {
    'MOTAMEMI': {'pos_hint_word': 'Noun', 'pos_hint_expression': ['N', 'Ne', 'AJ', 'AJe']},
    'MAFOULI': {'pos_hint_word': 'Noun', 'pos_hint_expression': ['N', 'Ne']},
    'NAHADI': {'pos_hint_word': 'Noun', 'pos_hint_expression': ['N', 'Ne']},
    'GHEIDI': {'pos_hint_word': 'Adverb', 'pos_hint_expression': ['ADV']},
    'ADAD': {'pos_hint_expression': ['NUM']}}
    self.LINKING_VERBS = {'است', 'بود', 'شد', 'گشت', 'گردید', 'هست'}

  def create_farsnet_session(self, username, token):
      # connecting client
    session = Session()
    session.auth = HTTPBasicAuth(username, token)
    self.client_sense = Client(self.wsdl_sense_service, transport=Transport(session=session))
    self.client_synset = Client(self.wsdl_synset_service, transport=Transport(session=session))

  def extract_structures(self, sentence):
    neutral_words = r"N|Ne|PRO|PROe"
    grammar = r"""
      MOTAMEMI:  {<P|Pe><N|Ne>(<CONJ>?<N|Ne|AJ|AJe>)*}
      MAFOULI:   {<N|Ne><POSTP>}
      NAHADI:    {<DET>?<NW>((<CONJ><NW>)|<AJe|AJ>)*}
      GHEIDI:    {<ADV>+}
      ADAD:      {<NUM>+}
    """
    grammar = grammar.replace('NW', neutral_words)
    cp = nltk.RegexpParser(grammar)
    return cp.parse(sentence)

  def get_sense(self, word):
    word = hazm.Lemmatizer().lemmatize(word)
    request = {"searchKeyword": word, "userKey": self.token, "searchStyle": "EXACT"}
    sense = self.client_sense.service.getSensesByWord(**request)
    return sense


  def get_synset(self, word):
    word = hazm.Lemmatizer().lemmatize(word)
    request = {"searchKeyword": word, "userKey": self.token, "searchStyle": "EXACT"}
    sense = self.client_synset.service.getSynsetsByWord(**request)
    return sense

  def is_linking_verb(self, verb):
    verb = set(hazm.Lemmatizer().lemmatize(verb).split('#'))
    return bool(self.LINKING_VERBS.intersection(verb))

  def is_linking_sentence(self, sentence_tokens):
    words = self.tagger.tag(sentence_tokens)
    verb_types = map(self.is_linking_verb, map(lambda x: x[0], filter(lambda x: x[1] == 'V', words)))
    return functools.reduce(operator.or_, verb_types, False)

  def get_question_word(self, expression, pos_hint_word=[], pos_hint_expression=[]):
    expression = hazm.Normalizer().normalize(expression)
    words = hazm.word_tokenize(expression)
    if len(words) == 1:
        word = words[0]

        if 'NUM' in pos_hint_expression:
            return 'چند'

        # extracting sense and pos
        senses = self.get_sense(word)
        if not senses:
            return 'چه'
        if pos_hint_word:
            senses_f = list(filter(lambda sense: sense['word']['pos'] == pos_hint_word, senses))
            if senses_f:
                senses = senses_f
        poses = list(map(lambda sense: sense['word']['pos'], senses))
        sense = senses[0]
        pos = sense['word']['pos']

        # extracting semantics and synset
        synsets = self.get_synset(word)
        if not synsets:
            return 'چه'
        if pos_hint_expression:
            synsets_f = list(filter(lambda synset: synset['pos'] == pos_hint_word, synsets))
            if synsets_f:
                synsets = synsets_f
        semantics = list(map(lambda synset: synset['pos'], synsets))
        synset = synsets[0]
        semantic = synset['semanticCategory']

        # decide how to generate qusition word based on its POS
        if pos == 'Adverb':
            if semantic in ['TIME', 'زمان']:
                return 'چه زمانی'
            return 'چگونه'
        elif pos == 'Noun':
            noun_specifity_type = sense['nounSpecifityType']
            if noun_specifity_type == 'Human':
                return 'چه کسی'
            elif noun_specifity_type == 'Animal':
                return 'چه جانوری'
            elif noun_specifity_type == 'Place':
                return 'کجا'
            elif noun_specifity_type == 'Time' or semantic in ['TIME', 'زمان']:
                return 'چه زمانی'
            else:
                return 'چه چیز'
        elif pos == 'Adjective':
            if 'QUANTITY' in semantics:
                return 'چند'
            return 'چگونه'
        else:
            return 'چه'

    elif len(words) > 1 and pos_hint_expression:
        words = list(filter(lambda word: word[1] in pos_hint_expression, self.tagger.tag(words)))
        if not words:
            return 'چه'
        return self.get_question_word(words[0][0], pos_hint_word=pos_hint_word)
    else:
        return 'چه'

  def extract_time(self, text):
    result = self.time_extractor.extract_marker(text)
    return result

  def check_pos_tag(self, pos_filename):
    if not os.path.exists(pos_filename):
      logging.info('pos tagger could not be found at the current directory, downloading ...')
      gid = '1rcKIMKdjpmAjAv8OzvwdpwpanzaMJ4X6'
      gdown.download(id=gid, output=pos_filename)
    self.tagger = POSTagger(model=pos_filename, ouput=pos_filename)

  def load_files(self):
    # file to find root of a verb
    # with open('verb_to_bon.json', encoding='utf-8') as f:
    #   v_to_thirdperson = json.load(f)
    # file containing persian names
    with open(str(self.base_dir / "resources" /'farsi_names.sql')) as f:
      names = [eval(line.rstrip('\n').split(",")[1]) for line in f]
    # file containing name of places/locations
    with open(str(self.base_dir / "resources" / 'places.txt')) as f:
      places = f.read().split("|")
    return names, places

  def check_live_noun(self, text):
      text_arr = text.split()
      for t in text_arr:
          if t in self.live_patterns:
              return True
      return False
  
  def check_place(self, text):
      if text in self.places:
          return True
      return False

  def sentence_clean(self, sentence: str):
      sentence = self.normalizer.normalize(sentence)
      return sentence.split('. ')


class QuestionGeneration:

  def __init__(self, farsnet_user="", farsnet_token=""):
    self.utils = Utils(farsnet_user, farsnet_token)
    self.all_regexes = {
      "چرایی": {"regex": r"""(?P<effect>.*)[،|؛|](?P<reason> زیرا| چون| به‌دلیل| بدلیل|چون\sکه | به\sدلیل\sاینکه)(?P<cause>.*)|چون(?P<cause2>.*)(،|\s،|؛)(?P<effect2>.*)""", "q_as": [{"question": "چرا {effect} ؟", "answer": "زیرا {cause}"}]}, 
      "سببی": {"regex": r"(?P<effect>.*) (?P<reason>مسبب|دلیل|مسبّب) (?P<cause>.*) [است|شد|شدند]|(?P<reason2>مسبب|دلیل) (?P<effect2>.*)[،|؛] (?P<cause2>) است.", "q_as": [{"question": "{effect} باعث چه می شود؟ ", "answer": "باعث {cause}"}, {"question": "چه باعث  {cause} می‌شود?", "answer": "{effect}"}]},
      "موجب": {"regex":r"(?P<effect>.*) موجب (?P<cause>.*) می‌شود.*|(?P<effect2>.*) موجبات (?P<cause2>.*) فراهم می‌کند","q_as": [{ "question": "چه موجب {effect} می‌شود؟", "answer": "{cause}"}, {"question": "{cause} موچب چه می‌شود؟", "answer": "موجب {effect}"}]},
      "ترین": {"regex":r"(?P<tarin>.*ترین) (?P<cause>.*)[،|؛](?P<effect>.*) است", "q_as": [{"question": "{tarin} {cause} چیست؟", "answer": "{effect}"}]},
      "خاطر": {"regex": r"""(?P<reason> بخاطر|به خاطر) (?P<cause>.*)[،|] (?P<effect>.*)|(?P<effect2>.*) (?P<reason2> بخاطر|به خاطر) (?P<cause2>.*)""","q_as": [{ "question": "چرا {effect} ؟", "answer": "به خاطر {cause}"}]},
      "منجر": {"regex": r"(?P<cause>.*)(?P<reason> منجر به)(?P<effect>.*)می شود.|(?P<reason2>مسبب|دلیل) (?P<effect2>.*)[،|؛] (?P<cause2>) است.", "q_as": [{"question": "علت {effect} چیست؟", "answer": "{cause}"}]},
      "هدف": {"regex":r"هدف (?P<effect>.*) (?P<reason>این\sاست\sکه|این\sاست) (?P<cause>.*)", "q_as": [{"question": "هدف {effect} چیست؟", "answer": "{cause}"}]},
      "تا": {"regex":r"(?P<effect>.*) (?P<reason>تا) (?P<cause>.*)", "q_as": [{ "question": "چرا {effect} ?", "answer": "{cause}"}]},
      "علت": {"regex": r"(?P<reason>علت) (?P<effect>.*)[،|؛] (?P<cause>.*) است", "q_as": [{ "question": "علت {effect} چیست؟", "answer": "{cause}"}]},
      "نتیجه": {"regex": r"(?P<effect>.*) (?P<reason>نتیجه‌ی|نتیجه\sی) (?P<cause>.*) [است|هستند]", "q_as": [{ "question": "{effect} نتیجه‌ی چیست؟", "answer": "{cause}"}]}
    }
    self.cause_effect_extractor_keys = ["تا", ]


  # write methods here, each method extracts a list of questions, write preprocessing in Utils class if needed, a question mark at the end
  def transitive_verbs(self, text):
    text = text.replace("\u200c", " ")
    result = []
    regexes = re.finditer(r"\sرا\s", text)
    prev_e = 0
    for regex in regexes:
        s, e = regex.start(), regex.end()
        text_arr = text.split()
        index_of_ra = text_arr.index("را", prev_e)
        prev_e = index_of_ra + 1
        A = text_arr[index_of_ra-1]
        # check live and not live subject
        live_or_not = self.utils.check_live_noun(A)
        if live_or_not:
            live_vs_not = " چه کسی را "
        else:
            live_vs_not = " چه چیزی/کسی را "
        Q = " ".join(text_arr[:index_of_ra-1]) + live_vs_not + text[e:-1] + "؟"  
        result.append({"Question": Q, "Answer": A})
    return result


  def esnadi_verbs(self, text):
    text = text.replace("\u200c", " ")
    result = []
    regexes = re.finditer(r"(است|بود|شد|گشت|گردید|هست|نیست|بود|باشد|باد|شود|می شود|شده است)(م|ی|یم|ید|ند|\s)", text)
    for regex in regexes:
        s, e = regex.start(), regex.end()
        Q = " ".join(text[:e].split()[:-2]) + " چگونه " + text[s:e].strip() + "؟"
        A = text
        result.append({"Question": Q, "Answer": A})
    return result


  def validate_ta_regex(self, text, key):
    effect_extractor = CauseEffectExtraction()
    result = effect_extractor.run(text)
    if not result[1] is None:
      return result[1] == key
    return False

  def get_all_not_none_groups(self, x):
    group_dicts = x.groupdict()
    groups = {}
    for key, value in group_dicts.items():
      if value:
        if key == "cause2" or key == "effect2" or key == "reason2":
          groups[key[:-1]] = value
        else:
          groups[key] = value
    if (not "cause" in groups.keys()) or (not "effect" in groups.keys()):
      print("bad input")
      return None # cause and effect shouldn't be empty
    return groups
  def prepositional_verbs(self, text):
    text = text.replace("\u200c", " ")
    result = []
    regexes = re.finditer(r"\s(از|به|با|در|برای)\s", text)
    for regex in regexes:
        s, e = regex.start(), regex.end()
        # check live and not live subject
        A = text[e:].split()[0]
        live_or_not = self.utils.check_live_noun(A)
        place = self.utils.check_place(A)
        if live_or_not:
            live_vs_not = "چه کسی "
        elif place:
            live_vs_not = "کجا "
        else:
            live_vs_not = "چه چیزی "
        Q = text[:e] + live_vs_not + " ".join(text[e:-1].split()[1:]) + "؟"
        result.append({"Question": Q, "Answer": A})
    return result

  
  def do_questions(self, text):
      result = []
      regexes = re.finditer(r"\s(زیرا|چون|چرا که|به این دلیل که)\s", text)
      s = -1
      for regex in regexes:
          s, e = regex.start(), regex.end()

      pos_tags = self.utils.tagger.tag(word_tokenize(text))
      text = text.replace("\u200c", " ")
      for word, tag in pos_tags:
          if tag == 'V':
              # check pos or neg
              if word[0] == "ن":
                  A = "خیر."
                  index_of_n = text.find(word)
                  new_text = ""
                  # remove n
                  for i, c in enumerate(text):
                      if i != index_of_n:
                          new_text += c
                  text = new_text
              else:
                  A = "بله."
              # check if there is a describtion after verb
              if text.find(word) < s:
                  Q = "آیا " + text[:s].strip() + "؟"
                  A += text[s:]
              else:
                  Q = "آیا " + text[:-1] + "؟"

              result.append({"Question": Q, "Answer": A})
              break
      return result


  def including_keywords(self, text):
      text = text.replace("\u200c", " ")
      text = text[:-1] if text[-1] is '.' else text
      result = []
      regexes = re.finditer(r"\s(باعث|عامل|دلیل|برهان|موجب)\s", text)
      for regex in regexes:
          s, e = regex.start(), regex.end()
          A = text[:s].strip()
          live_or_not = self.utils.check_live_noun(A)
          if live_or_not:
              live_vs_not = "چه کسی "
          else:
              live_vs_not = "چه چیزی"
          Q = live_vs_not + text[s:] + "؟"
          result.append({"Question": Q, "Answer": A})
      regexes = re.finditer(r"\s(زیرا|چون|چرا که|به این دلیل که)\s", text)
      for regex in regexes:
          s, e = regex.start(), regex.end()
          Q = "چرا " + text[:s] + "؟"
          A = "چون " + text[e:].strip() + '.'
          result.append({"Question": Q, "Answer": A})
      regexes = re.finditer(r"\s(می توان نتیجه گرفت)\s", text)
      for regex in regexes:
          s, e = regex.start(), regex.end()
          Q = text[:s] + " چه نتیجه ای می توان گرفت؟"
          A = text[e:].strip() + '.'
          result.append({"Question": Q, "Answer": A})
      return result
  def extract_cause_effects(self, text: str, key: str):
      """extracting cause and effect parts from text based on key regex. creating a Q&A based on key question format and answer format
      Parameters
      ---------
      text: str
        sentence query used to extract question and answers.
      key: str
        key should be one of all_regexes.keys(). sentence format used to extract Q&A
      
      
      Returns
      -------
      result: dict
        includes question and answer sentences.
        """

      key_information = self.all_regexes.get(key, None)
      if not key_information:
        print("you should specify current key information in all_regexes dict")
        return
      regex = key_information.get("regex")
      first_reg = re.compile(regex)
      x = re.search(first_reg, text)
      if x is not None:
        regex_groups = self.get_all_not_none_groups(x)
        if regex_groups is None:
          return
      else:
        # regex didn't found the structure. 
        return None
      if key in self.cause_effect_extractor_keys:
        if not self.validate_ta_regex(text, key):
          print("regex not validated with cause effect extractor")
          return None
      results = []
      q_as = key_information.get("q_as")
      for q_a in q_as:
        q_format = q_a.get("question")
        a_format = q_a.get("answer")  
        result = {"question": q_format.format(**regex_groups), "answer": a_format.format(**regex_groups)}
        results.append(result)
      return results


  def when_questions(self, text):
      result = []
      if bool(re.search('(زیرا|چون|چرا که|به این دلیل که)', text)):
        return result
      text = text.replace("\u200c", " ")
      text = text[:-1] if text[-1] is '.' else text
      extractions = self.utils.extract_time(text)
      for t in (extractions['datetime'].keys()):
          s, e = t[1:-1].split(', ')
          s, e = int(s), int(e)
          Q = text[:s] + 'چه زمانی' + text[e:] + '؟'
          A = text[s:e]
          result.append({"Question": Q, "Answer": A})
      return result


  def adjective_additive(self, text):
      # text = text[:-1] if text[-1] is '.' else text
      normalizer = Normalizer()
      text = normalizer.normalize(text)
      def check_live(word):
          stemmer = Stemmer()
          for pat in self.utils.live_patterns:
              if stemmer.stem(word) in pat:
                  return True
          return False 

      result = []
      if bool(re.search('(زیرا|چون|چرا که|به این دلیل که)', text)):
          return result
      
      word_taggs = self.utils.tagger.tag(word_tokenize(text))
      words = [w[0] for w in word_taggs]
      taggs = [w[1] for w in word_taggs]

      for i in range(1,len(taggs)):
          if taggs[i-1]=='Ne':
              if taggs[i]=='N' and check_live(words[i]):
                  Q = text.replace(words[i],'چه کسی')
                  Q = Q[:-1] if Q[-1] is '.' else Q
                  Q = Q + '؟'
                  A = words[i-1] + ' ' + words[i]
                  result.append({"Question": Q, "Answer": A})
              elif taggs[i] == 'AJ' or (taggs[i]=='N' and not(check_live(words[i]))):
                  l = words[:i-1]+ ['چه', words[i-1]+' ی']+words[i+1:]
                  Q = " ".join(l)
                  Q = Q[:-1] if Q[-1] is '.' else Q
                  Q = Q.strip() + '؟'
                  A = words[i-1] + ' ' + words[i]
                  result.append({"Question": Q, "Answer": A})
      return result

  def extract_questions(self, text: str):
    """
    checking all different sentence formats on text. if one is applied ignore others and return
    Parameters
    ----------
    text: str
        input sentence(s)
    
    Returns
    ------
    result: dict
      question and answer sentences.
    """
    for key, value in self.all_regexes.items():
        result = self.extract_cause_effects(text, key)
        if result:
            return result

  def generate_qa_by_substitution(self, sentence):
    if not self.utils.use_farsnet:
      return None 

    results = []
    sentence = hazm.Normalizer().normalize(sentence)
    words = hazm.word_tokenize(sentence)
    structure_tree = self.utils.extract_structures(tagger.tag(words))
    subtrees = list(structure_tree.subtrees())[1:]
    for index, subtree in enumerate(subtrees):
        if subtree.label() in self.utils.questionable_poses:
            answer = ' '.join(map(lambda leaf: leaf[0], subtree.leaves()))
            question_word = self.utils.get_question_word(answer, **self.utils.questionable_poses[subtree.label()])
            if subtree.label() == 'MOTAMEMI':
                question_word = list(subtree.leaves())[0][0] + ' ' + question_word
            elif subtree.label() == 'MAFOULI':
                question_word = question_word + ' ' + list(subtree.leaves())[-1][0]
            # print(question_word)
            question = sentence.replace(answer, question_word).replace('.', '?')
            results.append({"Question": question, "Answer": answer})
    return results

  def run(self, text):
    methods_names = [
        'transitive_verbs',
        'esnadi_verbs',
        'prepositional_verbs',
        'do_questions',
        'including_keywords',
        'when_questions',
        'adjective_additive',
        'extract_questions',
        'generate_qa_by_substitution'
        # append your methods here
    ]
    methods = [getattr(self, method_name) for method_name in methods_names]
    # run methods
    questions = list()
    for method in methods:
      try:
        result = method(text)
      except Exception as e:
        print("error running method: ", method)
        result = None
      if result:
        questions.extend(result)
    return questions
