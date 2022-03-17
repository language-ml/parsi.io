import re
from parsi_io.modules.parstdex.utils import const


class ValueExtractor:
    SHAMSHI_MONTHS = const.SHAMSHI_MONTHS
    GHAMARI_MONTHS = const.GHAMARI_MONTHS
    MILADI_MONTHS = const.MILADI_MONTHS

    ONES_TEXT = const.ONES_TEXT
    TENS_TEXT = const.TENS_TEXT
    TEN_PLUS_TEXT = const.TEN_PLUS_TEXT
    HUNDREDS_TEXT = const.HUNDREDS_TEXT
    MAGNITUDE = const.MAGNITUDE

    TYPO_LIST = const.TYPO_LIST

    FA_TO_EN = const.FA_TO_EN

    MINUTES = const.MINUTES
    HOUR_PART = const.HOUR_PART

    HOUR_PART_JOIN = "|".join(
        HOUR_PART.keys()
    )

    NEG_DURATION_JOIN = "|".join(
        ["به", "مانده به", "قبل", "قبل از", "پیش از"]
    )

    POS_DURATION_JOIN = "|".join(
        ["بعد", "پس از", "بعد از"]
    )

    DAY_PART_JOIN = '|'.join(
        ["شب", "شامگاه", "غروب", "بعد از ظهر", "بعدازظهر", "بعداز ظهر", "عصر", "صبح", "بامداد", "ظهر"]
    )
    PM_PART_LIST = ["شب", "شامگاه", "غروب", "بعد از ظهر", "بعدازظهر", "بعداز ظهر", "عصر"]

    SHAMSI_LIST = '|'.join(list(SHAMSHI_MONTHS.keys()))
    GHAMARI_LIST = '|'.join(list(GHAMARI_MONTHS.keys()))
    MILADI_LIST = '|'.join(list(MILADI_MONTHS.keys()))
    ALL_MONTHS = SHAMSI_LIST + '|' + GHAMARI_LIST + '|' + MILADI_LIST
    MINUTES_LIST = '|'.join(list(MINUTES.keys())[::-1])

    FA_NUMBERS = "۰|۱|۲|۳|۴|۵|۶|۷|۸|۹"
    EN_NUMBERS = "0|1|2|3|4|5|6|7|8|9"
    Symbols = ":|/|-"
    C_NUMBERS = FA_NUMBERS + "|" + EN_NUMBERS + "|" + Symbols
    MONTH_LIT = 'ماه'
    YEAR_LIT = 'سال'
    HOUR_LIT = 'ساعت'
    MIN_LIT = 'دقیقه'
    SEC_LIT = 'ثانیه'
    DATE_JOINER = '-|/'
    TIME_JOINER = ':'

    JOINER = 'و'

    Date_Units = "|".join(
        list(TEN_PLUS_TEXT.keys()) + list(HUNDREDS_TEXT.keys()) + list(MAGNITUDE.keys()) + list(
            TENS_TEXT.keys()) + list(
            ONES_TEXT.keys()) + list(TYPO_LIST.keys()))

    ONES_LIST = "|".join(list(ONES_TEXT.keys()))
    TEN_PLUS_LIST = "|".join(list(TEN_PLUS_TEXT))
    TENS_LIST = "|".join(list(TENS_TEXT.keys()))

    def normalize_numbers(self, text):
        """
        normalize_numbers converts persian digits into corresponding english digit
        :param text: str
        :return: str
        """
        pattern = "|".join(map(re.escape, self.FA_TO_EN.keys()))
        return re.sub(pattern, lambda m: self.FA_TO_EN[m.group()], str(text))

    def normalize_space(self, text):
        """
        normalize spaces
        :param text:
        :return:
        """
        res_space = re.sub(fr'((?:{self.C_NUMBERS})+(\.(?:{self.C_NUMBERS})+)?)', r' \1 ', text)
        res_space = ' '.join(res_space.split())
        return res_space

    def tokenize(self, text):
        for typo in self.TYPO_LIST.keys():
            if typo in text:
                text = text.replace(typo, self.TYPO_LIST[typo])
        slitted_text = text.split(' ')
        slitted_text = [txt for txt in slitted_text if txt != self.JOINER]

        return slitted_text

    @staticmethod
    def remove_ordinal_suffix(text):
        word = text.replace('مین', '')
        word = word.replace(' ام', '')
        word = word.replace(' اُم', '')

        if word.endswith('سوم'):
            return word[:-3] + 'سه'
        elif word.endswith('م'):
            return word[:-1]
        return word

    def compute_date(self, tokens):
        """
        it takes persian year and converts it into corresponding value
        :param tokens: str
        :return: int
        """
        result = 0
        for token in tokens:
            if self.ONES_TEXT.get(token):
                result += self.ONES_TEXT[token]
            if self.TEN_PLUS_TEXT.get(token):
                result += self.TEN_PLUS_TEXT[token]
            if self.TENS_TEXT.get(token):
                result += self.TENS_TEXT[token]
            elif self.HUNDREDS_TEXT.get(token):
                result += self.HUNDREDS_TEXT[token]
            elif token.isdigit():
                result += int(token)
            elif self.MAGNITUDE.get(token):
                result = result * self.MAGNITUDE[token] if result != 0 else self.MAGNITUDE[token]

        return result

    def convert_word_to_digits(self, text):
        """
        convert_word_to_digits will apply preprocess needed to convert text into tokens appropriate for compute_date method
        :param text: str
        :return: int
        """
        if text == '' or text is None or text == ' ':
            return ' '

        if self.normalize_space(text) == self.JOINER:
            return ' ' + self.JOINER + ' '

        text_date = self.remove_ordinal_suffix(text)
        computed = self.compute_date(self.tokenize(text_date))
        return computed

    def date_reformat(self, text):
        try:
            # First regex covers following formats:
            # ۲۳ آبان ماه سال ۱۳۵۴
            # ۲۳ ماه آبان سال ۱۳۵۴
            date_format_num1 = fr'(\d+)\s*[(?:\b{self.MONTH_LIT})]*\s*(\b{self.ALL_MONTHS})\s*[(?:\b{self.MONTH_LIT})]*\s*[(?:\b{self.YEAR_LIT})]* (\d+)'
            day_month_year = re.search(date_format_num1, text).groups()

            day = int(day_month_year[0])
            month = day_month_year[1]
            year = int(day_month_year[2])

            if month in self.MILADI_MONTHS.keys():
                month_index = self.MILADI_MONTHS[month]
                return f'{day:02}/{month_index:02}/{year}'
            elif month in self.GHAMARI_MONTHS.keys():
                # TODO : Improve offset 1400:
                # if the shamsi year is lower than 100 then assume it has 13 before it
                if day < 100 and year < 100:
                    # year += 1400
                    pass
                month_index = self.GHAMARI_MONTHS[month]
                return f'{year}/{month_index:02}/{day:02}ه.ق  '
            elif month in self.SHAMSHI_MONTHS.keys():
                # TODO : Improve offset 1300:
                # if the shamsi year is lower than 100 then assume it has 13 before it
                if day < 100 and year < 100:
                    # year += 1300
                    pass
                month_index = self.SHAMSHI_MONTHS[month]
                return f'{year}/{month_index:02}/{day:02}'
            else:
                return f'{year}/{month}/{day:02}'
        except:
            pass

        try:
            # Second regex covers following formats:
            # 1375-02-04
            date_format_num2 = fr'(\d+)\s*[(?:\b{self.DATE_JOINER})]\s*(\d+)\s*[(?:\b{self.DATE_JOINER})]\s*(\d+)'
            detected_date = re.search(date_format_num2, text).groups()

            year = int(detected_date[0])
            month = int(detected_date[1])
            day = int(detected_date[2])

            # TODO : Improve these constraints for different days:
            # if year is lower than 100 then assume it has 13 before it
            if day < 100 and year < 100:
                # year += 1300
                pass
            # assume the greater value as year
            if day > year or 'میلادی' in text:
                year, day = day, year

            # ghamari
            if 'قمری' in text:
                return f'{year}/{month:02}/{day:02}ه.ق  '
            # miladi date:
            if year > 1800 or 'میلادی' in text:
                return f'{day:02}/{month:02}/{year:02}'
            # shamsi date
            else:
                return f'{year:02}/{month:02}/{day:02}'
        except:
            return None

    def time_reformat(self, text):
        """
        Reformat time markers as mentioned in the examples.
        :param text: str
        :return: str
        """
        # example: ساعت 00:13:42
        PM = False
        for part_night in self.PM_PART_LIST:
            if part_night in text:
                PM = True

        # example: بیست دقیقه قبل از هفت
        try:
            reg = fr'(\d+)\s*(?:{self.MIN_LIT})\s*(?:{self.NEG_DURATION_JOIN})\s*(?:{self.HOUR_LIT})?\s*(\d+)\s*(?:{self.DAY_PART_JOIN})?'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[1]) - 1
            minute = int(detected_time[0])
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{(60 - minute):02}'
        except:
            pass

        # example: بیست دقیقه بعد از هفت
        try:
            reg = fr'(\d+)\s*(?:{self.MIN_LIT})\s*(?:{self.POS_DURATION_JOIN})\s*(?:{self.HOUR_LIT})?\s*(\d+)\s*(?:{self.DAY_PART_JOIN})?'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[1])
            minute = int(detected_time[0])
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}'
        except:
            pass

        # example: یه ربع به شش
        try:
            reg = fr'({self.HOUR_PART_JOIN})\s*(?:{self.HOUR_LIT})?\s*(?:{self.NEG_DURATION_JOIN})\s*(?:{self.HOUR_LIT})?\s*(\d+)\s*(?:{self.DAY_PART_JOIN})?'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[1]) - 1
            minute = self.HOUR_PART[detected_time[0]]
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{(60 - minute):02}'
        except:
            pass

        # example: یه ربع بعد شش
        try:
            reg = fr'({self.HOUR_PART_JOIN})\s*(?:{self.HOUR_LIT})?\s*(?:{self.POS_DURATION_JOIN})\s*(?:{self.HOUR_LIT})?\s*(\d+)\s*(?:{self.DAY_PART_JOIN})?'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[1])
            minute = self.HOUR_PART[detected_time[0]]
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}'
        except:
            pass

        # example: ساعت ۰۹:۳۴
        try:
            reg = fr'(?:{self.HOUR_LIT})?\s*(\d+)(?:[{self.TIME_JOINER}])(\d*)\s*(?:[{self.TIME_JOINER}])?(\d*)?'

            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[0])
            minute = int(detected_time[1])
            second = int(detected_time[2] if detected_time[2] != '' else "0")
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}:{second:02}'
        except:
            pass

        # example: ساعت بیست و یک و چهل و دو دقیقه و سی و دو ثانیه
        try:
            reg = fr'(?:{self.HOUR_LIT})\s+(\d+)\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.MIN_LIT})?\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.SEC_LIT})?'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[0])
            minute = int(detected_time[1] if detected_time[1] != '' else "0")
            second = int(detected_time[2] if detected_time[2] != '' else "0")
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}:{second:02}'
        except:
            pass

        # example: ساعت 23 دقیقه و 40 ثانیه
        try:
            reg = fr'(?:{self.HOUR_LIT})\s+(\d+)\s*(?:{self.MIN_LIT})\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.SEC_LIT})?'
            detected_time = re.search(reg, text).groups()
            hour = 0
            minute = int(detected_time[0])
            second = int(detected_time[1])
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}:{second:02}'
        except:
            pass

        # example: بیست و یک و چهل و دو دقیقه و سی و دو ثانیه صبح
        try:
            reg = fr'(\d+)\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.MIN_LIT})?\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.SEC_LIT})?\s+(?:{self.DAY_PART_JOIN})'
            detected_time = re.search(reg, text).groups()
            hour = int(detected_time[0])
            minute = int(detected_time[1] if detected_time[1] != '' else "0")
            second = int(detected_time[2] if detected_time[2] != '' else "0")
            if hour < 13 and PM == True:
                hour = hour + 12
            return f'{hour:02}:{minute:02}:{second:02}'
        except:
            pass

        # example: 23 دقیقه و 40 ثانیه شب
        try:
            reg = fr'(\d+)\s*(?:{self.MIN_LIT})\s*[{self.JOINER}]?\s*(\d*)\s*(?:{self.SEC_LIT})?\s+(?:{self.DAY_PART_JOIN})'
            detected_time = re.search(reg, text).groups()
            hour = 0
            minute = int(detected_time[0])
            second = int(detected_time[1])
            if hour < 13 and PM:
                hour = hour + 12
            return f'{hour:02}:{minute:02}:{second:02}'
        except:
            return None

    def compute_date_value(self, text):
        """
        takes time marker and converts it into '{hour:02}:{minute:02}:{second:02}'
        :param text: str
        :return: str
        """
        text = self.normalize_numbers(text)
        res = re.sub(fr'\b(?:{self.Date_Units}|\s{self.JOINER}\s|\s|\d{1, 4})+\b',
                     lambda m: str(self.convert_word_to_digits(m.group())), text)
        # 23هزار -> 23 هزار
        res = self.normalize_space(res)
        res = self.date_reformat(res) if self.date_reformat(res) is not None else res
        res = self.normalize_space(res)
        return res

    def compute_time_value(self, text):
        """
        find time appropriate time markers and evaluate time marker as {hour:02}:{minute:02}:{second:02}
        :param text: str
        :return: str
        """
        text = self.normalize_numbers(text)
        res = re.sub(fr'\b(?:{self.MINUTES_LIST})\b', lambda m: str(self.MINUTES[m.group()]), str(text))
        res = self.normalize_space(res)
        res = self.time_reformat(res) if self.time_reformat(res) is not None else res
        return res


    def compute_value(self, text):

        text = self.normalize_numbers(text)

        #time part
        res_time = re.sub(fr'\b(?:{self.MINUTES_LIST})\b', lambda m: str(self.MINUTES[m.group()]), str(text))
        res_time = self.normalize_space(res_time)
        res_time = self.time_reformat(res_time)

        # if time doesnot work then try date: time reformat is more cautious the date reformat.
        if res_time:
            res = res_time
        else:
            res_date = self.normalize_space(text)
            res = self.compute_date_value(res_date)

        return res