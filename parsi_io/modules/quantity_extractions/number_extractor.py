import re
import unidecode


def join_patterns(patterns, grouping=False):
    return '(' + ('?:' if not grouping else '') + '|'.join(patterns) + ')'


END_WORDS_LIST = [
    'م',
    'مین',
    'بار',
    'عدد',
    'برابر',
    'دفعه',
    'مرتبه',
    'تا',
]

NUM_1_2_to_9_DICT = {
    'یک': 1,
    'دو': 2,
    'سه': 3,
    'سو': 3,
    'چهار': 4,
    'پنج': 5,
    'شش': 6,
    'هفت': 7,
    'هشت': 8,
    'نه': 9
}

NUM_10_11_to_19_DICT = {
    'ده': 10,
    'یازده': 11,
    'دوازده': 12,
    'سیزده': 13,
    'چهارده': 14,
    'پانزده': 15,
    'شانزده': 16,
    'هفده': 17,
    'هجده': 18,
    'نوزده': 19
}

NUM_20_30_to_90_DICT = {
    'بیست': 20,
    'سی': 30,
    'چهل': 40,
    'پنجاه': 50,
    'شصت': 60,
    'هفتاد': 70,
    'هشتاد': 80,
    'نود': 90,
}

NUM_100_200_to_900_DICT = {
    'صد': 100,
    'یکصد': 100,
    'دویست': 200,
    'سیصد': 300,
    'چهارصد': 400,
    'پانصد': 500,
    'ششصد': 600,
    'هفتصد': 700,
    'هشتصد': 800,
    'نهصد': 900
}

NUM_EXTENDER_DICT = {
    'هزار': 1E3,
    'میلیون': 1E6,
    'میلیارد': 1E9
}

NUM_SPECIAL_FRACTION_DICT = {
    'نیم': 1 / 2,
    'نصف': 1 / 2,
    'ثلث': 1 / 3,
    'ربع': 1 / 4,
    'خمس': 1 / 5
}

NUM_UNDER_1000_DICT = {
    **NUM_1_2_to_9_DICT,
    **NUM_10_11_to_19_DICT,
    **NUM_20_30_to_90_DICT,
    **NUM_100_200_to_900_DICT
}

WHITE_SPACE = r'[\s\u200c]+'
CONNECTOR = rf'{WHITE_SPACE}و{WHITE_SPACE}'
DIGITS = r'[۰۱۲۳۴۵۶۷۸۹0123456789٠١٢٣٤٥٦٧٨٩]'
NEGATIVE = r'منفی'
DOTS = r'[٫\.]'
ZERO = r'صفر'

# Pattern for digit-based NUM
NUM_DIGIT_BASED = rf'(?:-?{DIGITS}+(?:{DOTS}{DIGITS}+)?)'

# Pattern for NUM ∈ {1,2,...,99}
NUM_1_2_to_9 = join_patterns(NUM_1_2_to_9_DICT.keys(), True)
NUM_10_11_to_19 = join_patterns(NUM_10_11_to_19_DICT.keys(), True)
NUM_20_30_to_90 = join_patterns(NUM_20_30_to_90_DICT.keys(), True)
NUM_20_21_to_99 = rf'(?:{NUM_20_30_to_90}(?:{CONNECTOR}{NUM_1_2_to_9})?)'
NUM_1_2_to_99 = join_patterns([NUM_10_11_to_19, NUM_20_21_to_99, NUM_1_2_to_9])

# Pattern for NUM ∈ {1,2,...,999}
NUM_100_200_to_900 = join_patterns(NUM_100_200_to_900_DICT.keys(), True)
NUM_100_101_to_999 = rf'(?:{NUM_100_200_to_900}(?:{CONNECTOR}{NUM_1_2_to_99})?)'
NUM_1_2_to_999 = join_patterns([NUM_100_101_to_999, NUM_1_2_to_99, NUM_DIGIT_BASED])

# Pattern for NUM ∈ {1,2,...}
NUM_EXTENDER = join_patterns(NUM_EXTENDER_DICT.keys(), True)
NUM_1_2_to_999_EXTENDED = rf'(?:(?:{NUM_1_2_to_999}{WHITE_SPACE})?{NUM_EXTENDER}(?:{WHITE_SPACE}{NUM_EXTENDER})*)'
NUM_EXTENDED = rf'(?:{NUM_1_2_to_999_EXTENDED}(?:{CONNECTOR}{NUM_1_2_to_999_EXTENDED})*(?:{CONNECTOR}{NUM_1_2_to_999})?)'
NUM_NATURAL = join_patterns([NUM_EXTENDED, NUM_1_2_to_999])

# Pattern for NUM ∈ Z
NUM_INTEGER = join_patterns([ZERO, rf'(?:(?:({NEGATIVE}){WHITE_SPACE})?{NUM_NATURAL})'])

