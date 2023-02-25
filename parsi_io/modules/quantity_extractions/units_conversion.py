from .unit_extractor import *
from .helpers import *
import pint 

ureg = pint.UnitRegistry()

question_words = [
    'چند',
    'چقدر',
    'چه‌قدر',
    'چه قدر',
    'چه‌میزان',
    'چه میزان'
]

equivalent_words = [
    'به',
    'برابر',
    'مساوی',
    'معادل',
    'هم‌ارز',
    'هم ارز',
]

Q_WORDS = join_patterns(question_words)
EQV_WORDS = join_patterns(equivalent_words)

QUESTION_TYPES = [
    rf'(?P<given>{NUM_UNIT})(.*){WS}(?:{EQV_WORDS}{WS}(?:با{WS})?)?{Q_WORDS}{WS}(?P<asked>{COMPLEX_UNIT})',
    rf'{Q_WORDS}{WS}(?P<asked>{COMPLEX_UNIT})(.*){WS}(?:{EQV_WORDS}{WS}(?:با{WS})?)?(?P<given>{NUM_UNIT})',
    rf'تبدیل{WS}(?P<given>{NUM_UNIT}){WS}به{WS}(?P<asked>{COMPLEX_UNIT})',
    rf'(?P<given>{COMPLEX_UNIT})(.*){WS}(?:{EQV_WORDS}{WS}(?:با{WS})?)?{Q_WORDS}{WS}(?P<asked>{COMPLEX_UNIT})',
    rf'{Q_WORDS}{WS}(?P<asked>{COMPLEX_UNIT})(.*){WS}(?:{EQV_WORDS}{WS}(?:با{WS})?)?(?P<given>{COMPLEX_UNIT})',
    rf'تبدیل{WS}(?P<given>{COMPLEX_UNIT}){WS}به{WS}(?P<asked>{COMPLEX_UNIT})',
]


def convert_units(num1, unit1, unit2):
    try:
        conversion = ureg(unit_to_str(unit1)).to(unit_to_str(unit2))
        return (num1 * conversion).magnitude
    except:
        return 'ناممکن'


def answer_conversion_question(question):
    ureg = pint.UnitRegistry()
    for pattern in QUESTION_TYPES:
        for match in re.finditer(pattern, question):
            given_unit = extract_units(match.group('given'))[0]['object']
            asked_unit = extract_units(match.group('asked'))[0]['object']
            given_nums = extract_numbers(match.group('given'))
            if not given_nums:
                given_nums = [{'value': 1}]
            asked_nums = []
            for num in given_nums:
                asked_num = convert_units(num['value'], given_unit, asked_unit)
                if asked_num != 'ناممکن':
                    asked_num = round(asked_num, 4)
                asked_nums.append(asked_num)
            return asked_nums
