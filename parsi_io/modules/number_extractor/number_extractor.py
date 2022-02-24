import typing
import math
import re
from .pattern import *

class NumberExtractor:
	def __init__(self):
		# extract_phrases regex
		self.re_search = re.compile(PATTERN_SEARCH)
		self.re_norm_add_space = re.compile(f'({PATTERN_NUMBER_WITH_DIGITS})')
		self.re_norm_revert = re.compile(f' ?({PATTERN_NUMBER_WITH_DIGITS}) ?')
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

	def __extract_phrases(self, input_sentence: str) -> typing.List[str]:
		input_sentence = self.re_norm_add_space.sub(r' \1 ', input_sentence)  # adding space around digits
		phrases = self.re_search.findall(input_sentence)
		for index, phrase in enumerate(phrases):
			phrases[index] = self.re_norm_revert.sub(r'\1', phrase)   # reverting space around digits
		return phrases

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

		for extend in extends:
			multiplier *= PERSIAN_REQUIRED_EXTENDABLE_NUMBERS[extend]

		if multiplier < 1:
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

		if phrase == PERSIAN_ZERO:
			return 0  # this is zero obviously
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
		phrases = self.__extract_phrases(input_sentence)
		i = 0
		while i < len(phrases):
			try:
				return_value.append({
					'phrase': phrases[i],
					'value': self.__get_value(phrases[i])
				})
				i += 1
			except ValueError as exp:  # Handling __get_value panic
				last_phrase_parts = phrases[i].split(PERSIAN_V, exp.args[0])
				phrase1_end = len(phrases[i]) - len(last_phrase_parts[-1])
				sub_phrase1 = self.__extract_phrases(phrases[i][:phrase1_end])[0]
				sub_phrase2 = self.__extract_phrases(last_phrase_parts[-1])[0]
				phrases[i] = sub_phrase1
				phrases.insert(i + 1, sub_phrase2)
		return return_value
