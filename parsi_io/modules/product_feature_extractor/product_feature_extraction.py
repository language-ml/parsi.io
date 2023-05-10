import hazm
import re

data_path = './parsi_io/modules/product_feature_extractor/data'

class MyNormalizer(hazm.Normalizer):
    
    def __init__(self):
        super().__init__()
        self.aug_data_init()
        
    def aug_data_init(self):
        f = open(f'{data_path}/augmented_data.txt', 'r')
        self.aug_data = f.readlines()
        f.close()
    
    def replace_with_persian(self, sent):
        replace_list = {'ى':'ی',
                        'ة':'ه',
                        'ي':'ی'}
        
        for x in replace_list:
            sent = sent.replace(x, replace_list[x])
        
        return sent
    
    
    def my_normalize(self, text):
        text = self.normalize(text)
        
        aug = {y[0]:y[1] for y in [x.replace('\n', '').split('\t') for x in self.aug_data]}
        
        for k in aug:
            while k in text:
                text = text.replace(k, aug[k])
        while '\u200c' in text:
            text = text.replace('\u200c', ' ')
        return text
    

class ProductFeatureExtractor():
    def __init__(self):
        self.normalizer = MyNormalizer()
        self.taste_init()
        self.size_init()
        self.originality_init()
        self.quality_init()
        self.beauty_init()
        self.purchaseValue_init()
        self.color_init()
    
    
    def color_init(self):
        key_words = r"\b(نور|تم|رنگ)\s*((ی|اش|شو|ش)\s*)*\b"
        colors = r"\b(سفید|نخودی|زرشکی|قرمز|سرخ|مغز پسته ای|سورمه ای|سورمه‌ای|سرمیی|سبز دودی|آبی دریایی|فیروزه ای|نیلی|بنفش|توسی|خاکستری|بور|قهوه ای|نارنجی|سبز|لاجوردی|سرخابی|مشکی|سیاه|زرد|آبی|صورتی|طلایی|نقره ای|بژ|دهانی|انگوری|پسته ای|فیروزی|نیل|سرمئی|بادامی|بهورا|نارنجی|مالا|آسمانی|جامنی|پیلا|نیلا|سرخابی|ارغوانی)\s*((ه||شو|یش|ی|ش)\s*)*\b"
        self.color_p1 = f"\s*({key_words})*(\s*{colors})+"
        self.color_p2 = f"\s*({colors})+(\s*{key_words})*"
        self.color_p = f"({self.color_p1})|({self.color_p2})"
    
    
    def beauty_init(self):
        def read_file(file):
            texts = []
            for word in file:
                text = word.rstrip('\n')
                texts.append(text)
            return texts

        positivers = read_file(open(f'{data_path}/positivers.txt', 'r', encoding='utf-8').readlines())
        negativers = read_file(open(f'{data_path}/negativers.txt', 'r', encoding='utf-8').readlines())

        positivers = r'\b(' + r''.join([i + r'|' for i in positivers])[:-1] + r')\b'
        negativers = r'\b(' + r''.join([i + r'|' for i in negativers])[:-1] + r')\b'
        
        postively_corrlated_to_beauty_words = r"\b(جذاب|زیبا|دلفریب|خوش منظر|قسیم|فرخ|قشنگ|خوشگل|شکیل|خوبرو|شیک|تمیز|منصف|برازنده|موزون|مطابق مد روز|بدیع|خوش منظره|شایان تصویر|خوش ترکیب|باب روز|زیبنده|جمیل|خوشنما|نیکو|خوب رو|جمیل|شکیل|جذاب|ترگل |ورگل|نایس|بیوتیفول|بیوتی فول|خوجل|خوب رو|دل فریب|جهون|رعنا|کیوت|لاکچری)((ش||تر|یی|ییش|انه|یش|ی))\b"
        negativly_corrlated_to_beauty_words = r"\b(زشت|بدریخت|بدشکل|بدمنظر|بدهیکل|بیریخت|بی ریخت|کریه|کریه المنظر|پچل|بد|سوء|مذموم|ذمیمه|رکیک|سخیف|شنیع|فاحش|قبیح|مستهجن|مکروه|ناپسند|نازیبا|نفرت انگیز|نکوهیده|ننگین|شنیع|منزجر|مکروه|مغایر|ناسازگار|فرومایه|بیمناک|شریر|فجیع|تاثر اور|زننده|ترسناک|مهیب|عنیف|وقیح|سهمگین|بدکار|نابکار|ناپسند|بد گل|نازیبا|بی قواره|زشت و وقیح|خبیی|ستبر|زمخت|شرم اور|غلیظ|نا هموار|رنجاننده|چپ چپ|بدشکل|زننده|کثیف|کریه|نامطبوع|چرک و کثیف|بد قیافه|برملا|ناهنجار|نفرت انگیز|زمخت و غیر جذاب|چرک|چرکین|پرخش|ژیژ|نفرت انگیز|سهمناک|نامطبوع|زننده|تهوع اور|منزجر کننده|فاقد جمال|دارای صورت ناهنجار و زننده|نامطلوب|مجدر|ژولیده|ناسترده|نامطبوع|نا زیبا|زبون|ضد زیبا|بدشکل|بدگل|ضد زیبا و درشت|زبون|ناهموار|بدنما|تنفرآور|قبیح|بد ترکیب|پتیاره|کریه|کریح|ارنعوت|بد پک و پوز|خوار|نکوهیده|ننگین|نارعنا|زشتوک|نا رعنا|بد دک و پور|بدترکیب|تنفر آور|تنفراور|تنفر اور|بد نما|بد گل|بد شکل|ضدزیبا|نازیبا|نا مطبوع|نا سترده|نا مطلوب|تهوع آور|بر ملا|بد قیافه|کثیف|چرک|بد شکل|ناهموار|شرم آور|بیقواره|نا زیبا|بدگل|بد کار|تاثر آور|منزجر کننده|نا زیبا|بد هیکل|بد منظر|بد شکل|بد ریخت)((ش||اش|تر|یی|ییش|انه|یش|ی))\b"
        positive_verbs = r"\b(جذاب|زیبا|دلفریب|خوش منظر|قسیم|فرخ|قشنگ|خوشگل|شکیل|خوبرو|شیک|تمیز|منصف|برازنده|موزون|مطابق مد روز|بدیع|خوش منظره|شایان تصویر|خوش ترکیب|باب روز|زیبنده|جمیل|خوشنما|نیکو|خوب رو|جمیل|شکیل|جذاب|ترگل |ورگل|نایس|بیوتیفول|بیوتی فول|خوجل|خوب رو|دل فریب|جهون|رعنا|کیوت|لاکچری)((ه|ن|ند)+)\b"
        negative_verbs = r"\b(زشت|بدریخت|بدشکل|بدمنظر|بدهیکل|بی ریخت|بیریخت|کریه|کریه المنظر|پچل|بد|سوء|مذموم|ذمیمه|رکیک|سخیف|شنیع|فاحش|قبیح|مستهجن|مکروه|ناپسند|نازیبا|نفرت انگیز|نکوهیده|ننگین|شنیع|منزجر|مکروه|مغایر|ناسازگار|فرومایه|بیمناک|شریر|فجیع|تاثر اور|زننده|ترسناک|مهیب|عنیف|وقیح|سهمگین|بدکار|نابکار|ناپسند|بد گل|نازیبا|بی قواره|زشت و وقیح|خبیی|ستبر|زمخت|شرم اور|غلیظ|نا هموار|رنجاننده|چپ چپ|بدشکل|زننده|کثیف|کریه|نامطبوع|چرک و کثیف|بد قیافه|برملا|ناهنجار|نفرت انگیز|زمخت و غیر جذاب|چرک|چرکین|پرخش|ژیژ|نفرت انگیز|سهمناک|نامطبوع|زننده|تهوع اور|منزجر کننده|فاقد جمال|دارای صورت ناهنجار و زننده|نامطلوب|مجدر|ژولیده|ناسترده|نامطبوع|نا زیبا|زبون|ضد زیبا|بدشکل|بدگل|ضد زیبا و درشت|زبون|ناهموار|بدنما|تنفرآور|قبیح|بد ترکیب|پتیاره|کریه|کریح|ارنعوت|بد پک و پوز|خوار|نکوهیده|ننگین|نارعنا|زشتوک|نا رعنا|بد دک و پور|بدترکیب|تنفر آور|تنفراور|تنفر اور|بد نما|بد گل|بد شکل|ضدزیبا|نازیبا|نا مطبوع|نا سترده|نا مطلوب|تهوع آور|بر ملا|بد قیافه|کثیف|چرک|بد شکل|ناهموار|شرم آور|بیقواره|نا زیبا|بدگل|بد کار|تاثر آور|منزجر کننده|نا زیبا|بد هیکل|بد منظر|بد شکل|بد ریخت)((ه|ن|ند)+)\b"
        keywords = r"\b(شکل|ظاهر|قیاقه|قواره|قشنگی|شکل ظاهر|رنگ و رو|رنگ و لعاب|طرح|خوشرنگ|خوش رنگ)((ی|اش|شو|ش)\s*)*\b"
        self.beauty_p1 = f"\s*({keywords})*(\s*{postively_corrlated_to_beauty_words})+(\s*{positivers})+"
        self.beauty_p2 = f"({postively_corrlated_to_beauty_words})+$"
        self.beauty_p3 = f"({positive_verbs})+"
        self.beauty_p4 = f"(\s*{postively_corrlated_to_beauty_words})+"
        self.beauty_beau_p = f"({self.beauty_p1})|({self.beauty_p2})|({self.beauty_p3})|({self.beauty_p4})"
        self.beauty_ugly_p1 = f"\s*({keywords})*(\s*{negativly_corrlated_to_beauty_words})+(\s*{positivers})+"
        self.beauty_ugly_p2 = f"({negativly_corrlated_to_beauty_words})+$"
        self.beauty_ugly_p3 = f"({negative_verbs})+"
        self.beauty_ugly_p4 = f"(\s*{negativly_corrlated_to_beauty_words})+"
        self.beauty_ugly_p = f"({self.beauty_ugly_p1})|({self.beauty_ugly_p2})|({self.beauty_ugly_p3})|({self.beauty_ugly_p4})"
        self.beauty_neu_p1 = f"\s*({keywords})*(\s*{negativly_corrlated_to_beauty_words})+(\s*{negativers})+"
        self.beauty_neu_p2 = f"\s*({keywords})*(\s*{postively_corrlated_to_beauty_words})+(\s*{negativers})+"
        self.beauty_neu_p = f"({self.beauty_neu_p1})|({self.beauty_neu_p2})"
    
    
    def purchaseValue_init(self):
        g1 = r"\b(?P<where>تخفیف ویژه|پیشنهاد ویژه|پیشنهاد شگفت انگیز|شگفت انگیز|تخفیف)\b"
        g2 = r"\b(ارزش خرید|ارزش|ارزشمند|ارزشمنده|باارزش)\b"
        g3 = r"\b(?P<دارد>دارد|داشت|داره|است|هست|هستش|بود)\b"
        g4 = r"\b(?P<ندارد>ندارد|نداشت|نداره|نیست|نیستش)\b"
        g5 = r"\b(?P<بالا>بالا|بالایی|زیاد|زیاده|زیادی|خوب)\b"
        g6 = r"(ارزشمند|می ارز)"
        g7 = r"(نمی ارز)"
        g8 = r"(بخر)"
        g9 = r"(نخر)"
        g10 = r"(قیمت خرید|قیمت)"
        g11 = r"(بالا|زیاد)"
        g12 = r"(خوب|کم|مناسب)"
        postfix = r"(ه|ی|ش|ند|ین|ن|ید)"


        self.purchaseValue_p1 = f"({g2}{postfix}*)\s*({g3}{postfix}*|{g4}{postfix}*)" 
        self.purchaseValue_p2 = f"({g2}{postfix}*)\s*({g5}{postfix}*)"
        self.purchaseValue_p3 = f"({g2}{postfix}*).*?({g1}{postfix}*)"
        self.purchaseValue_p4 = f"({g6}{postfix}*)"
        self.purchaseValue_p5 = f"({g7}{postfix}*)"
        self.purchaseValue_p6 = f"({g8}{postfix}*)"
        self.purchaseValue_p7 = f"({g9}{postfix}*)"
        self.purchaseValue_p8 = f"({g10}{postfix}*)\s*({g11}{postfix}*)"
        self.purchaseValue_p9 = f"({g10}{postfix}*)\s*({g12}{postfix}*)"
        
    
    def size_init(self):
        g1 = r"\b(?P<بزرگ>بزرگ|بزرگی|بزرگه)\b"
        g2 = r"\b(?P<کوچک>کوچک|کوچیکی|کوچکی|کوچیک|کوچکه|کوچیکه)\b"
        g3 = r"\b(?P<مناسب>مناسب|مناسبه|مناسبی|معمولی)\b"
        g4 = r"\b(?P<خوب>خوب|خوبه|خوبی|عالی)\b"
        g5 = r"\b(خیلی|زیاد|زیادی|بیش از حد|تا حدی|نسبتا)\b"
        g6 = r"\b(سایز|سایزش|سایزی)\b"
        g7 = r"\b(اندازه|اندازه‌ای|اندازش|اندازه‌اش|اندازه‌ی)\b"
        g8 = r"\b(دارد|است|هست|هستش|بود)\b"
        g9 = r"\b(?P<not>ندارد|نیست|نیستش|نبود)\b"
        postfix = r"(ه|ی|ش|ند|ین|ن)"
        
        self.size_not_mapper = {
            'کوچک': 'بزرگ',
            'بزرگ': 'کوچک',
            'مناسب': 'نامناسب',
            'نامناسب': 'مناسب',
            'خوب': 'بد',
            'بد': 'خوب'
        }
        self.size_p1 = f"({g6}{postfix}*|{g7}{postfix}*)\s*({g5}{postfix}*)*\s*({g1}{postfix}*|{g2}{postfix}*|{g3}{postfix}*|{g4}{postfix}*)\s*({g8}{postfix}*|{g9}{postfix}*)*"
        self.size_p2 = f"({g5}{postfix}*)*\s*({g1}{postfix}*|{g2}{postfix}*)\s*({g8}{postfix}*|{g9}{postfix}*)*"
    
    
    def originality_init(self):
        real_ = r"(اصل|اورجینال|فابریک)(\s|ه)*"
        fake_ = r"(تقلبی|فیک)(\s|ه)*"
        not_verbs = r"(نیست|نبود|نیس)"
        not_fake = fr"({fake_})\s*({not_verbs})+"
        not_real = fr"({real_})\s*({not_verbs})+"
        fake = fr"((غیر)\s*({real_})|{fake_}|{not_real})"
        real = fr"((غیر)\s*({fake_})|{real_}|{not_fake})"

        self.fake_p = fr"\s*({fake})"
        self.real_p = fr"\s*({real})"
    
    
    def taste_init(self):
        self.taste_main = r"(طعم|مزه|لذیذ)"
        nagam = r"(نگویم|نگم)\s*(برای|برا)(ت|تان)"
        taste_sense = fr"({nagam}|دلنشین|ادویه|شکر|نمک|ملس|گس|شیرین|ترش|شور|تلخ)"
        self.taste_prefix = r"(پر|کم|کمی|خیلی|یک ذره|یکم|مقداری|بی|خوش)"
        self.taste_suffix = r"(بهتر|زیاد|معمولی|عادی|جالب|خوب|عالی)"
        self.taste_suffix_non_space = r"(هایی|های|ها|یی|ی)"
        all_suffix = fr"({self.taste_suffix_non_space}|{self.taste_suffix})"
        match_chr = r"(با|و)"
        self.taste_p1 = fr"({self.taste_prefix}|\s)*({taste_sense})+(\s|{all_suffix}|({match_chr}+(\s)*({taste_sense})+))*"
        self.taste_p2 = fr"({self.taste_prefix}|\s)*({self.taste_main})+({taste_sense}|\s|{all_suffix}|({match_chr}+(\s)*({taste_sense})+))*"
    
    
    def quality_init(self):
        f = open(f'{data_path}/quality_pre_words.txt', 'r')
        words = f.readlines()
        f.close()
        words = [w.replace('\n', '').replace('\\s', '\s') for w in words]
        self.quality_pre_words = "|".join(words)
        
        f = open(f'{data_path}/base_form.txt', 'r')
        base_forms = f.readlines()
        f.close()
        base_forms = [b.replace('\n', '').split() for b in base_forms]
        self.quality_base_forms = [[b[0], b[1].replace('(', '').replace(')', '')] for b in base_forms]
        
        self.quality_pre_words = fr"({self.quality_pre_words})+(ش|ی|ه|ها|های|هایی|\s)*"
        bd = "(به)(\s)*(درد)(\s)*(ن|ب)(خور)"
        prefix = r"(اصلا|خیلی|بسیار|کمی|یک ذره)"
        adj1 = fr"(خوب|عالی|آشغال|اشغال|بد|ضعیف|بدک|{bd}|مناسب|مزخرف|مرغوب)"
        suffix = r"(اش|ش|ه|ی)"
        self.quality_not_verbs = r"(نیست|نبود|نیس|نداشت|ندارد)"
        adj2 = fr"(پایین|بالا|{adj1}|ناراضی|راضی)"
        self.quality_main = fr"(سطح|کیفیت)"
        self.quality_m_prefix = r"(بی|با|کم)"
        
        self.quality_p1 = fr"({self.quality_pre_words})*({prefix}|\s)*({adj1})+(\s|{suffix})*({self.quality_not_verbs})*"
        self.quality_p2 = fr"({self.quality_m_prefix})*\s*({self.quality_main})({suffix}|{self.quality_main}|\s)*({prefix}|\s)*({adj2})*(\s|{suffix})*({self.quality_not_verbs})*"
    
    
    def sent_normalize(self, sent):
        return self.normalizer.my_normalize(sent)
    
    
    def clean_result(self, text):
        for i in range(len(text)):
            for base_form in self.quality_base_forms:
                text[i] = re.sub(fr"({base_form[0]})", f"{base_form[1]}", text[i])
        return text
    
    
    def find_words(self, sent, pattern):
        matchs = []
        for m in re.finditer(pattern, sent):
            text = m.group()
            sp = list(m.span())
            if text[0] == ' ':
                sp[0] += 1
                text = text[1:]
            if text[-1] == ' ':
                sp[-1] -= 1
                text = text[:-1]
            matchs.append([text, sp])
        return matchs
    
    
    def taste(self, text):
        pattern1_res = self.find_words(text, self.taste_p1)
        pattern2_res = self.find_words(text, self.taste_p2)
        
        tmp = []
        for p in pattern1_res:
            if (re.search(fr"({self.taste_prefix})+\s*({self.taste_main})", p[0]) == None) and (re.search(fr"({self.taste_main})\s*({self.taste_suffix})", p[0]) == None):
                tmp.append([re.sub(fr"({self.taste_main})+(\s|{self.taste_suffix_non_space})*", '', p[0]), p[1]])
            else:
                tmp.append([p[0], p[1]])
        pattern1_res = tmp.copy()
        
        tmp = []
        for p in pattern2_res:
            if (re.search(fr"({self.taste_prefix})+\s*({self.taste_main})", p[0]) == None) and (re.search(fr"({self.taste_main})\s*({self.taste_suffix})", p[0]) == None):
                tmp.append([re.sub(fr"({self.taste_main})+(\s|{self.taste_suffix_non_space})*", '', p[0]), p[1]])
            else:
                tmp.append([p[0], p[1]])
        pattern2_res = tmp.copy()
        
        del tmp
        
        result = []
        for p1 in pattern1_res:
            check = True
            for p2 in pattern2_res:
                if p1[1][0] >= p2[1][0] and p1[1][1] <= p2[1][1]:
                    check = False
            if check:
                result.append(p1)
        result.extend(pattern2_res)
        
        for i in range(len(result)):
            if result[i][-1] == 'ی':
                result[i] = [result[i][0][:-1], [result[i][1][0], result[i][1][1]-1]]
            sp = [result[i][1][0], result[i][1][1]]
            result[i] = [self.clean_result([result[i][0]])[0], text[sp[0]:sp[1]], result[i][1]]
        
        return result
    
    
    def quality(self, text):
        pat1_res = self.find_words(text, self.quality_p1)
        pat2_res = self.find_words(text, self.quality_p2)
        
        pat1_res = [[re.sub(fr"({self.quality_pre_words}|{self.quality_main})", '', p[0]), p[1]] for p in [j for j in pat1_res]]
        
        tmp = []
        for p in pat2_res:
            if (re.search(fr"({self.quality_m_prefix})+\s*({self.quality_main})", p[0]) == None) and (re.search(fr"({self.quality_main})\s*({self.quality_not_verbs})", p[0]) == None):
                tmp.append([re.sub(fr"({self.quality_pre_words}|{self.quality_main})", '', p[0]), p[1]])
            else:
                tmp.append([p[0], p[1]])
        pat2_res = tmp.copy()
        
        del tmp
        
        if pat2_res:
            texts = [p[0].strip() for p in [j for j in pat2_res]]
            spans = [p[1] for p in [j for j in pat2_res]]
            texts = self.clean_result(texts)
            return [[t, text[s[0]:s[1]], s] for t, s in zip(texts, spans)]
        else:
            texts = [p[0].strip() for p in [j for j in pat1_res]]
            spans = [p[1] for p in [j for j in pat1_res]]
            texts = self.clean_result(texts)
            return [[t, text[s[0]:s[1]], s] for t, s in zip(texts, spans)]
        
    
    def originality(self, text):
        fake_res = self.find_words(text, self.fake_p)
        real_res = self.find_words(text, self.real_p)
        
        fake_index = []
        real_index = []

        for i, f in enumerate(fake_res):
            for j, r in enumerate(real_res):
                if f[0] in r[0]:
                    fake_index.append(i)
                if r[0] in f[0]:
                    real_index.append(j)

        result = [[t[0], t[1], 'ORGINAL'] for i, t in enumerate(real_res) if i not in real_index]
        result.extend([[f[0], f[1], 'FAKE'] for i, f in enumerate(fake_res) if i not in fake_index])
        
        return [[self.clean_result([r[0]])[0], text[r[1][0]:r[1][1]], r[1], r[2]] for r in result]
    
    
    def extract_value(self, d: dict):
        result = None
        for key, value in d.items():
            if key != 'not' and value is not None:
                result = key
            if key == 'not' and value is not None:
                result = self.size_not_mapper[result]
        return result
    
    
    def size(self, text):
        for m in re.finditer(self.size_p1, text):
            return self.extract_value(m.groupdict()), m.span()
        for m in re.finditer(self.size_p2, text):
            return self.extract_value(m.groupdict()), m.span()

    
    def beauty(self, text):
        output = []
        for _, m in enumerate(re.finditer(self.beauty_beau_p, text)):
            start, end = m.span()
            output = [[start, end], text[start:end], 'زیبا']
        for _, m in enumerate(re.finditer(self.beauty_ugly_p, text)):
            start, end = m.span()
            output = [[start, end], text[start:end], 'زشت']
        for _, m in enumerate(re.finditer(self.beauty_neu_p, text)):
            start, end = m.span()
            output =  [[start, end], text[start:end], 'معمولی']
        return output
    
    
    def color(self, text):
        colors = r"(سفید|نخودی|زرشکی|قرمز|سرخ|مغز پسته ای|سورمه ای|سورمه‌ای|سرمیی|سبز دودی|آبی دریایی|فیروزه ای|نیلی|بنفش|توسی|خاکستری|بور|قهوه ای|نارنجی|سبز|لاجوردی|سرخابی|مشکی|سیاه|زرد|آبی|صورتی|طلایی|نقره ای|بژ|دهانی|انگوری|پسته ای|فیروزی|نیل|سرمئی|بادامی|بهورا|نارنجی|مالا|آسمانی|جامنی|پیلا|نیلا|سرخابی|ارغوانی)"
        output = []
        for _, m in enumerate(re.finditer(self.color_p, text)):
            start, end = m.span()
            result = text[start:end]
            for base_form in self.quality_base_forms:
                cleaned_result = re.sub(fr"({base_form[0]})", f"{base_form[1]}", result)
                if result != cleaned_result:
                    break
            output.append([[start, end], text[start:end], re.search(colors, result).group()]) 
        return output
    
        
    def purchaseValue(self, text):
        for m in re.finditer(self.purchaseValue_p1, text):
            for key, value in m.groupdict().items():
                if value is not None:
                    return key, m.span()
                    break
            break
        for m in re.finditer(self.purchaseValue_p2, text):
            return 'بالا', m.span()
            break
        for m in re.finditer(self.purchaseValue_p3, text):
            return m.groupdict()['where'], m.span()
            break
        for m in re.finditer(self.purchaseValue_p5, text):
            return 'کم', m.span()
            break
        for m in re.finditer(self.purchaseValue_p4, text):
            return 'بالا', m.span()
            break
        for m in re.finditer(self.purchaseValue_p6, text):
            return 'بالا', m.span()
            break
        for m in re.finditer(self.purchaseValue_p7, text):
            return 'کم', m.span()
            break
        for m in re.finditer(self.purchaseValue_p8, text):
            return 'کم', m.span()
            break
        for m in re.finditer(self.purchaseValue_p9, text):
            return 'بالا', m.span()
            break
    
    
    def run(self, text):
        result = {}
        
        result["طعم"] = []
        taste_res = self.taste(text)
        if taste_res:
            for t in taste_res:
                if t[0]:
                    result["طعم"].append({"result": t[0], "span": [t[2][0], t[2][1]], "text": t[1]})
        else:
            result["طعم"] = None
            
        result["کیفیت"] = []
        quality_res = self.quality(text)
        if quality_res:
            for t in quality_res:
                if t[0]:
                    result["کیفیت"].append({"result": t[0], "span": [t[2][0], t[2][1]], "text": t[1]})
        else:
            result["کیفیت"] = None
            
        result["اصالت"] = []
        originality_res = self.originality(text)
        if originality_res:
            for t in originality_res:
                if t[0]:
                    result["اصالت"].append({"result": t[0], "span": [t[2][0], t[2][1]], "text": t[1], "label": t[3]})
        else:
            result["اصالت"] = None
        
        result["ظاهر"] = []
        beauty_res = self.beauty(text)
        if beauty_res:
            result["ظاهر"].append({"result": beauty_res[1], "span": [beauty_res[0][0], beauty_res[0][1]], "text": beauty_res[2]})
        else:
            result["ظاهر"] = None
        
        result["اندازه"] = []
        size_res = self.size(text)
        if size_res:
            result["اندازه"].append({"result": size_res[0], "span": [size_res[1][0], size_res[1][1]], "text": text[size_res[1][0]:size_res[1][1]]})
        else:
            result["اندازه"] = None
        
        result["رنگ"] = []
        color_res = self.color(text)
        if color_res:
            for t in color_res:
                if t[1]:
                    result["رنگ"].append({"result": t[1], "span": [t[0][0], t[0][1]], "text": t[2]})
        else:
            result["رنگ"] = None
            
        result["ارزش خرید"] = []
        purchaseValue_res = self.purchaseValue(text)
        if purchaseValue_res:
            result["ارزش خرید"].append({"result": purchaseValue_res[0], "span": [purchaseValue_res[1][0], purchaseValue_res[1][1]], "text": text[purchaseValue_res[1][0]:purchaseValue_res[1][1]]})
        else:
            result["ارزش خرید"] = None
        
        return result
    

if __name__ == '__main__':
    model = ProductFeatureExtractor()
    input_text = input()
    normalized_text = model.sent_normalize(input_text)
    print(model.run(input_text))