# Pattern for NUM ∈ {p/q | p,q ∈ Z}
NUM_NORMAL_FRACTION = rf'(?:{NUM_INTEGER}{WHITE_SPACE}{NUM_INTEGER}م)'
NUM_NORMAL_FRACTION_LABELED = rf'(?:(?P<numerator>{NUM_INTEGER}){WHITE_SPACE}(?P<denominator>{NUM_INTEGER})م)'
NUM_SPECIAL_FRACTION = join_patterns(NUM_SPECIAL_FRACTION_DICT.keys())
NUM_FRACTION = join_patterns([NUM_SPECIAL_FRACTION, NUM_NORMAL_FRACTION])

# Pattern for NUM ∈ {n+(p/q) | n,p,q ∈ Z}
NUM_INTEGER_PLUS_FRACTION_LABELED = rf'(?:(?P<integer_part>{NUM_INTEGER}){CONNECTOR}(?P<fraction_part>{NUM_FRACTION}))'
NUM_INTEGER_PLUS_FRACTION = rf'({NUM_INTEGER}{CONNECTOR}{NUM_FRACTION})'

# Pattern for NUM ∈ Q
NUM_RATIONAL = join_patterns([NUM_FRACTION, NUM_INTEGER_PLUS_FRACTION, NUM_INTEGER])

# Pattern for NUM in text
NUM_IN_TEXT = rf'{NUM_RATIONAL}{join_patterns(END_WORDS_LIST)}?'


def get_value_NUM_DIGIT_BASED(num_string):
    return float(unidecode.unidecode(num_string))


def get_value_NUM_1_2_to_999(num_string):
    try:
        return get_value_NUM_DIGIT_BASED(num_string)
    except:
        match_groups = re.match(NUM_1_2_to_999, num_string).groups()
        return sum([NUM_UNDER_1000_DICT[key] for key in filter(None, match_groups)])


def get_value_NUM_1_2_to_999_EXTENDED(num_string):
    extender_value = 1
    num_extender_matches = re.finditer(NUM_EXTENDER, num_string)
    for match in num_extender_matches:
        extender_value *= NUM_EXTENDER_DICT[match.group()]
    try:
        num_without_extender_match = re.search(NUM_1_2_to_999, re.sub(NUM_EXTENDER, '', num_string))
        num_without_extender = get_value_NUM_1_2_to_999(num_without_extender_match.group())
    except:
        num_without_extender = 1
    return extender_value * num_without_extender


def get_value_NUM_NATURAL(num_string):
    num_1_2_to_999_extended_list = re.finditer(NUM_1_2_to_999_EXTENDED, num_string)
    num_value = 0
    for match in num_1_2_to_999_extended_list:
        num_value += get_value_NUM_1_2_to_999_EXTENDED(match.group())
    num_1_2_to_999_at_the_end = re.search(NUM_1_2_to_999, re.sub(NUM_1_2_to_999_EXTENDED, '', num_string))
    if num_1_2_to_999_at_the_end:
        num_value += get_value_NUM_1_2_to_999(num_1_2_to_999_at_the_end.group())
    return num_value


def get_value_NUM_INTEGER(num_string):
    if re.search(ZERO, num_string):
        return 0
    coefficient = 1
    if re.search(NEGATIVE, num_string):
        coefficient = -1
    num_natural = re.search(NUM_NATURAL, num_string).group()
    return coefficient * get_value_NUM_NATURAL(num_natural)


def get_value_NUM_FRACTION(num_string):
    match = re.search(NUM_SPECIAL_FRACTION, num_string)
    if match:
        return NUM_SPECIAL_FRACTION_DICT[match.group()]
    match = re.search(NUM_NORMAL_FRACTION_LABELED, num_string)
    numerator = get_value_NUM_INTEGER(match.group('numerator'))
    denominator = get_value_NUM_INTEGER(match.group('denominator'))
    try:
        return numerator / denominator
    except:
        return 0


def get_value_NUM_INTEGER_PLUS_FRACTION(num_string):
    match = re.search(NUM_INTEGER_PLUS_FRACTION_LABELED, num_string)
    integer_part = get_value_NUM_INTEGER(match.group('integer_part'))
    try:
        fraction_part = get_value_NUM_FRACTION(match.group('fraction_part'))
    except:
        fraction_part = 0
    return integer_part + fraction_part


def get_value_NUM_RATIONAL(num_string):
    NUM_FRACTION_match = re.fullmatch(NUM_FRACTION, num_string)
    if NUM_FRACTION_match:
        return float(get_value_NUM_FRACTION(num_string))
    NUM_INTEGER_PLUS_FRACTION_match = re.fullmatch(NUM_INTEGER_PLUS_FRACTION, num_string)
    if NUM_INTEGER_PLUS_FRACTION_match:
        return float(get_value_NUM_INTEGER_PLUS_FRACTION(num_string))
    return float(get_value_NUM_INTEGER(num_string))


def extract_numbers(text):
    extracted_numbers = []
    for match in re.finditer(NUM_IN_TEXT, text):
        before_index = match.span()[0] - 1
        after_index = match.span()[1]
        if before_index >= 0 and re.match('\w', text[before_index]):
            continue
        if after_index < len(text) and re.match('\w', text[after_index]):
            continue

        extracted_numbers.append({
            'marker': match.group(),
            'span': match.span(),
            'value': get_value_NUM_RATIONAL(match.group())
        })

    return extracted_numbers
