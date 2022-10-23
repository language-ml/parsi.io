import re
from pathlib import Path
import numpy as np
from parstdex import Parstdex

from parsi_io.modules.event_extractor.address import AddressExtraction

resources_path = __file__.split('event_extractions.py')[0]


class EventExtractor:

    def __init__(self):

        def read_file(file):
            texts = []
            for word in file:
                text = word.rstrip('\n')
                texts.append(text)
            return texts

        # ______ time extraction from parstdex_____________________________
        self.time_extractor = Parstdex()

        # _________________ sources for political  events __________________________________________________________________
        agreement_ = read_file(open(f'{resources_path}/sources/agreement.txt', 'r', encoding='utf-8').readlines())
        contract_ = read_file(open(f'{resources_path}/sources/contract.txt', 'r', encoding='utf-8').readlines())
        removal_ = read_file(open(f'{resources_path}/sources/removal_installation.txt', 'r', encoding='utf-8').readlines())
        postfix = read_file(open(f'{resources_path}/sources/postfixs.txt', 'r', encoding='utf-8').readlines())
        country = read_file(open(f'{resources_path}/sources/country.txt', 'r', encoding='utf-8').readlines())

        self.postfixs = r'\b(' + r''.join([i + r'|' for i in postfix])[:-1] + r')\b'
        self.contract_verbs = r'\b(' + r''.join([i + r'|' for i in contract_])[:-1] + r')\b'
        self.removal_verbs = r'\b(' + r''.join([i + r'|' for i in removal_])[:-1] + r')\b'
        self.agreement_verbs = r'\b(' + r''.join([i + r'|' for i in agreement_])[:-1] + r')\b'
        self.countries = r'\b(' + r''.join([i + r'|' for i in country])[:-1] + r')\b'

        # ___________________ sources for sport events______________________________________________________________________
        sport_keyword = read_file(open(f'{resources_path}/sources/sport_key_words.txt', 'r', encoding='utf-8').readlines())
        geog_keywords = open(f'{resources_path}/sources/countries_cities.csv', 'r', encoding='utf-8').readlines()
        iran_geog_keywords = open(f'{resources_path}/sources/city_iran.csv', 'r', encoding='utf-8').readlines()
        geog_keyword = read_file(geog_keywords + iran_geog_keywords)
        self.max_allowded_space = 5

        self.sport_key_word = ''.join([i + '|' for i in sport_keyword if len(i) > 2])
        self.geog_key_word = ''.join([i.strip() + '|' for i in re.sub('\"|\'|\]|\[|u200c', '',
                                                                      str(geog_keyword).lower().replace('\\',
                                                                                                        ' ').replace(
                                                                          '  ', ' ')).split(',') if len(i) > 2])

    # ____________________ run function ________________________________________________________________
    def run(self, input, mode=0):

        # modes : 0: تمامی وقایع
        # modes : 1: گفتگو و مذاکرات و تووافق
        # modes : 2: قرارداد های رسمی
        # modes : 3: عزل و نصب و استعفا و انتخاب
        # modes : 4: تغییر قیمت
        # modes : 5: واردات و صادرات
        # modes : 6: مرگ
        # modes : 7: وقایع ورزشی

        out = []
        if mode in [0, 1]:
            res = self.agreement(input, self.postfixs, self.agreement_verbs, self.countries)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 2]:
            res = self.Contract(input, self.postfixs, self.contract_verbs, self.countries)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 3]:
            res = self.removal_installation(input, self.postfixs, self.removal_verbs, self.countries)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 4]:
            res = self.price_change(input)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 5]:
            res = self.import_export(input)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 6]:
            res = self.death(input)
            for output in res:
                if len(output["text"]) > 5:
                    # print(output)
                    out.append(output)

        if mode in [0, 7]:
            res = self.sports(input, self.sport_key_word)
            if res != 0:
                # print(res)
                out.append(res)
        return out

    # ______________ place detection function ____________________________________________________________________

    def location_extraction(self, line, geog_key_word):

        extractor = AddressExtraction()

        loc = {'address': [], 'address_span': []}

        # 'address' 'address_span'
        ex_result = extractor.run(line)

        if len(ex_result['address']) > 0:
            loc['address'] = ex_result['address']
            loc['address_span'] = ex_result['address_span']
        else:
            re_results = re.finditer(geog_key_word, line)
            for re_result in re_results:
                detected_loc = line[re_result.span()[0]:re_result.span()[1]]
                if len(detected_loc) > 1:
                    loc['address'].append(line[re_result.span()[0]:re_result.span()[1]])
                    loc['address_span'] += [re_result.span()[0], re_result.span()[1]]

        # if more than 1 loc
        if len(loc['address']) > 1:
            dar_in_loc = 'در'
            dar_span = []
            re_dar_results = re.finditer(dar_in_loc, line)
            for re_dar_result in re_dar_results:
                detected_dar = line[re_dar_result.span()[0]:re_dar_result.span()[1]]
                if len(detected_dar) > 1:
                    dar_span += [re_dar_result.span()[0], re_dar_result.span()[1]]

            real_locs = []
            real_locs_span = []
            for span in dar_span[::2]:
                temp = (np.array(loc['address_span'][::2]) - span)
                temp[temp < 0] = len(line)

                if np.min(temp) != len(line) and np.min(temp) < self.max_allowded_space:
                    real_loc = np.argmin(temp)
                    real_locs.append(loc['address'][real_loc])
                    real_locs_span += [loc['address_span'][2 * real_loc], loc['address_span'][2 * real_loc + 1]]
            if len(real_locs) > 0:
                return dict({'address': real_locs, 'address_span': real_locs_span})

        if len(loc['address']) == 0:
            loc['address'] = ['']
            loc['address_span'] = ['']
        return loc

    # ________________ political events function ____________________________________________________________
    def agreement(self, input, postfix, key_verbs, key_countries):

        key_words = r"\b(مذاکر|توافق|گفتگو|گفت و گو|گفت‌و‌گو)\s*((ه|ات|ها|های)\s*)*\b"
        parties = f"(بین|میان)?\s*{key_countries}\s*و\s*{key_countries}\s*(و\s*{key_countries}\s*)*"
        description = r"\b(بر سر|درمورد)\b"
        names = r"\b(صلح|آتش بس|تحریم|تحریم های|اولیه|نهایی|همکاری|چندجانبه|چند جانبه|دو طرفه|مربوط به|صلح جهانی|برجام|مفاد|عهد نامه|اقتصادی|نظامی|جنگی)\b"
        pattern_1 = f"\s*({parties})(\s*{description})?(\s*{names})*\s*{key_verbs}(\s*{postfix})+"
        pattern_2 = f"\s*({key_words})(\s*{names})*(\s*{key_countries})*(\s*{parties})?(\s*{description})?(\s*{names})*"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append(
                    {'type': 'گفتگو و مذاکرات و توافق', 'text': input[start:end], 'span': [start, end], 'place': loc,
                     'time': time[i]})
            else:
                output.append(
                    {'type': 'گفتگو و مذاکرات و توافق', 'text': input[start:end], 'span': [start, end], 'place': loc,
                     'time': ''})

        return output

    def Contract(self, input, postfix, key_verbs, key_countries):

        starter = r"\b(امضاء|امضای|عقد|اجرای|انعقاد|لغو|توافق بر سر)\b"
        key_words = r"\b(پیمان|قرارداد|عهد نامه|قطع نامه|تعهد نامه|قرار داد)\b"
        parties = f"(بین|میان)?\s*{key_countries}\s*و\s*{key_countries}\s*(و\s*{key_countries}\s*)*"
        description = r"\b(را|بر سر|درمورد)\b"
        names = r"\b(صلح|آتش بس|تحریم|تحریم های|اولیه|نهایی|همکاری|چندجانبه|چند جانبه|دو طرفه|مربوط به|صلح جهانی|برجام|مفاد|عهد نامه|نظامی|جنگی|اقتصادی|برون مرزی|بین المللی|منطقه ای|سازمان ملل)\b"
        pattern_1 = f"(\s*{parties})(\s*{description})?(\s*{key_words})*(\s*[0-9]+)*(\s*{names})*(\s*{description})?(\s*{key_verbs})(\s*{postfix})+"
        pattern_2 = f"(\s*{starter})(\s*{key_words})(\s*[0-9]+)*(\s*{names})*(\s*{parties})?"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append({'type': 'قرارداد های رسمی', 'text': input[start:end], 'span': [start, end], 'place': loc,
                               'time': time[i]})
            else:
                output.append({'type': 'قرارداد های رسمی', 'text': input[start:end], 'span': [start, end], 'place': loc,
                               'time': ''})

        return output

    def removal_installation(self, input, postfix, key_verbs, key_countries):

        key_words = r"\b(عزل|نصب|استعفا|استعفای|انتخاب|استیضاح|برکناری|جایگزینی|انتصاب|کناره گیری)\b"
        key_positions = r"\b(نسخت وزیر|جمهور|ریاست|جمهوری|نخست وزیر|نخست‌وزیر|رئیس|سپاه|ارتش|ارگان|اداره|ادارات|رهبر|مقام|منصب|فرمانده|مسئولیت|کشور|جمهور|مسئول|مجلس|قوه|قضائیه|مجریه|مقننه|ملکه|پادشاه|ولیعهد|جانشین|سمت|مقام|سازمان|ملل)\b"
        description = r"\b(را|برای|به عنوان|از|خود|خویش|به)\b"

        pattern_1 = f"(\s*{key_words})(\s*{key_positions})+(\s*{key_countries})*(\s*{description})*(\s*{key_countries})*(\s*{description})*"
        pattern_2 = f"(\s*{key_positions})+(\s*{key_countries})*(\s*{description})*(\s*{key_positions})*(\s*{key_countries})*(\s*{description})*(\s*{key_verbs})(\s*{postfix})+"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append({'type': 'عزل و نصب و استعفا و انتخاب', 'text': input[start:end], 'span': [start, end],
                               'place': loc, 'time': time[i]})
            else:
                output.append({'type': 'عزل و نصب و استعفا و انتخاب', 'text': input[start:end], 'span': [start, end],
                               'place': loc, 'time': ''})

        return output

    # _____________________ price change, import,export and death functions____________________________________________________
    def price_change(self, input):
        change_infinitive = r"\b(افزایش|کاهش|رشد|صعود|نزول|بالا رفتن|پایین آمدن|[\w\u200c]+ برابر شدن)\b"
        percentage_p1 = r"\b([\w\u200c]+ درصدی)\b"
        value_keyword = r"\b(قیمت|ارزش|بها|بهای)\b"
        products = r"([\w\u200c]+((، [\w\u200c]+)*( و [\w\u200c]+))?)"
        change_keyword = r"\b(افزایش|کاهش|گران|ارزان|بالا|پایین|[\w\u200c]+ برابر)\b"
        change_verb = r"\b(یافت|می‌یابد|یافته است|کرد|می‌کند|کرده است|رفت|می‌رود|رفته‌است|آمد|می‌آید|آمده است|شد|می‌شود|شده است)\b"
        percentage_p2 = r"\b([\w\u200c]+ درصد)\b"

        pattern_1 = f"(({change_infinitive}\s*({percentage_p1}\s*)?{value_keyword}\s*)|((گران شدن|ارزان شدن)\s*({percentage_p1}\s*)?)){products}"
        pattern_2 = f"({value_keyword}\s*)?{products}\s*({percentage_p2}\s*)?{change_keyword}\s*{change_verb}"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append({'type': 'تغییر قیمت', 'text': input[start:end], 'span': [start, end], 'place': loc,
                               'time': time[i]})
            else:
                output.append(
                    {'type': 'تغییر قیمت', 'text': input[start:end], 'span': [start, end], 'place': loc, 'time': ''})

        return output

    def import_export(self, input):
        change_keywords = r"\b(افزایش|کاهش|صعود|نزول|بالا رفتن|پایین آمدن|[\w\u200c]+ برابر)\b"
        inex_infinitive = r"\b(واردات|صادرات|وارد کردن|صادر کردن)\b"
        adjectives = r"\b(بی رویه|ناکافی|بیش از اندازه)\b"
        products = r"([\w\u200c]+((، [\w\u200c]+)*( و [\w\u200c]+))?)"
        sord = r"\b((از|به)\s*[\w\u200c]+)\s*\b"
        inex_keywords = r"\b(صادر|وارد)\b"
        inex_verbs = r"\b(شد|شدند|می‌شود|می‌شوند|شده است|شده‌اند|کرد|کردند|می‌کند|می‌کنند|کرده است|کرده‌اند)\b"

        pattern_1 = f"({change_keywords}\s*)?{inex_infinitive}\s*({adjectives}\s*)?{products}(\s*{sord})*"
        pattern_2 = f"{products}\s*(را)?\s*({sord})*\s*{inex_keywords}\s*{inex_verbs}"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append({'type': 'واردات و صادرات', 'text': input[start:end], 'span': [start, end], 'place': loc,
                               'time': time[i]})
            else:
                output.append({'type': 'واردات و صادرات', 'text': input[start:end], 'span': [start, end], 'place': loc,
                               'time': ''})

        return output

    def death(self, input):
        death_infinitive = r"\b(وفات|مرگ|فوت|درگذشت|شهادت|عروج|جان باختن|کشته شدن|به قتل رسیدن|از دست رفتن)\b"
        death_verb = r"\b(فوت کرد|مرد|درگذشت|به شهادت رسید|شهید شد|به دیار باقی شتافت|جان باخت|جان به جان آفرین تسلیم کرد|کشته شد|به قتل رسید|دار فانی را وداع گفت|به دیدار حق شتافت|را از دست دادیم)(ند)?\b"
        people = r"([\w\u200c]+ تن|[\w\u200c]+ نفر)\s*(از [\w\u200c]+)?"
        description = r"\b(امام|شهید|آقای|خانم|آیت‌الله)\b"
        prayers = r"\b(رحم الله علیه|علیه السلام)\b"
        death_cause = r"\b(در اثر|بر اثر|به دلیل|به سبب|پس از)\b[\w\u200c\s]+"
        names = r"[\w\u200c][\w\u200c][\w\u200c]+"

        pattern_1 = f"{death_infinitive}\s*(({description}\s*)?{names}(\s*{prayers})?|{people})(\s*{death_cause})?"
        pattern_2 = f"(({description}\s*)?{names}\s*({prayers})?|{people})(\s*{death_cause})?\s*{death_verb}"
        pattern = f"({pattern_1})|({pattern_2})"

        time = list(self.time_extractor.extract_marker(input)["date"].values())
        len_time = len(time)
        location = self.location_extraction(input, self.geog_key_word)

        output = []
        for i, m in enumerate(re.finditer(pattern, input)):
            start, end = m.span()
            loc = ''
            if len(location['address'][0]) > 0 and (
                    location['address_span'][0] > end or location['address_span'][1] < start):
                loc = location['address'][0]
            if i < len_time:
                output.append(
                    {'type': 'مرگ', 'text': input[start:end], 'span': [start, end], 'place': loc, 'time': time[i]})
            else:
                output.append({'type': 'مرگ', 'text': input[start:end], 'span': [start, end], 'place': loc, 'time': ''})

        return output

    # ___________________sport events function_______________________________________________________________
    def sports(self, line, sport_key_word):

        line_key_start_span_list = []
        line_key_end_span_list = []
        line_keys = []

        key_verbs = r'است|کرد|شد|بود'
        sub_key_1 = 'برد|باخت|تساوی'  # type = 'برد و باخت و تساوی'
        sub_key_2 = 'صعود|سقوط|حذف'  # type = 'صعود و سقوط و حذف'
        sub_key_3 = 'قهرمان|نایب قهرمان'  # type = 'قهرمان و نایب قهرمان'
        sub_key_4 = 'مدال'  # type = 'کسب مدال'
        types = ['برد و باخت و تساوی', 'صعود و سقوط و حذف', 'قهرمان و نایب قهرمان', 'کسب مدال']

        keys = re.finditer(sport_key_word, line)

        is_it_about_sport = False
        for k in keys:

            if (k.span()[1] - k.span()[0]) > 1:
                is_it_about_sport = True

                line_keys.append(line[k.span()[0]:k.span()[1]])
                line_key_start_span_list += [k.span()[0]]
                line_key_end_span_list += [k.span()[1]]
        if not is_it_about_sport:
            return 0

        line_key_start_span = line_key_start_span_list[np.argmin(line_key_start_span_list)]
        line_key_end_span = line_key_end_span_list[np.argmax(line_key_end_span_list)]

        line_verbs_span = []
        verbs = re.finditer(key_verbs, line)

        for v in verbs:
            line_verbs_span = line[v.span()[0]:v.span()[1]]

            if (v.span()[1] - v.span()[0]) > 1:

                if v.span()[0] - line_key_end_span < 3 * self.max_allowded_space:  # 3 words
                    line_key_end_span = v.span()[1]

        # detecting the type

        result_types = []

        result_types.append(len([i for i in re.finditer(sub_key_1, line) if (i.span()[1] - i.span()[0]) > 1]))
        result_types.append(len([i for i in re.finditer(sub_key_2, line) if (i.span()[1] - i.span()[0]) > 1]))
        result_types.append(len([i for i in re.finditer(sub_key_3, line) if (i.span()[1] - i.span()[0]) > 1]))
        result_types.append(len([i for i in re.finditer(sub_key_4, line) if (i.span()[1] - i.span()[0]) > 1]))

        result = dict({"line": line, "type": '', "text": '', "span": None, "place": '', "time": ''})

        result['type'] = types[np.argmax(result_types)]
        result['span'] = [line_key_start_span, line_key_end_span]
        result['text'] = line[line_key_start_span: line_key_end_span]

        # detecting locations
        loc = self.location_extraction(line, self.geog_key_word)
        result['place'] = loc['address']

        time = list(self.time_extractor.extract_marker(line)["datetime"].values())
        time_dict = dict({'time': time})
        result['time'] = time_dict['time']

        return result
