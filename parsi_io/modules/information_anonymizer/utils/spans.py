import re
from traceback import print_tb
from typing import Dict
import numpy as np
from parsanonymizer.utils import const


def merge_spans(spans: Dict, text: str):
    result, encoded = dict(), dict()

    for key in spans.keys():
        if key == 'personalname':
            encoded[key] = encode_span(spans[key], spans['adversarial'] + spans['address'], text)
            encoded[key] = encode_space(encoded[key], spans['space'])
            result[key] = find_spans(encoded[key])
        else:
            encoded[key] = encode_span(spans[key], spans['adversarial'], text)
            encoded[key] = encode_space(encoded[key], spans['space'])
            result[key] = find_spans(encoded[key])

        if key == 'url':
            encoded[key] = encode_span(spans[key], spans['adversarial'] + spans['email'], text)
            encoded[key] = encode_space(encoded[key], spans['space'])
            result[key] = find_spans(encoded[key])
        else:
            encoded[key] = encode_span(spans[key], spans['adversarial'], text)
            encoded[key] = encode_space(encoded[key], spans['space'])
            result[key] = find_spans(encoded[key])


    return result


def create_spans(regexes, text):
    # add pattern keys to dictionaries and define a list structure for each key
    spans = {}
    for key in regexes.keys():
        spans[key] = []

    # apply regexes on normalized sentence and store extracted markers
    for key in regexes.keys():
        for regex_value in regexes[key]:
            # apply regex
            matches = list(
                re.finditer(
                    fr'\b(?:{regex_value})(?:\b|(?!{const.FA_SYM}|\d+))',
                    text)
            )
            # ignore empty markers
            if len(matches) > 0:
                # store extracted markers
                for match in matches:
                    start = match.regs[0][0]
                    end = match.regs[0][1]
                    if (key=='personalname'):
                        if any([start>= s[0] and end <= s[1] + 2 for s in spans['address']]):
                            continue
                        
                    spans[key].append((start, end))

    return spans


def encode_span(normal_spans, adv_spans, text):
    encoded_sent = np.zeros(len(text))

    for span in normal_spans:
        encoded_sent[span[0]: span[1]] = 1

    for span in adv_spans:
        encoded_sent[span[0]: span[1]] = 0

    return encoded_sent


def find_spans(encoded_sent):
    """
    Find spans in a given encoding
    :param encoded_sent: list
    :return: list[tuple]
    """
    spans = []
    i: int = 0
    len_sent = len(encoded_sent)

    while i < len_sent:
        # ignore if it starts with 0(nothing matched) or -1(space)
        if encoded_sent[i] <= 0:
            i += 1
            continue
        else:
            # it means it starts with 1
            start = i
            end = i + 1
            # continue if you see 1 or -1
            while i < len_sent and (encoded_sent[i] == 1 or encoded_sent[i] == -1):
                # store the last time you see 1
                if encoded_sent[i] == 1:
                    end = i + 1
                i += 1

            spans.append([start, end])
    return spans



def encode_space(encoded_sent, space_spans):
    """
    Encoded spaces to -1 in sentence encoding
    :param encoded_sent: list
    :param space_spans: list[tuple]
    :return: list
    """
    for span in space_spans:
        encoded_sent[span[0]: span[1]] = -1

    return encoded_sent

