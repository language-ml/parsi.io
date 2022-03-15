import re
from itertools import chain


class AddressExtraction(object):
    def __init__(self):
        self.ez_address_identifier = "آدرس|نشانی"
        self.non_starter_address_keywords = r"\b(منطقه|طبقه|کوچه|بن بست|پلاک|واحد)\b"
        self.relational_address_keywords = r"\b(جنب|رو به رو|روبرو|بالاتر از|پایین‌ تر از|قبل از|بعد از)\b"
        self.special_place = r"\b(مجموعه ورزشی|دانشگاه صنعتی|مغازه|نمایشگاه|سینما|سینمای|پارک|موزه|ورزشگاه|باشگاه|رستوران|کافه|پاساژ|کترینگ|شرکت|دانشگاه|مدرسه|مسجد|راسته|تیمچه|بازار|درمانگاه|بیمارستان|حسینیه|دبستان|دبیرستان|دانشکده|آزمایشگاه|تعمیرگاه|مکانیکی|آتلیه|رادیولوژی|سونوگرافی|نانوایی|بولینگ|تولیدی|کارخانه|قهوه خانه|چای خانه|سفره خانه|فودکورت|مجتمع تجاری|داروخانه|مجلس شورای|ریاست|قوه|دادگاه|دادسرای|بیت |دفتر|حوزه ی علمیه|حرم|فدراسیون)\b"
        self.countries = r"\b(آندورا|امارات متحده عربی|افغانستان|آنتیگوا و باربودا|آنگویلا|آلبانی|ارمنستان|آنگولا|جنوبگان|آرژانتین|ساموآی آمریکا|اتریش|استرالیا|آروبا|جزایر آلند|جمهوری آذربایجان|بوسنی و هرزگوین|باربادوس|بنگلادش|بلژیک|بورکینا فاسو|بلغارستان|بحرین|بوروندی|بنین|سنت بارثلمی|برمودا|برونئی|بولیوی|هلند کارائیب|برزیل|باهاما|بوتان|جزیره بووه|بوتسوانا|بلاروس|بلیز|کانادا|جزایر کوکوس|جمهوری دموکراتیک کنگو|جمهوری آفریقای مرکزی|جمهوری کنگو|سوئیس|ساحل عاج|جزایر کوک|شیلی|کامرون|چین|کلمبیا|کاستاریکا|کوبا|کیپ ورد|کوراسائو|جزیره کریسمس|قبرس|جمهوری چک|آلمان|جیبوتی|دانمارک|دومینیکا|دومینیکا|الجزایر|اکوادور|استونی|مصر|صحرای غربی|اریتره|اسپانیا|اتیوپی|فنلاند|فیجی|جزایر فالکلند|ایالات فدرال میکرونزی|جزایر فارو|فرانسه|گابن|انگلستان|گرانادا|گرجستان|گویان فرانسه|گرنزی|غنا|جبل الطارق|گرینلند|گامبیا|گینه|جزیره گوادلوپ|گینه استوایی|یونان|جزایر جورجیای جنوبی و ساندویچ جنوبی|گواتمالا|گوام|گینه بیسائو|گویان|هنگ کنگ|جزیره هرد و جزایر مک دونالد|هندوراس|کرواسی|هائیتی|مجارستان|اندونزی|جمهوری ایرلند|فلسطین اشغالی (اسرائیل)|جزیره من|هند|قلمروی اقیانوس هند بریتانیا|عراق|ایران|ایسلند|ایتالیا|ادبیات|جامائیکا|اردن|ژاپن|کنیا|قرقیزستان|کامبوج|کیریباتی|کومور|سنت کیتس و نویس|کره شمالی|کره جنوبی|کویت|جزایر کیمن|قزاقستان|لائوس|لبنان|سنت لوسیا|لیختن اشتاین|سری لانکا|لیبریا|لسوتو|لیتوانی|لوکزامبورگ|لتونی|لیبی|مراکش|موناکو|مولداوی|مونته نگرو|سنت مارتین فرانسه|ماداگاسکار|جزایر مارشال|جمهوری مقدونیه|مالی|میانمار|مغولستان|ماکائو|جزایر ماریانای شمالی|مارتینیک|موریتانی|مونتسرات|مالت|موریس|مالدیو|مالاوی|مکزیک|مالزی|موزامبیک|نامیبیا|کالدونیای جدید|نیجر|جزیره نورفولک|نیجریه|نیکاراگوئه|هلند|نروژ|نپال|نائورو|نیوئه|نیوزلند|عمان|پاناما|پرو|پلینزی فرانسه|پاپوآ گینه نو|فیلیپین|پاکستان|لهستان|سنت پیر و ماژلان|جزایر پیت کرن|پورتوریکو|فلسطین|پرتغال|پالائو|پاراگوئه|قطر|ریونیون|رومانی|صربستان|روسیه|رواندا|عربستان سعودی|جزایر سلیمان|سیشل|سودان|سوئد|سنگاپور|سینت هلینا|اسلوونی|سوالبارد و یان ماین|اسلواکی|سیرالئون|سن مارینو|سنگال|سومالی|سورینام|سائوتومه و پرینسیپ|السالوادور|سنت مارتین هلند|سوریه|سوازیلند|جزایر تورکس و کایکوس|چاد|سرزمین های قطب جنوب و جنوبی فرانسه|توگو|تایلند|تاجیکستان|توکلائو|تیمور شرقی|ترکمنستان|تونس|تونگا|ترکیه|ترینیداد و توباگو|تووالو|تایوان|تانزانیا|اوکراین|اوگاندا|جزایر کوچک حاشیه ای آمریکا|ایالات متحده|اروگوئه|ازبکستان|شهر واتیکان|سنت وینسنت و گرنادین|ونزوئلا|جزایر ویرجین بریتانیا|جزایر ویرجین ایالات متحده آمریکا|ویتنام|وانواتو|والیس و فوتونا|ساموآ|یمن|مایوت|آفریقای جنوبی|زامبیا|زیمبابوه)\b"
        self.central_cities = r"\b(تبریز|ارومیه|اردبیل|اصفهان|کرج|ایلام|بوشهر|تهران|شهرکرد|بیرجند|مشهد|بجنورد|اهواز|زنجان|سمنان|زاهدان|شیراز|قزوین|قم|سنندج|کرمان|کرمانشاه|یاسوج|گرگان|خرم آباد|رشت|ساری|اراک|بندرعباس|بندر عباس|همدان|یزد)\b"
        self.provinces = r"\b(آذربایجان شرقی|آذربایجان غربی|اردبیل|اصفهان|البرز|ایلام|بوشهر|تهران|چهارمحال و بختیاری|خراسان جنوبی|خراسان رضوی|خراسان شمالی|خوزستان|زنجان|سمنان|سیستان و بلوچستان|فارس|قزوین|قم|کردستان|کرمان|کرمانشاه|کهگیلویه و بویراحمد|گلستان|لرستان|گیلان|مازندران|مرکزی|هرمزگان|همدان|یزد)\b"
        self.separators = "،|-|,"
        self.start_address_keywords = r"\b(منطقه|خیابان|بلوار|میدان|بزرگراه|آزادراه|آزاد راه|اتوبان|جاده|محله|کوی|چهار راه|سه‌ راه|شهر|کشور|استان|شهرستان|دهستان|روستای|شهرک)\b"
        self.locations = f"{self.countries}|{self.central_cities}|{self.provinces}"
        self.middle_address_keywords = f"{self.start_address_keywords}|{self.non_starter_address_keywords}|{self.relational_address_keywords}"
        self.starter_keywords = f"{self.ez_address_identifier}|{self.start_address_keywords}|{self.locations}"
        self.pattern = f"({self.starter_keywords})([^\\.]{{{{{{spaces_count}}}}}}({self.middle_address_keywords}|{self.separators})){{{{{{keyword_count}}}}}}( *({self.special_place})? *\w+)"

    def normalizer_number(self, s: str):
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
        english_numbers = "0123456789"
        arabic_numbers = "٠١٢٣٤٥٦٧٨٩"

        translation_from_persian = str.maketrans(persian_numbers, english_numbers)
        translation_from_arabic = str.maketrans(arabic_numbers, english_numbers)

        return s.translate(translation_from_persian).translate(translation_from_arabic)

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
        cities_phone_prefix = "(41|44|45|31|84|77|21|38|51|56|58|61|24|23|54|71|26|25|28|87|34|83|74|17|13|66|11|86|76|81)"
        mobile_pattern = "(0|((\+98)[- ]?|(\(\+98\))[- ]?))?9([01239][0-9])[- ]?[0-9]{3}[- ]?[0-9]{4}"
        phone_pattern = f"(0|(((\+98)|(\(\+98\)))[- ]?))?(({cities_phone_prefix}|(\({cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"
        phone_without_country_pattern = f"(((0?{cities_phone_prefix})|(\(0?{cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"  # ----->   (021)7782540555
        phone_three_digit = "\\b(110|112|113|114|115|123|125|111|116|118|120|121|122|124|129|131|132|133|134|136|137|141|162|190|191|192|193|194|195|197|199)\\b"
        phone_three_digit_word = " صد و ده|صد و دوازده|صد و سیزده|صد و چهارده|صد و پانزده|صد و بیست و سه|صد و بیست و پنج|صد و یازده|صد و شانزده|صد و هجده|صد و بیست|صد و بیست و یک|صد و بیست و دو|صد و بیست و چهار|صد و بیست و نه|صد و سی یک|صد و سی و دو|صد و سی و سه|صد و سی و چهار|صد و سی و شش|صد و سی هفت|صد و چهل و یک|صد و شصت و دو|صد و نود|صد و نود و یک|صد و نود و دو|صد و نود و سه|صد و نود و چهار|صد و نود و پنج|صد و نود و هفت|صد و نود و نه"
        phone_four_digit = f"((0?{cities_phone_prefix}|\(0?{cities_phone_prefix}\))[- ]?)[1-9][0-9]{{3}}|([3-9]\d{{3}}|2[1-9]\d{{2}})"
        return re.finditer(
            f"(({mobile_pattern})|({phone_pattern})|({phone_without_country_pattern})|({phone_three_digit})|({phone_three_digit_word})|({phone_four_digit}))",
            inp)

    def run(self, text):
        text = text.replace("\u200C", " ")
        text = self.normalizer_number(text)
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
