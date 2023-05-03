import re
import pickle
from resources.location import LatLong

class AddressExtractor(object):

    def __init__(self):
        self.resources = "parsi_io/modules/address_extractor/resources"
        self.__load_dicts()
        self.latlon = LatLong()
        self.abbreviates = {
            "پ": "پلاک",
            "خ": "خیابان",
            "م": "میدان",
        }
        self.ez_address_identifier = "ادرس|آدرس|نشانی"
        self.non_starter_addresskeywords = "منطقه|طبقه|کوچه|بن‌بست|بنبست|بن بست|پلاک|واحد|بلوک|برج"
        self.non_starter_address_keywords_regex =\
             r"\b(منطقه|طبقه|کوچه|بن‌بست|بنبست|بن بست|پلاک|واحد|بلوک|برج)\b"
        self.relational_addresskeywords = "جنب|رو به رو|رو به روی|روبه‌رو|روبه‌روی|روبروی|روبرو|بالاتر از|پایین‌تر از|پایین‌ تر از|قبل از|بعد از|نبش"
        self.relational_address_keywords_regex =\
             r"\b(جنب|رو به رو|رو به روی|روبه‌رو|روبه‌روی|روبروی|روبرو|بالاتر از|پایین‌تر از|پایین‌ تر از|قبل از|بعد از|نبش)\b"
        self.separators = "،|-|,"
        self.start_addresskeywords = "تقاطع|منطقه‌ی|بعد از|منطقه ی|دانشگاه|مدرسه|منطقه|خیابون|خیابان|بلوار|میدون|میدان|بزرگ‌راه|بزرگراه|آزادراه|آزاد راه|اتوبان|محله‌ی|محله ی|جاده|محله|کوی|چهارراه|چهار راه|سه‌راه|سراه|سه‌ راه|شهر|کشور|استان|شهرستان|دهستان|روستای|شهرک|حومه‌ی|حومه ی|حومه|پل"
        self.start_address_keywords_regex =\
            r"\b(تقاطع|منطقه‌ی|بعد از|منطقه ی|منطقه|خیابون|خیابان|بلوار|میدون|میدان|بزرگ‌راه|بزرگراه|آزادراه|آزاد راه|اتوبان|محله‌ی|محله ی|جاده|محله|کوی|چهارراه|چهار راه|سه‌راه|سراه|سه‌ راه|شهر|کشور|استان|شهرستان|دهستان|روستای|شهرک|حومه‌ی|حومه ی|حومه|پل)\b"
        self.locations = f"{self.countries}|{self.cities}|{self.province}"
        self.middle_address_keywords = f"{self.start_address_keywords_regex}|{self.non_starter_address_keywords_regex}|{self.relational_address_keywords_regex}"
        self.starter_keywords = f"({self.ez_address_identifier}|{self.start_address_keywords_regex}|{self.locations})"
        self.pattern = f"({self.starter_keywords})([^\\.]{{{{{{spaces_count}}}}}}({self.middle_address_keywords}|{self.separators})){{{{{{keyword_count}}}}}}( *({self.places})? *\w+)"
    
    def __load_dicts(self):

        with open("{0}/ambiguity_countries.csv".format(self.resources), "r", encoding='utf8') as f:
            self.ambiguity_countries = {
                line.replace("\n", "").strip().split(",")[0]:
                int(line.replace("\n", "").strip().split(",")[1])
                for line in f.readlines()}
        with open("{0}/countries.pickle".format(self.resources), "rb") as f:
            countries = [str(num) for num in pickle.load(f)]
            self.countries = "\\b(" + '|'.join(countries) + ")\\b"

        with open("{0}/provinces.pickle".format(self.resources), "rb") as f:
            province = [str(num) for num in pickle.load(f)]
            self.province = "\\b(" + '|'.join(province) + ")\\b"

        with open("{0}/cities_phone.pickle".format(self.resources), "rb") as f:
            cities_phone = [str(num) for num in pickle.load(f)]
            self.cities_phone_prefix = "(" + '|'.join(cities_phone) + ")"

        with open("{0}/cities_name.pickle".format(self.resources), "rb") as f:
            self.cities = [str(num) for num in pickle.load(f)]
            self.cities = "\\b(" + '|'.join(self.cities) + ")\\b"

        with open("{0}/places.pickle".format(self.resources), "rb") as f:
            places = [str(num) for num in pickle.load(f)]
            self.places = "\\b(" + '|'.join(places) + ")\\b"
            
    def standardize_query(self, text: str):
        words = text.split(" ")
        for i in range(len(words)):
            if words[i] in self.abbreviates:
                words[i] = self.abbreviates[words[i]]
            elif "." in words[i]:
                tokens = words[i].split(".")
                if len(tokens) == 1 and tokens[0] in self.abbreviates:
                    words[i] = self.abbreviates[tokens[0]]
                elif len(tokens) == 2 and tokens[0] in self.abbreviates and\
                tokens[1] not in self.abbreviates:
                    words[i] = self.abbreviates[tokens[0]] + " " + tokens[1]
        return ' '.join(words).lstrip().rstrip().strip()

    def normalize_number(self, text: str):
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹" 
        english_numbers = "0123456789"
        arabic_numbers = "٠١٢٣٤٥٦٧٨٩"

        translation_from_persian = str.maketrans(persian_numbers, english_numbers)
        translation_from_arabic = str.maketrans(arabic_numbers, english_numbers)

        return text.translate(translation_from_persian).translate(translation_from_arabic)

    def split_sentences(self, text: str):
        sentence_delimiters = [
            ":",
            "\.",
            "\?",
            "\؟",
            "\!",
            "؛",
        ]
        sentences = [
            sentence.lstrip().rstrip().strip()
            for sentence in
            re.split("("+'|'.join(sentence_delimiters)+")", text)
        ]
        new_sentences = []
        for i in range(len(sentences)):
            new_sentences.append(sentences[i])
            if sentences[i-1]== ".":
                if sentences[i-2].split(" ")[-1] in self.abbreviates:
                    if sentences[i].split(" ")[0] not in self.abbreviates:
                        new_sentences = new_sentences[:-3]
                        new_sentences.append(
                            sentences[i-2]+""+sentences[i-1]+" "+sentences[i]
                        )
                    
        new_sentences = [
            sentence.lstrip().rstrip().strip()
            for sentence in new_sentences
            if sentence not in sentence_delimiters and sentence!="."
        ]
        return new_sentences

    def specify_ambiguity_locations(self, text: str):
        signs = list(self.abbreviates.keys()) +\
                list(self.abbreviates.values()) +\
                self.ez_address_identifier.split("|") +\
                self.non_starter_addresskeywords.split("|") +\
                self.relational_addresskeywords.split("|") +\
                self.start_addresskeywords.split("|")

        words = text.split(" ")
        for i in range(len(words)) :
            if words[i] in self.ambiguity_countries and\
            self.ambiguity_countries[words[i]] == 0:
                if not list(set(signs) & set([words[i-2], words[i-1], words[i+1], words[i+2]])):
                    words[i] = "1**1" + words[i] + "1**1"

        return ' '.join(words)
    
    def run(self, text: str):
        # sentences = self.split_sentences(text)
        # addresses = []
        # for sentence in sentences:
        sentence = self.standardize_query(text)
        sentence = self.specify_ambiguity_locations(sentence)
        address = self.extract_address1(sentence)
        place = self.latlon.get_latlong(address["address"])
        address["place"] = [place["x"], place["y"]] if place is not None else []
        # addresses.append(address)
        return address
    
    def match_address(self, inp):
        matches = []
        for keyword_count in range(10, 0, -1):
            count_pattern = self.pattern.format(keyword_count=keyword_count, spaces_count="0,20")
            for matched in re.finditer(count_pattern, inp):
                start, end = matched.span()
                inp = inp[:start] + '#' * (end - start) + inp[end:]
                matches.append(matched)
        matches += list(re.finditer(self.locations, inp))
        return matches

    def match_email(self, inp):
        return re.finditer(
            r"\b(\w+([-+(\.|\[dot\])']\w+)*(@|\[at\])\w+([-(\.|\[dot\])]\w+)*(\.|\[dot\])\w+([-(\.|\[dot\])]\w+)*)\b", inp)

    def match_url(self, inp):
        return re.finditer(
            r"\b((https|http|ftp):\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)\b",
            inp)

    def match_phone(self, inp):
        self.cities_phone_prefix = "(41|44|45|31|84|77|21|38|51|56|58|61|24|23|54|71|26|25|28|87|34|83|74|17|13|66|11|86|76|81)"
        mobile_pattern = "(0|((\+98)[- ]?|(\(\+98\))[- ]?))?9([01239][0-9])[- ]?[0-9]{3}[- ]?[0-9]{4}"
        phone_pattern = f"(0|(((\+98)|(\(\+98\)))[- ]?))?(({self.cities_phone_prefix}|(\({self.cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"
        phone_without_country_pattern = f"(((0?{self.cities_phone_prefix})|(\(0?{self.cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"  # ----->   (021)7782540555
        phone_three_digit = "\\b(110|112|113|114|115|123|125|111|116|118|120|121|122|124|129|131|132|133|134|136|137|141|162|190|191|192|193|194|195|197|199)\\b"
        phone_three_digit_word = " صد و ده|صد و دوازده|صد و سیزده|صد و چهارده|صد و پانزده|صد و بیست و سه|صد و بیست و پنج|صد و یازده|صد و شانزده|صد و هجده|صد و بیست|صد و بیست و یک|صد و بیست و دو|صد و بیست و چهار|صد و بیست و نه|صد و سی یک|صد و سی و دو|صد و سی و سه|صد و سی و چهار|صد و سی و شش|صد و سی هفت|صد و چهل و یک|صد و شصت و دو|صد و نود|صد و نود و یک|صد و نود و دو|صد و نود و سه|صد و نود و چهار|صد و نود و پنج|صد و نود و هفت|صد و نود و نه"
        phone_four_digit = f"((0?{self.cities_phone_prefix}|\(0?{self.cities_phone_prefix}\))[- ]?)[1-9][0-9]{{3}}|([3-9]\d{{3}}|2[1-9]\d{{2}})"
        return re.finditer(
            f"(({mobile_pattern})|({phone_pattern})|({phone_without_country_pattern})|({phone_three_digit})|({phone_three_digit_word})|({phone_four_digit}))",
            inp)

    def extract_address1(self, text):
        text = text.replace("\u200C", " ")
        text = self.normalize_number(text)
        matches = {'address':[], 'email':[], 'url':[], 'number':[], 'address_span':[], 'email_span':[], 'url_span':[], 'number_span':[]}
        for i in (self.match_address(text)):
            matches['address'].append(i.group())
            matches['address_span'].append(i.start())
            matches['address_span'].append(i.end())

        for i in (self.match_email(text)):
            matches['email'].append(i.group())
            matches['email_span'].append(i.start())
            matches['email_span'].append(i.end())

        for i in (self.match_url(text)):
            matches['url'].append(i.group())
            matches['url_span'].append(i.start())
            matches['url_span'].append(i.end())

        for i in ( self.match_phone(text)):
            matches['number'].append(i.group())
            matches['number_span'].append(i.start())
            matches['number_span'].append(i.end())

        return matches


if __name__ == '__main__':
    model = AddressExtractor()
    input_text = input()
    print(model.run(input_text))