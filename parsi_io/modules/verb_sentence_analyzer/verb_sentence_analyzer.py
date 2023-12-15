import re

from sentence_analyzer import analyze
from sentence_analyzer import split_sentences_semantically
from sentence_analyzer import convert_chunked_to_normal
from verb_scanner import find_verb_details

normalized_tense = {
    "mazi_sade": "گذشته ساده",
    "mazi_estemrari": "گذشته پیوسته",
    "mazi_naghli": "گذشته زنده",
    "mazi_baeed": "گذشته دور",
    "mazi_eltezami": "گذشته درخواستی",
    "mazi_mostamar": "گذشته ملموس",

    "mozare_ekhbari": "حال اخباری",
    "mozare_ekhbari_mianji": "حال اخباری",
    "mozare_eltezami": "حال التزامی",
    "mozare_eltezami_mianji": "حال التزامی",
    "mozare_mostamar": "حال ملموس",
    "mozare_mostamar_mianji": "حال ملموس",
    "ayande": "آینده ساده"
}

normalized_person = {
    'من': 'اول شخص مفرد',
    'تو': 'دوم شخص مفرد',
    'او': 'سوم شخص مفرد',
    'ما': 'اول شخص جمع',
    'شما': 'دوم شخص جمع',
    'ایشان': 'سوم شخص جمع',
}


def run(text):
    sentences = split_sentences_semantically(text)
    sentences = [convert_chunked_to_normal(sentence) for sentence in sentences]

    seen_verbs = {}
    final_results = []
    for sentence in sentences:
        extracted_info = analyze(sentence)
        spans_sentence = []
        for verb_parts in extracted_info["verbs_dependency_graph"]:
            verb = " ".join(verb_parts)

            if verb in seen_verbs:
                seen_verbs[verb] += 1
            else:
                seen_verbs[verb] = 0

            pattern = re.compile(verb)
            list_spans_verb = []
            for match in pattern.finditer(text):
                span = match.start(), match.start() + len(verb)
                list_spans_verb.append(span)

            span_current_verb = list_spans_verb[seen_verbs[verb]]
            spans_sentence.append(span_current_verb)

        subject = extracted_info["sub_dependency_graph"]
        list_subjects = ['من', 'تو', 'ما', 'شما', 'ایشان']
        if subject is not None:
            if "".join(subject.split()) == 'آنها':
                subject = 'ایشان'
            if subject not in list_subjects:
                subject = 'او'

        details = find_verb_details(extracted_info["verbs_dependency_graph"], subject)
        final_result = {
            "verb": {
                "span": spans_sentence,
                "root": details['root'],
                "structure": details['structure'],
                "person": normalized_person[details['person']],
                "tense": normalized_tense[details['tense']],
                "prefix": details['prefix']
            },
            "subject phrase": extracted_info["sub_dependency_graph"],
            "object phrase": extracted_info["obj_dependency_graph"],
        }
        final_results.append(final_result)
    return final_results


