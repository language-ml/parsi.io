# coding: utf-8

"""این ماژول شامل کلاس‌ها و توابعی برای نرمال‌سازی متن است.
"""

from __future__ import unicode_literals
import re
from typing import List

from .Lemmatizer import Lemmatizer
from .WordTokenizer import WordTokenizer
from .utils import maketrans


def compile_patterns(patterns):
    return [(re.compile(pattern), repl) for pattern, repl in patterns]


class Normalizer(object):
    """این کلاس شامل توابعی برای نرمال‌سازی متن است.

    Args:
        remove_extra_spaces (bool, optional): اگر `True‍` باشد فواصل اضافهٔ متن را حذف می‌کند.
        persian_style (bool, optional): اگر `True` باشد اصلاحات مخصوص زبان فارسی را انجام می‌دهد؛ مثلاً جایگزین‌کردن کوتیشن با گیومه.
        persian_numbers (bool, optional): اگر `True` باشد ارقام انگلیسی را با فارسی جایگزین می‌کند.
        remove_diacritics (bool, optional): اگر `True` باشد اعرابِ حروف را حذف می‌کند.
        affix_spacing (bool, optional): اگر `True` باشد فواصل را در پیشوندها و پسوندها اصلاح می‌کند.
        token_based (bool, optional): اگر `True‍` باشد متن به‌شکل توکن‌به‌توکن نرمالایز می‌شود نه یکجا.
        punctuation_spacing (bool, optional): اگر `True` باشد فواصل را در نشانه‌های سجاوندی اصلاح می‌کند.
    """

    def __init__(self, remove_extra_spaces=True, persian_style=True, persian_numbers=True,
                 remove_diacritics=True, affix_spacing=True, token_based=False,
                 punctuation_spacing=True, kohan_style=False):
        self._punctuation_spacing = punctuation_spacing
        self._affix_spacing = affix_spacing
        self._token_based = token_based
        self._kohan_style = kohan_style

        translation_src, translation_dst = ' ىكي“”', ' یکی""'
        if persian_numbers:
            translation_src += '0123456789%'
            translation_dst += '۰۱۲۳۴۵۶۷۸۹٪'
        self.translations = maketrans(translation_src, translation_dst)

        if self._token_based:
            lemmatizer = Lemmatizer()
            self.words = lemmatizer.words
            self.verbs = lemmatizer.verbs
            self.tokenizer = WordTokenizer(join_verb_parts=False)
            self.suffixes = {'ی', 'ای', 'ها', 'های', 'تر', 'تری', 'ترین', 'گری', 'ام', 'ات', 'اش'}

        self.character_refinement_patterns = []

        if remove_extra_spaces:
            self.character_refinement_patterns.extend([
                (r' {2,}', ' '),  # remove extra spaces
                (r'\n{3,}', '\n\n'),  # remove extra newlines
                (r'\u200c{2,}', '\u200c'),  # remove extra ZWNJs
                (r'[ـ\r]', ''),  # remove keshide, carriage returns
            ])

        if persian_style:
            self.character_refinement_patterns.extend([
                ('"([^\n"]+)"', r'«\1»'),  # replace quotation with gyoome
                ('([\d+])\.([\d+])', r'\1٫\2'),  # replace dot with momayez
                (r' ?\.\.\.', ' …'),  # replace 3 dots
            ])

        if remove_diacritics:
            self.character_refinement_patterns.append(
                ('[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]', ''),
                # remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN
            )

        self.character_refinement_patterns = compile_patterns(self.character_refinement_patterns)

        punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'«\[\(\{'
        if punctuation_spacing:
            self.punctuation_spacing_patterns = compile_patterns([
                ('" ([^\n"]+) "', r'"\1"'),  # remove space before and after quotation
                (' ([' + punc_after + '])', r'\1'),  # remove space before
                ('([' + punc_before + ']) ', r'\1'),  # remove space after
                ('([' + punc_after[:3] + '])([^ ' + punc_after + '\d۰۱۲۳۴۵۶۷۸۹])', r'\1 \2'),  # put space after . and :
                ('([' + punc_after[3:] + '])([^ ' + punc_after + '])', r'\1 \2'),  # put space after
                ('([^ ' + punc_before + '])([' + punc_before + '])', r'\1 \2'),  # put space before
            ])

        if affix_spacing:
            self.affix_spacing_patterns = compile_patterns([
                (r'([^ ]ه) ی ', r'\1‌ی '),  # fix ی space
                # (r'(^| )(ن?می) ', r'\1\2‌'),  # put zwnj after می, نمی
                # (
                #     r'(?<=[^\n\d ' + punc_after + punc_before + ']{2}) (تر(ین?)?|گری?|های?)(?=[ \n' + punc_after + punc_before + ']|$)',
                #     r'‌\1'),  # put zwnj before تر, تری, ترین, گر, گری, ها, های
                (r'([^ ]ه) (ا(م|یم|ش|ند|ی|ید|ت))(?=[ \n' + punc_after + ']|$)', r'\1‌\2'),
                # join ام, ایم, اش, اند, ای, اید, ات
            ])

        if kohan_style:
            base_pattern_regex = r'(^|[^\S]){}([^\S]|$)'
            base_repl_regex = r'\1{}\2'
            fix_pp_dict = {
                'مگر': 'اگر',
                'ز': 'از'
            }
            extract_pp_dict = {
                'زان': 'از آن',
                'کان': 'که آن',
                'کاین': 'که این',
                'کاندر': 'که در',
                'گر': 'اگر',
                'کز': 'که از',
                'اندر': 'در',
                'ار': 'اگر',
                'کاخر': 'که آخر',
                'بتر': 'بدتر',
                'وان': 'و آن',
                'اوفتاد': 'افتاد'
            }
            self.fix_pp_patterns = compile_patterns([(base_pattern_regex.format(pt),
                                                      base_repl_regex.format(rep)) for pt, rep in fix_pp_dict.items()])
            self.extract_pp_patterns = compile_patterns([(base_pattern_regex.format(pt),
                                                          base_repl_regex.format(rep)) for pt, rep in extract_pp_dict.items()])

    def normalize(self, text):
        """متن را نرمال‌سازی می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.normalize('اِعلام کَرد : « زمین لرزه ای به بُزرگیِ 6 دهم ریشتر ...»')
            'اعلام کرد: «زمین‌لرزه‌ای به بزرگی ۶ دهم ریشتر…»'

        Args:
            text (str): متنی که باید نرمال‌سازی شود.

        Returns:
            (str): متنِ نرمال‌سازی‌شده.
        """
        text = self.character_refinement(text)
        if self._affix_spacing:
            text = self.affix_spacing(text)

        if self._token_based:
            # print(f"\nTEXT ::::: \n{text} \n END OF TEXT \n")

            tokens = self.tokenizer.tokenize(text.translate(self.translations))
            tokens = self.token_spacing(tokens)
            if self._kohan_style:
                tokens = self.fix_tokens(tokens)
            text = ' '.join(tokens)

        if self._punctuation_spacing:
            text = self.punctuation_spacing(text)

        if self._kohan_style:
            text = self.apply_patterns(text, self.fix_pp_patterns, self.extract_pp_patterns)

        return text

    def character_refinement(self, text):
        """حروف متن را به حروف استاندارد فارسی تبدیل می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.character_refinement('اصلاح كاف و ياي عربي')
            'اصلاح کاف و یای عربی'

            >>> normalizer.character_refinement('عراق سال 2012 قراردادی به ارزش "4.2 میلیارد دلار" برای خرید تجهیزات نظامی با روسیه امضا  کرد.')
            'عراق سال ۲۰۱۲ قراردادی به ارزش «۴٫۲ میلیارد دلار» برای خرید تجهیزات نظامی با روسیه امضا کرد.'

            >>> normalizer.character_refinement('رمــــان')
            'رمان'

            >>> normalizer.character_refinement('بُشقابِ مَن را بِگیر')
            'بشقاب من را بگیر'

        Args:
            text (str): متنی که باید حروف آن استانداردسازی شود.

        Returns:
            (str): متنی با حروف استاندارد فارسی.
        """

        text = text.translate(self.translations)
        for pattern, repl in self.character_refinement_patterns:
            text = pattern.sub(repl, text)
        return text

    def punctuation_spacing(self, text):
        """فاصله‌گذاری‌های اشتباه را در نشانه‌های سجاوندی اصلاح می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.punctuation_spacing('اصلاح ( پرانتزها ) در متن .')
            'اصلاح (پرانتزها) در متن.'

            >>> normalizer.punctuation_spacing('نسخه 0.5 در ساعت 22:00 تهران،1396')
            'نسخه 0.5 در ساعت 22:00 تهران، 1396'

            >>> normalizer.punctuation_spacing('اتریش ۷.۹ میلیون.')
            'اتریش ۷.۹ میلیون.'

        Args:
            text (str): متنی که باید فاصله‌گذاری‌های اشتباه آن در نشانه‌های سجاوندی اصلاح شود.

        Returns:
            (str): متنی با فاصله‌گذاری صحیحِ‌ نشانه‌های سجاوندی.
        """

        for pattern, repl in self.punctuation_spacing_patterns:
            text = pattern.sub(repl, text)
        return text

    def affix_spacing(self, text):
        """فاصله‌گذاری‌های اشتباه را در پسوندها و پیشوندها اصلاح می‌کند.

        Examples:
            >>> normalizer = Normalizer()
            >>> normalizer.affix_spacing('خانه ی پدری')
            'خانه‌ی پدری'

            >>> normalizer.affix_spacing('فاصله میان پیشوند ها و پسوند ها را اصلاح می کند.')
            'فاصله میان پیشوند‌ها و پسوند‌ها را اصلاح می‌کند.'

            >>> normalizer.affix_spacing('می روم')
            'می‌روم'

            >>> normalizer.affix_spacing('حرفه ای')
            'حرفه‌ای'

            >>> normalizer.affix_spacing('محبوب ترین ها')
            'محبوب‌ترین‌ها'

        Args:
            text (str): متنی که باید فاصله‌گذاری‌های اشتباهِ آن در پسوندها و پیشوندها اصلاح شود.

        Returns:
            (str): متنی با فاصله‌گذاری صحیحِ پیشوندها و پسوندها.
        """

        for pattern, repl in self.affix_spacing_patterns:
            text = pattern.sub(repl, text)
        return text

    def token_spacing(self, tokens):
        """توکن‌های ورودی را به فهرستی از توکن‌های نرمال‌سازی شده تبدیل می‌کند.

        در این فرایند ممکن است برخی از توکن‌ها به یکدیگر بچسبند؛
        برای مثال: `['زمین', 'لرزه', 'ای']` تبدیل می‌شود به: `['زمین‌لرزه‌ای']`

        Examples:
            >>> normalizer = Normalizer(token_based=True)
            >>> normalizer.token_spacing(['کتاب', 'ها'])
            ['کتاب‌ها']

            >>> normalizer.token_spacing(['او', 'می', 'رود'])
            ['او', 'می‌رود']

            >>> normalizer.token_spacing(['ماه', 'می', 'سال', 'جدید'])
            ['ماه', 'می', 'سال', 'جدید']

            >>> normalizer.token_spacing(['اخلال', 'گر'])
            ['اخلال‌گر']

            >>> normalizer.token_spacing(['پرداخت', 'شده', 'است'])
            ['پرداخت', 'شده', 'است']

            >>> normalizer.token_spacing(['زمین', 'لرزه', 'ای'])
            ['زمین‌لرزه‌ای']

        Args:
            tokens (List[str]): توکن‌هایی که باید نرمال‌سازی شود.

        Returns:
            (List[str]): لیستی از توکن‌های نرمال‌سازی شده به شکل `[token1, token2, ...]`.
        """

        result = []
        for t, token in enumerate(tokens):
            joined = False

            if result:
                token_pair = result[-1] + '‌' + token
                if token_pair in self.verbs or token_pair in self.words and self.words[token_pair][0] > 0:
                    joined = True

                    if t < len(tokens) - 1 and token + '_' + tokens[t + 1] in self.verbs:
                        joined = False

                elif token in self.suffixes and result[-1] in self.words:
                    joined = True

            if joined:
                result.pop()
                result.append(token_pair)
            else:
                result.append(token)

        return result

    def fix_tokens(self, tokens: List[str]):
        fixed_tokens = []
        jump = 0
        for ind, token in enumerate(tokens):
            if jump > 0:
                jump -= 1
                continue

            new_tokens = [token]

            if token.startswith('ف'):
                new_tokens = self.get_normalized_tokens(token, 'ا' + token, words_list=self.verbs)
            elif token.endswith('ا'):
                new_tokens = self.get_normalized_tokens(token, token + 'ه', words_list=self.words)
            elif token.startswith('ب'):
                new_tokens = self.get_normalized_tokens(token, 'و' + token[1:], words_list={**self.words, **self.verbs})
            elif token.endswith('ه'):
                new_tokens = self.get_normalized_tokens(token, token[:-1] + 'اه', words_list=self.words)
            # elif token.startswith('ک'):
            #     new_tokens = self.get_normalized_tokens(token, check_token=token[1:],
            #                                        new_tokens=['که', token[1:]], words_list=self.words)
            elif token in ['می', 'نمی'] and ind != len(tokens) - 1:
                if tokens[ind+1] in self.verbs:
                    new_token = token + '‌' + tokens[ind+1]
                    new_tokens = [new_token]
                    jump = 1

            fixed_tokens.extend(new_tokens)
        return fixed_tokens

    @staticmethod
    def apply_patterns(text, *patterns):
        import itertools
        patterns = list(itertools.chain(*patterns))
        for pattern, repl in patterns:
            text = pattern.sub(repl, text)
        return text

    @staticmethod
    def get_normalized_tokens(token, check_token, new_tokens=None, words_list=None):
        if token in words_list:
            return [token]

        if new_tokens is None:
            new_tokens = []

        if not isinstance(new_tokens, List):
            new_tokens = [new_tokens]

        if not new_tokens:
            new_tokens = [check_token]

        if check_token in words_list:
            return new_tokens
        elif check_token.startswith('ا') and 'آ' + check_token[1:] in words_list:
            new_tokens[1] = 'آ' + check_token[1:]
            return new_tokens
        else:
            return [token]
