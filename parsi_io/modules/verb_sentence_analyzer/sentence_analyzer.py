from hazm import *
import re
from constants import *

lemmatizer = Lemmatizer()
normalizer = Normalizer()
tagger = POSTagger(model=postagger_path)
chunker = Chunker(model=chunker_path)
parser = DependencyParser(tagger=tagger, lemmatizer=lemmatizer)

'''
Returns a list of POS tagged sub_sentences, each of which is a str object.
If the sentences is not a compound of multiple sentences, the list will have one element.
'''
def chunk_sentence(sentence):
    tagged = tagger.tag(word_tokenize(sentence))
    tree = chunker.parse(tagged)
    chunked = tree2brackets(tree)
    separator_pattern = re.compile(r'] ([^\[ ]+?) \[')
    separators = separator_pattern.findall(chunked)
    non_punctuation_tokens = set(map(lambda e: e[0] if e[1] != 'PUNCT' else None, tagged))
    conjunctions = non_punctuation_tokens.intersection(separators)
    sub_sentences = [[]]
    for tag in tagged:
        if tag[0] in conjunctions:
            sub_sentences.append([])
        else:
            sub_sentences[-1].append(tag)
    chunked_sub_sentences = [tree2brackets(chunker.parse(sub_sentence)) for sub_sentence in sub_sentences]
    return chunked_sub_sentences


def clean_verb(verb_phase):
    return re.subn('_', ' ', verb_phase)[0]

def extract_verb_phrases(chunked):
    verb_phrase_pattern = re.compile(r'\[([^\[]+?) VP]')
    verb_phrases = verb_phrase_pattern.findall(chunked)
    if verb_phrases:
        verb_phrases = [clean_verb(vp) for vp in verb_phrases]
    return verb_phrases


def extract_objects(chunked):
    obj_pattern = re.compile(r'\[([^\[]+) NP] \[را POSTP]')
    objects = obj_pattern.findall(chunked)
    return objects


def extract_subj_from_dependency_graph(dependencyGraph, info):
    subj_parts = []
    if info['deps']:  # if had dependencies
        for type in info['deps']:
            for index in info['deps'][type]:
                subj_parts.append((index, dependencyGraph.nodes[index]["word"]))
    subj_parts.append((info['address'], info['word']))
    subj_parts.sort(key=lambda a: a[0])
    if subj_parts:
        subj = " ".join([subj_part[1] for subj_part in subj_parts])
    else:
        subj = None
    return subj


def extract_obj_from_dependency_graph(dependencyGraph, info):
    obj_parts = []
    if info['deps']:  # if had dependencies
        for type in info['deps']:
            if type != "case":  # ignore را
                for index in info['deps'][type]:
                    obj_parts.append((index, dependencyGraph.nodes[index]["word"]))
    obj_parts.append((info['address'], info['word']))
    obj_parts.sort(key=lambda a: a[0])
    if obj_parts:
        obj = " ".join([obj_part[1] for obj_part in obj_parts])
    else:
        obj = None
    return obj


def extract_verbs_from_dependency_graph(dependencyGraph, info):
    verb_parts = []
    if info['deps']:
        for type in info['deps']:
            if type == 'compound':
                for index in info['deps'][type]:
                    verb_parts.append(dependencyGraph.nodes[index]['word'])
    verb_parts.append(clean_verb(info['word']))
    return verb_parts


def create_dependency_graph(sentence):
    dependencyGraph = parser.parse(word_tokenize(sentence))
    subj = None
    obj = None
    verbs = []
    for i in range(len(dependencyGraph.nodes)):
        info = dependencyGraph.nodes[i]
        if info['tag'] == 'VERB':
            verbs.append(extract_verbs_from_dependency_graph(dependencyGraph, info))
        if info['rel'] == 'obj':
            obj = extract_obj_from_dependency_graph(dependencyGraph, info)
        if info['rel'] == 'nsubj':
            subj = extract_subj_from_dependency_graph(dependencyGraph, info)
    return (subj, obj, verbs)

def convert_chunked_to_normal(chunked_sent):
    removed_brackets = re.subn(r'\[|]', '', chunked_sent)[0]
    removed_alphabets = re.subn(r'[A-Z]', '', removed_brackets)[0]
    removed_underscores = re.subn('_', ' ', removed_alphabets)[0]
    removed_extra_spaces = re.subn(r'\s(?=[a-zA-Z])', '', removed_underscores)[0]
    return removed_extra_spaces

def split_sentences_semantically(input_text):
    all_sub_sentences = []
    sentences = sent_tokenize(input_text)
    for sentence in sentences:
        chunked_sub_sentences = chunk_sentence(sentence)
        all_sub_sentences.extend(chunked_sub_sentences)
    return all_sub_sentences


def analyze(sentence):
    extracted_info_sentence = {}
    chunked_sub_sentences = chunk_sentence(sentence)
    for chunked_sub_sentence in chunked_sub_sentences:
        obj_chunker = extract_objects(chunked_sub_sentence)
        verbs_chunker = extract_verb_phrases(chunked_sub_sentence)
        sub_dependency_graph, obj_dependency_graph, verbs_dependency_graph = create_dependency_graph(convert_chunked_to_normal(chunked_sub_sentence))
        extracted_info_sentence["obj_chunker"] = obj_chunker
        extracted_info_sentence["verbs_chunker"] = verbs_chunker
        extracted_info_sentence["sub_dependency_graph"] = sub_dependency_graph
        extracted_info_sentence["obj_dependency_graph"] = obj_dependency_graph
        extracted_info_sentence["verbs_dependency_graph"] = verbs_dependency_graph


    return extracted_info_sentence
