import re


class DateExtractor:
    def __init__(self):
        self.pre = ['از', 'شروع']
        self.pos = ['تا', 'تمام', 'تموم', 'پایان', 'ددلاین', 'ددلاین تسک']
        self.week = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        self.month = ['مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد',
                      'شهریور']
        self.spec_numbers = ['یک', 'دو', 'سه', 'چهار', 'پنج', 'شش', 'هفت', 'هشت', 'نه', 'ده', 'یازده', 'دوازده',
                             'سیزده', 'چهارده', 'پانزده', 'شانزده', 'هفده', 'هجده', 'نوزده', 'بیست', 'بیست و یک',
                             'بیست و دو', 'بیست و سه', 'بیست و چهار', 'بیست و پنج', 'بیست و شش', 'بیست و هفت',
                             'بیست و هشت', 'بیست و نه', 'سی',
                             '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                             '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        self.holiday = ['عید', 'تابستون', 'زمستون', 'کریسمس', 'بهار', 'پاییز', 'امروز', 'فردا', 'محرم']
        self.ordinal_numbers = ['یکم', 'دوم', 'سوم', 'چهارم', 'پنجم', 'ششم', 'هفتم', 'هشتم', 'نهم', 'دهم',
                                'یازدهم', 'دوازدهم', 'سیزدهم', 'چهاردهم', 'پانزدهم', 'شانزدهم', 'هفدهم', 'هجدهم',
                                'نوزدهم', 'بیستم', 'بیست و یکم', 'بیست و دوم', 'بیست و سوم', 'بیست و چهارم',
                                'بیست و پنجم', 'بیست و ششم', 'بیست و هفتم', 'بیست و هشتم', 'بیست و نهم', 'سی‌ام',
                                'سی و یکم']
        self.farsi_numbers = ['۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۱۰', '۱۱', '۱۲', '۱۳', '۱۴', '۱۵', '۱۶',
                              '۱۷', '۱۸', '۱۹', '۲۰', '۲۱', '۲۲', '۲۳', '۲۴', '۲۵', '۲۶', '۲۷', '۲۸', '۲۹', '۳۰', '۳۱']
        self.start_time_change_pattern = (r'(شروع|استارت).*?(کار|تسک|ددلاین)?.*?(منتقل شد|انتقال یافت|عوض شد|تغییر '
                                          r'کرد)?.*?به (.*?)(منتقل شد|انتقال یافت|عوض شد|تغییر کرد)')
        self.end_time_change_pattern = (r'(پایان|ددلاین|مهلت|اتمام).*?(کار|تسک|ددلاین)?.*?(منتقل شد|انتقال یافت|عوض '
                                        r'شد|تغییر کرد)?.*?به (.*?)(اضافه شد|منتقل شد|انتقال یافت|عوض شد|تغییر کرد)')

    def extract_date(self, text, is_start: bool):
        numbers = self.spec_numbers + self.farsi_numbers + self.ordinal_numbers
        text = text.split()
        prepositions = self.pre if is_start else self.pos
        for i, word in enumerate(text):
            if word in prepositions:
                if i < len(text) - 1:  # check the word after
                    next_word = text[i + 1]
                    if next_word in self.week or next_word in self.holiday:
                        return next_word
                    elif next_word in self.month and i < len(text) - 1:  # check the word after the number
                        next2_word = text[i + 2]
                        try:
                            float_next = float(next2_word)
                            is_number = True
                        except ValueError:
                            is_number = False
                        if next2_word == 'امسال':
                            is_number = True
                        if is_number:
                            return next_word + ' ' + next2_word
                        else:
                            return next_word
                    elif next_word in numbers and i < len(text) - 1:  # check the word after the number
                        if (next_word == 'بیست' or next_word == 'سی') and text[i + 2] == 'و':
                            next2_word = text[i + 2]
                            next3_word = text[i + 3]
                            next4_word = text[i + 4]
                            if next4_word in self.month:
                                return next_word + ' ' + next2_word + ' ' + next3_word + ' ' + next4_word
                            else:
                                return next_word + ' ' + next2_word + ' ' + next3_word
                        next2_word = text[i + 2]
                        next3_word = text[i + 3]
                        try:
                            float_next = float(next3_word)
                            is_number = True
                        except ValueError:
                            is_number = False
                        if next3_word == 'امسال':
                            is_number = True
                        if next2_word in self.month and is_number:
                            return next_word + ' ' + next2_word + ' ' + next3_word
                        elif next2_word in self.month:
                            return next_word + ' ' + next2_word
                        else:
                            return next_word
                if i > 0:  # check the word before
                    prev_word = text[i - 1]
                    try:
                        float_next = float(prev_word)
                        is_number = True
                    except ValueError:
                        is_number = False
                    if prev_word == 'امسال':
                        is_number = True
                    if prev_word in self.week or prev_word in self.holiday:
                        return prev_word
                    elif is_number:  # check the word after the number
                        prev2_word = text[i - 2]
                        prev3_word = text[i - 3]
                        if prev2_word in self.month and prev3_word in numbers:
                            return prev3_word + ' ' + prev2_word + ' ' + prev_word
                        elif prev2_word in self.month:
                            return prev2_word + ' ' + prev_word
                        else:
                            return prev_word
                    elif prev_word in self.month and i > 1:  # check the word after the number
                        prev2_word = text[i - 2]
                        prev3_word = text[i - 3]
                        prev4_word = text[i - 4]
                        if prev3_word == 'و' and (prev4_word == 'بیست' or prev4_word == 'سی'):
                            if prev2_word in numbers:
                                return prev4_word + ' ' + prev3_word + ' ' + prev2_word + ' ' + prev_word
                            else:
                                return prev_word
                        if prev2_word in numbers:
                            return prev2_word + ' ' + prev_word
                        else:
                            return prev_word
        return ''

    def extract_start_time_change(self, text):
        match = re.search(self.start_time_change_pattern, text)
        if match:
            return match.group(4).strip()
        else:
            return None

    def extract_end_time_change(self, text):
        match = re.search(self.end_time_change_pattern, text)
        if match:
            return match.group(4).strip()
        else:
            return None


if __name__ == '__main__':
    date_extractor = DateExtractor()
    text = 'لطفا این کار رو در یک خرداد شروع کنید و حتما تا پاییز کار تموم باشه دیگع.'
    print(date_extractor.extract_date(text, True))
    print(date_extractor.extract_date(text, False))

    text = 'شروع کار به 7 مهر منتقل شد'
    print(date_extractor.extract_start_time_change(text))
    text = 'ددلاین کار به 5 مهر منتقل شد'
    print(date_extractor.extract_end_time_change(text))
