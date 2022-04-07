import typing
import math
import re
from .pattern import *

class NumberExtractor:
	def __init__(self):
		# extract_phrases regex
		self.re_search = re.compile(PATTERN_SEARCH)
		self.re_norm_add_space = re.compile(f'({PATTERN_NUMBER_WITH_DIGITS})')
		# self.re_norm_revert = re.compile(f' ?({PATTERN_NUMBER_WITH_DIGITS}) ?')
		# get_value_extend regex
		self.re_before_extend = re.compile(PATTERN_BEFORE_EXTEND)
		self.re_extend = re.compile(PATTERN_EXTEND)
		# get_sub_phrase_value regex
		self.re_parts = {}
		for key, val in ALL_PARTS.items():
			self.re_parts[key] = re.compile(val)
		# get_value regex
		self.re_neg = re.compile(ALL_NEGS)
		self.re_single = re.compile(PATTERN_SINGLE_NUMBER)

	def __find_index_match(self, base, normed):
		base_idx = [idx for idx, c in enumerate(base) if c != ' ']
		normed_idx = [idx for idx, c in enumerate(normed) if c != ' ']
		return dict(list(zip(normed_idx, base_idx)))

	def __extract_spans(self, input_sentence: str) -> typing.List[typing.Tuple[int, int]]:
		return_value = []
		normed_input_sentence = self.re_norm_add_space.sub(r' \1 ', input_sentence)  # adding space around digits
		span_convert_dict = self.__find_index_match(input_sentence, normed_input_sentence)
		for match in self.re_search.finditer(normed_input_sentence):
			_span_b, _span_e = match.span(1)
			span = span_convert_dict[_span_b], span_convert_dict[_span_e - 1] + 1
			return_value.append(span)
		return return_value

	def __get_value_digit(self, sub_phrase: str) -> typing.Tuple[float]:
		intab = PERSIAN_ZERO_DIGIT + PERSIAN_NON_ZERO_DIGITS + '٫'
		outtab = ENGLISH_ZERO_DIGIT + ENGLISH_NON_ZERO_DIGITS + '.'
		translation = str.maketrans(intab, outtab)
		return float(sub_phrase.translate(translation)),

	def __get_value_simple(self, sub_phrase: str) -> typing.Tuple[float]:
		return ALL_PERSIAN_SIMPLE_NUMBERS[sub_phrase],

	def __get_value_extend(self, sub_phrase: str) -> tuple:
		multiplier = 1

		before_extend = self.re_before_extend.findall(sub_phrase)[0]
		before_extend_value = self.__get_value(before_extend)  # a digit_Value or a simple value
		sub_phrase = self.re_before_extend.sub('', sub_phrase, 1)  # remove before extend part

		extends = self.re_extend.findall(sub_phrase)

		if before_extend.strip() == TEXT_SI and extends[0] == TEXT_SAD: # 300 special case
			before_extend_value = 3

		for extend in extends:
			multiplier *= PERSIAN_REQUIRED_EXTENDABLE_NUMBERS[extend]

		if multiplier < 1:
			return before_extend_value * multiplier,

		if extends[0] == TEXT_SAD:
			return before_extend_value * multiplier,

		return before_extend_value, multiplier

	def __get_sub_phrase_value(self, sub_phrase: str) -> tuple:
		get_value_mapper = {
			'EXTENDED': self.__get_value_extend,
			'DIGIT': self.__get_value_digit,
			'SIMPLE': self.__get_value_simple
		}
		for sub_phrase_kind, re_obj in self.re_parts.items():
			if re_obj.match(sub_phrase):
				return get_value_mapper[sub_phrase_kind](sub_phrase)

	def __get_value(self, phrase: str) -> float:
		return_value = 0
		temp_value = 0
		highest_extend_multiplier = 0
		negative_number = False

		if phrase in PERSIAN_SPECIAL_CASES:
			return PERSIAN_SPECIAL_CASES[phrase]
		if len(self.re_neg.findall(phrase)):
			negative_number = True

		sub_phrases = self.re_single.findall(phrase)
		sub_phrase_values = map(self.__get_sub_phrase_value, sub_phrases)

		for index, value in enumerate(sub_phrase_values):
			addition = value[0]

			if temp_value != 0:
				if temp_value % 10**math.ceil(math.log(addition, 10)) >= 1:
					raise ValueError(index)  # Panic: There are more than one valid number in the phrase

			temp_value += addition

			if len(value) == 2:
				multiplier = value[1]
				if highest_extend_multiplier < multiplier:
					highest_extend_multiplier = multiplier
					temp_value += return_value
					return_value = 0
				return_value = return_value + temp_value * multiplier
				temp_value = 0

		return_value += temp_value

		if negative_number:
			return_value = -return_value

		return return_value

	def run(self, input_sentence):
		return_value = []
		spans = self.__extract_spans(input_sentence)
		i = 0
		while i < len(spans):
			span = spans[i]
			phrase = input_sentence[span[0]: span[1]]
			try:
				return_value.append({
					'span': list(span),
					'phrase': phrase,
					'value': self.__get_value(phrase)
				})
				i += 1
			except ValueError as exp:  # Handling __get_value panic
				last_phrase_parts = phrase.split(PERSIAN_V, exp.args[0])
				phrase1_end = len(phrase) - len(last_phrase_parts[-1])
				_sub_span1 = self.__extract_spans(phrase[:phrase1_end])[0]
				_sub_span2 = self.__extract_spans(last_phrase_parts[-1])[0]
				sub_span1 = _sub_span1[0] + span[0], _sub_span1[1] + span[0]
				sub_span2 = _sub_span2[0] + span[0] + phrase1_end, _sub_span2[1] + span[0] + phrase1_end
				spans[i] = sub_span1
				spans.insert(i + 1, sub_span2)
		return return_value
