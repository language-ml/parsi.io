
def join_patterns(items):
	return '(?:' + '|'.join(list(items)) + ')'  # No capture grouping


# Let's ignore this for now
# def accept_all_ya(pattern: str):
ALL_YA = '[یي]'  # Both ی in perso-arabic script
# 	return pattern.replace('ی', ALL_YA)

ENGLISH_NON_ZERO_DIGITS = '123456789'
PERSIAN_NON_ZERO_DIGITS = '۱۲۳۴۵۶۷۸۹'
ENGLISH_ZERO_DIGIT = '0'
PERSIAN_ZERO_DIGIT = '۰'
DIGIT_NEG = '-'

PERSIAN_V = 'و'
PERSIAN_NEG = 'منفی'

NIM_SPACE = '\u200c'
WHITE_SPACE = rf'[{NIM_SPACE}\s]'

PERSIAN_SPECIAL_CASES = {
	'صفر': 0,
	# 'اول': 1,
}

PERSIAN_UNDER_10_NUMBERS = {
	'یک': 1,  # Zero has different properties
	'دو': 2,
	'سه': 3,
	'سوم': 3,
	'چهار': 4,
	'پنج': 5,
	'شش': 6,
	'هفت': 7,
	'هشت': 8,
	'نه': 9,
	'نیم': 0.5
}

PERSIAN_UNDER_20_NUMBERS = {
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

TEXT_SI = 'سی' # special case with 100
TEXT_SAD = 'صد'
PERSIAN_UNDER_100_NUMBERS = {
	'بیست': 20,
	'سی': 30,
	'چهل': 40,
	'پنجاه': 50,
	'شصت': 60,
	'هفتاد': 70,
	'هشتاد': 80,
	'نود': 90,
}

PERSIAN_UNDER_1000_NUMBERS = {
	'صد': 100,
	# 'یکصد': 100,
	'دویست': 200,
	# 'سیصد': 300,
	# 'چهارصد': 400,
	'پانصد': 500,
	# 'ششصد': 600,
	# 'هفتصد': 700,
	# 'هشتصد': 800,
	# 'نهصد': 900,
	'هزار': 1000,
	# 'یکهزار': 1000
}


PERSIAN_REQUIRED_EXTENDABLE_NUMBERS = {
    'دهم': 0.1,
   	'صدم': 0.01,
   	'هزارم': 0.001,

	'صد': 100,  # YES I know these are redundant but it has a different usage
	'هزار': 1000,
	'میلیون': 10**6,  # Handle different form?
	'ملیون': 10**6,
	'میلیارد': 10**9
}

# Handling 123, ۲۱۳, 3۲1
PATTERN_DIGIT = join_patterns(list(ENGLISH_NON_ZERO_DIGITS + PERSIAN_NON_ZERO_DIGITS + ENGLISH_ZERO_DIGIT + PERSIAN_ZERO_DIGIT))
PATTERN_DOT = '(?:\.|٫)'
PATTERN_NUMBER_WITH_DIGITS = f'{PATTERN_DIGIT}*{PATTERN_DOT}?{PATTERN_DIGIT}+'
# Handling یگ, یازده, دویست
ALL_PERSIAN_SIMPLE_NUMBERS = { # Order is important :|
	**PERSIAN_UNDER_1000_NUMBERS,
	**PERSIAN_UNDER_100_NUMBERS,
	**PERSIAN_UNDER_20_NUMBERS,
	**PERSIAN_UNDER_10_NUMBERS
}
PATTERN_SIMPLE_NUMBER = join_patterns(ALL_PERSIAN_SIMPLE_NUMBERS.keys())
# Handling 33 هزار
PATTERN_BEFORE_EXTEND = join_patterns([rf'{PATTERN_NUMBER_WITH_DIGITS}{WHITE_SPACE}*', rf'{PATTERN_SIMPLE_NUMBER}{WHITE_SPACE}*'])
PATTERN_EXTEND = join_patterns(PERSIAN_REQUIRED_EXTENDABLE_NUMBERS)
PATTERN_EXTENDABLE_NUMBER = rf'{PATTERN_BEFORE_EXTEND}{PATTERN_EXTEND}(?:{WHITE_SPACE}+{PATTERN_EXTEND})*'
# Handing number with و
# REASON of using dict: cleaner code when using get_value in the main
ALL_PARTS = {
	'EXTENDED': PATTERN_EXTENDABLE_NUMBER,
	'DIGIT': PATTERN_NUMBER_WITH_DIGITS,
	'SIMPLE': PATTERN_SIMPLE_NUMBER
}  # Order is important :|
PATTERN_SINGLE_NUMBER = join_patterns(ALL_PARTS.values())  # We do not need the keys here
PATTERN_MULTIPLE_NUMBER = rf'{PATTERN_SINGLE_NUMBER}(?:{WHITE_SPACE}+{PERSIAN_V}{WHITE_SPACE}+{PATTERN_SINGLE_NUMBER})*'

ALL_NEGS = join_patterns([rf'{PERSIAN_NEG}{WHITE_SPACE}+', rf'{DIGIT_NEG}{WHITE_SPACE}*'])
PATTERN_ALL_NUMBER_EXCEPT_ZERO = f'{ALL_NEGS}?{PATTERN_MULTIPLE_NUMBER}'
PATTERN_ALL_NUMBER = join_patterns([PATTERN_ALL_NUMBER_EXCEPT_ZERO] + list(PERSIAN_SPECIAL_CASES.keys()))

BEFORE_NUMBER = r'(?:\W|^)'

END_WORD_LIST = [
	'م',
	'مین',
	'بار',
	'عدد',
	'برابر'
]
END_WORD_LIST_WITH_AFTER = [f'{item}{ALL_YA}?{WHITE_SPACE}' for item in END_WORD_LIST]
AFTER_NUMBER = join_patterns(END_WORD_LIST_WITH_AFTER + [r'\W', '$'])

PATTERN_SEARCH = BEFORE_NUMBER + f'({PATTERN_ALL_NUMBER})' + AFTER_NUMBER

