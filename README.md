# parsi.io
## Installation
Install parsi_io as a pip package with the following command to use the library

```
pip install git+https://github.com/language-ml/parsi.io.git
```

If you need to edit the library install with -e flag

```
pip install -e git+https://github.com/language-ml/parsi.io.git
```

## Price and Quantity Extraction
- Extracting price, amount, and unit of a service or product

### Supported marker
- Product or service name, span, unit, and amount

### Example
```python
from parsi_io.modules.price_quantity_extractor.price_quantity_extraction import PriceAndQuantityExtraction
extractor = PriceAndQuantityExtraction()
extractor.run("جوشکاری ساعتی صد هزار تومان است و بنا ساعتی ۶۰ هزار تومان دریافت میکند.")
```

### Output
```
{
  "products_list": [
      {
          "product_name": "جوشکاری",
          "product_name_span": [
              0,
              7
          ],
          "product_amount": 1,
          "product_unit": "عدد",
          "price_amount": 100000.0,
          "price_marker": "صد هزار",
          "price_unit": "تومان"
      },
      {
          "product_name": "بنا",
          "product_name_span": [
              34,
              37
          ],
          "product_amount": 1,
          "product_unit": "عدد",
          "price_amount": 60000.0,
          "price_marker": "۶۰ هزار",
          "price_unit": "تومان"
      }
  ]
}
```

## Old persian preprocessing
- Hazm model improvement to support old persian

### Supported marker
- Normalizer, lemmatizer, stop words for old Persian

### Example
```python
from hazm import Normalizer, Lemmatizer

# Normalizer on qazals collection
normalizer = Normalizer(token_based=True, kohan_style=True)
print(normalizer.normalize('نمی رفته ای'))
print(normalizer.normalize('همی افتیم'))

# Lemmatizer on Kohan verbs
lemmatizer = Lemmatizer()
print(lemmatizer.lemmatize('افتادندی'))
print(lemmatizer.lemmatize('یافتمی'))
print(lemmatizer.lemmatize('همی‌بیفتید'))

```

### Output
```
نمی‌رفته‌ای
همی‌افتیم
افتاد#افت
یافت#یاب
همی‌بیفتید
```


## Verb Information Extractor
- Determines different information about the verb in a sentence

### Supported marker
- Tense, root, person, type

### Example
```python
from parsi_io.modules.verb_info_extractions import VerbInfoExtraction
extractor = VerbInfoExtraction()
result = extractor.run("من به کتابخانه رفتند و می خوردم و انها داشتند می زدند و ما با آنها رفته بودند و در این حال دیده اید بکارند و دراین حین می جوید و ما آنها را دارید می جوید و خواهند پرید")
```

### Output
```
[
    {
        "زمان": "گذشته",
        "بن فعل": "رفت",
        "نوع": "گذشته ساده",
        "شخص": "سوم شخص جمع"
    },
    {
        "زمان": "گذشته",
        "بن فعل": "خورد",
        "نوع": "گذشته استمراری",
        "شخص": "اول شخص مفرد"
    },
    {
        "زمان": "گذشته",
        "بن فعل": "زد",
        "نوع": "گذشته مستمر",
        "شخص": "سوم شخص جمع"
    },
    {
        "زمان": "گذشته",
        "بن فعل": "رفت",
        "نوع": "گذشته بعید",
        "شخص": "سوم شخص جمع"
    },
    {
        "زمان": "گذشته",
        "بن فعل": "دید",
        "نوع": "گذشته نقلی",
        "شخص": "دوم شخص جمع"
    },
    {
        "زمان": "حال",
        "بن فعل": "کار",
        "شخص": "سوم شخص جمع",
        "نوع": "حال التزامی"
    },
    {
        "زمان": "حال",
        "بن فعل": "جو",
        "شخص": "دوم شخص جمع",
        "نوع": "حال اخباری"
    },
    {
        "زمان": "حال",
        "بن فعل": "جو",
        "شخص": "دوم شخص جمع",
        "نوع": "حال مستمر"
    },
    {
        "زمان": "آینده",
        "بن فعل": "پرید",
        "شخص": "سوم شخص جمع",
        "نوع": "آینده ساده"
    }
]
```

## Product Feature Extractor
- Determines what are the features mentioned in a comment about a product

### Supported marker
- taste, quality, originality, color, beauty, purchase value, size

### Example
```python
from parsi_io.modules.product_feature_extractor.product_feature_extraction import ProductFeatureExtractor
extractor = ProductFeatureExtractor()
extractor.run("این محصول با وجود کیفیت خوبی که داره اما از نظر قیمت زیاد نمی ارزید، اندازه اش نسبتا بزرگ بود و خیلی قشنگ نبود")
```

### Output
```
{
  "طعم": null,
  "کیفیت": [
      {
          "result": "خوب",
          "span": [
              18,
              28
          ],
          "text": "کیفیت خوبی"
      }
  ],
  "اصالت": null,
  "ظاهر": [
      {
          "result": " قشنگ نبود",
          "span": [
              100,
              110
          ],
          "text": "معمولی"
      }
  ],
  "اندازه": [
      {
          "result": "بزرگ",
          "span": [
              79,
              93
          ],
          "text": "نسبتا بزرگ بود"
      }
  ],
  "رنگ": null,
  "ارزش خرید": [
      {
          "result": "کم",
          "span": [
              58,
              66
          ],
          "text": "نمی ارزی"
      }
  ]
}
```
## Quantity extractor
- Extracts Quantities from input text.

### Supported marker
- Amount + Unit + Quantity : '۲ کیلوگرم وزن'
- Amount + Unit + item : '۲ کیلوگرم سیب'
- Quantity + Amount + Unit : 'وزن ۲ کیلوگرم'
- Amount + Unit : '۲ کیلوگرم'
- Quantity + Adjective : 'وزن زیاد'


### Example
```python
from parsi_io.modules.quantity_extractions import QuantityExtraction
extractor = QuantityExtraction()
print(extractor.run("علی ۳.۵ کیلوگرم آرد خرید و باتری خود را هشتاد و پنج صدم وات شارژ کرد."))
```
### Output
```json
[
	{'type': 'جرم',
	'amount': [3.5], 
	'unit': 'کیلوگرم',
	'item': 'آرد', 
	'marker': '۳٫۵ کیلوگرم آرد', 
	'span': [4, 19], 
	'SI_amount': [3.5],
	'SI_unit': 'kilogram'},
	
	{'type': 'توان', 
	'amount': [0.85], 
	'unit': 'وات', 
	'item': '', 
	'marker': 'هشتاد و پنج صدم وات',
	'span': [40, 59], 
	'SI_amount': [0.85], 
	'SI_unit': 'kilogram * meter ** 2 / second ** 3'}]

```


## Address extractor

### Supported marker
- Address, Email, URL, Phone Number extractor, and their span's

### Example
```python
from parsi_io.modules.address_extractor.address_extractions import AddressExtractor
extractor = AddressExtractor()
extractor.run('آدرس خیابان شهیدبهشتی می‌باشد و برای اطلاعات بیشتر به page.com مراجعه فرمایید')
```
### Output
```
{
	'address': ['آدرس خیابان شهیدبهشتی'],
	'email': [],
	'url': ['page.com'],
	'number': [],
	'address_span': [0, 21],
	'email_span': [],
	'url_span': [54, 62],
	'number_span': []
}
```

## Cause and Effect extractor
- Determines whether a sentence is causal

### Supported marker
- Causal marker extarctor

### Example
```python
from parsi_io.modules.cause_effect_extractions import CauseEffectExtraction
extractor = CauseEffectExtraction()
extractor.run('چون نمی‌خواستم اون چیزی از ماجرا بفهمه، مجبور به تظاهر شدم.')
```
### Output
```
{
      "flag": "بله",
      "marker": "چون",
      "marker_span": "[0, 3]"
}
```

## Number extractor
- Extracts persian numbers both in numeral form or text form or mixed form.

### Example
```python
from parsi_io.modules.number_extractor import NumberExtractor
extractor = NumberExtractor()
extractor.run('من در بیست و پنجمین روز فروردین سوار اتوبوس ۱۲ شدم.')
```
### Output
```json
[
  {
    "span": [6,16],
    "phrase": "بیست و پنج",
    "value": 25
  },
  {
    "span": [44,46],
    "phrase": "۱۲",
    "value": 12
  }
]
```

## Quranic extractor
- Extracts parts (at least two words) of The Holy Quran
 verses with their surah and verse number from input text

### Supported marker
- The Holy Quran verses extractor

### Example
```python
from parsi_io.modules.quranic_extractions import QuranicExtraction
extractor = QuranicExtraction(model = 'exact', precompiled_patterns='prebuilt')
extractor.run('شان نزول آیه ی انما وليكم اللّه ورسوله والّذين امنوا')
```
### Output
```
{
    'input_span': [15, 52],
    'extracted': 'انما وليكم اللّه ورسوله والّذين امنوا',
    'quran_id': '5##55',
    'verse': 'إِنَّمَا وَلِيُّكُمُ اللَّهُ وَ رَسُولُهُ وَ الَّذِينَ آمَنُوا الَّذِينَ يُقِيمُونَ الصَّلَاةَ وَ يُؤْتُونَ الزَّكَاةَ وَ هُمْ رَاكِعُونَ'
}
```


## Sentence Type
- Distinguish between imperative and question sentences.

### Supported marker
- Distinguish between imperative and question sentences, by giving a sentence and receiving the sentence type along with the determining verb in the sentence.
- If the sentence is neither an imperative nor a question, the "other:سایر" category is returned as the verb type.
- In the "type" section, three categories of output can be expected: "imperative,positive or negative: امری مثبت - امری منفی", "question:پرسشی" and "other:سایر".
### Example
```python
from parsi_io.modules.SentenceType import SentenceClassifier
sent_classifier = SentenceClassifier()
sent_classifier.run('به کجا چنین شتابان می‌روی')
```
### Output
```
{
    'type': 'پرسشی',
    'verb': 'می‌روی',
}
```



## TimeDate extractor
- Extracts Time Date Markers (stable)
- Extract Values (Unstable)

### Supported marker
- All Time and Date Markers

### Example
```python
from parsi_io.modules.time_extractions import TimeExtraction
extractor = TimeExtraction()
extractor.run("ماریا شنبه عصر در ساعت نه و پنجاه نه دقیقه - مورخ 13 می 1999 با نادیا تماس گرفت اما نادیا بعدا در 1100/09/09 قمری به پرسش او پاسخ داد.")
```
### Output
```
{'markers': {'date': {'[50, 60]': '13 می 1999',
                      '[6, 10]': 'شنبه',
                      '[98, 113]': '1100/09/09 قمری'},
             'datetime': {'[18, 42]': 'ساعت نه و پنجاه نه دقیقه',
                          '[50, 60]': '13 می 1999',
                          '[6, 14]': 'شنبه عصر',
                          '[98, 113]': '1100/09/09 قمری'},
             'time': {'[11, 14]': 'عصر',
                      '[18, 42]': 'ساعت نه و پنجاه نه دقیقه'}},
 'ner': [('ماریا', 'O'),
         ('شنبه', 'B-DAT'),
         ('عصر', 'I-DAT'),
         ('در', 'O'),
         ('ساعت', 'B-DAT'),
         ('نه', 'I-DAT'),
         ('و', 'I-DAT'),
         ('پنجاه', 'I-DAT'),
         ('نه', 'I-DAT'),
         ('دقیقه', 'I-DAT'),
         ('-', 'O'),
         ('مورخ', 'O'),
         ('13', 'B-DAT'),
         ('می', 'I-DAT'),
         ('1999', 'I-DAT'),
         ('با', 'O'),
         ('نادیا', 'O'),
         ('تماس', 'O'),
         ('گرفت', 'O'),
         ('اما', 'O'),
         ('نادیا', 'O'),
         ('بعدا', 'O'),
         ('در', 'O'),
         ('1100/09/09', 'B-DAT'),
         ('قمری', 'I-DAT'),
         ('به', 'O'),
         ('پرسش', 'O'),
         ('او', 'O'),
         ('پاسخ', 'O'),
         ('داد', 'O'),
         ('.', 'O')],
 'spans': {'date': [[6, 10], [50, 60], [98, 113]],
           'datetime': [[6, 14], [18, 42], [50, 60], [98, 113]],
           'time': [[11, 14], [18, 42]]},
 'values': {'date': {'[50, 60]': '13/05/1999',
                     '[6, 10]': 'شنبه',
                     '[98, 113]': '1100/09/09 ه.ق'},
            'time': {'[11, 14]': 'عصر', '[18, 42]': '09:59:00'}}}
```

## Event extractor
This module is devoted to extract common event types.

### Supported marker
- Extract Events of the following types:
  - All (mode = 0)
  - Negotiations and agreement (mode = 1)
  - Official contracts (mode = 2)
  - Dismissal and assignment and resignation from the position (mode = 3)
  - Price changes (mode = 4)
  - Import and Export of goods (mode = 5)
  - Death related (mode = 6)
  - Sports related (mode = 7)

### Example
```python
from parsi_io.modules.event_extractions import EventExtraction
extractor = EventExtraction()
extractor.run("کسب مدل طلای مسابقات آسیای یکی از بهترین اتفاقات سال ۲۰۲۲ برای ما بود.", mode=0)
```
### Output
```
[
  {
    "line": "کسب مدل طلای مسابقات آسیای یکی از بهترین اتفاقات سال ۲۰۲۲ برای ما بود.",
    "type": "برد و باخت و تساوی",
    "text": "مسابقات",
    "span": [13, 20],
    "place": [""],
    "time": ["سال ۲۰۲۲"]
  }
]

```

## Question Extractor

### Supported Questions
- sentences with simple words as subject or object with the help of farsnet module
- cause and effect sentences

### Example
```python
from parsi_io.modules.question_generator import QuestionGeneration
extractor = QuestionGeneration()
extractor.run('حرکت بار الکتریکی باعث ایجاد میدان الکترومغناطیسی در فضا می شود')
```

if you want to use farsnet module to extract more questions pass your farsnet username and token to question extraction module.

```python
from parsi_io.modules.question_extractions import QuestionGeneration
extractor = QuestionGeneration(farsnet_user="YOUR_USERNAME", farsnet_token="YOUR_TOKEN")
extractor.run('حرکت بار الکتریکی باعث ایجاد میدان الکترومغناطیسی در فضا می شود')
```

### Output
```
[
{'Question': 'حرکت چه بار ی باعث ایجاد میدان الکترومغناطیسی در فضا می‌شود؟', 'Answer': 'بار الکتریکی'},
{'Question': 'حرکت بار الکتریکی باعث ایجاد چه میدان ی در فضا می‌شود؟', 'Answer': 'میدان الکترومغناطیسی'},
{'Question': 'آیا حرکت بار الکتریکی باعث ایجاد میدان الکترومغناطیسی در فضا می‌شود؟', 'Answer': 'بله'},
{'Question': 'چه چیزی باعث ایجاد میدان الکترومغناطیسی در فضا می‌شود؟', 'Answer': 'حرکت بار الکتریکی'},
{'Question': 'حرکت بار الکتریکی باعث ایجاد میدان الکترومغناطیسی در چه چیزی می‌شود؟', 'Answer': 'فضا'}
]
```

## Vehicle Movement Extractor
- Extracts vehicle movement information including: Source, Destination, and Vehicle.

### Supported Marker
- Source, Destination, and Vehicle.

### Example
```python
from parsi_io.modules.vehicle_movement_extractions import VehicleMovementExtraction
extractor = VehicleMovementExtraction()
extractor.run('من با قطار از اصفهان به تهران می‌روم.')
```
### Output
```json
[
  {
    "from": "اصفهان", 
    "from_span": [14, 20],
    "to": "تهران", 
    "to_span": [24, 29], 
    "vehicle": "قطار", 
    "vehicle_span": [6, 10]
  }
]
```


## Test
Add test cases to parsi_io/test/testcases/\[marker_name].json in the following template

### Template
```
[
    {
        "id":test ID,
        "input":input text,
        "outputs":output dictionary
    },
    ...
]
```


## Space and Punctuation Editor
- Improves space, half-space, and punctuation within a given text


### Example
```python
from parsi_io.modules.space_punctuation_editor import Spacing

sp = Spacing()
sp.run('در هنگام وقوع بلایای طبیعی ،بیش ترین خسارت متوجه قشر آسیب پذیر جامعه می شود.')
```
### Output
```
در هنگام وقوع بلایای طبیعی، بیش‌ترین خسارت متوجه قشر آسیب پذیر جامعه می‌شود.
```

## Stock Market Event Extractor
- Extracts events and entity names related to stock market.

### Example
```python
from parsi_io.modules.stockmarket_event_extractor import StockMarketEventExtractor
S = StockMarketEventExtractor()
examples = [
    'گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰̸۰۹̸۳۰ برای دیران منتشر شد.',
        
    "ارزش سهام مخابرات ایران امروز کاهش زیادی یافت."
]

S.run(*examples)

```
### Output
```
---------------------------- input 1----------------------------------------------
Normalized input: گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰̸۰۹̸۳۰ برای دیران منتشر شد.
{
  "type": "نماد",
  "marker": "دیران",
  "span": [
    57,
    62
  ]
}
{
  "type": "اعلان",
  "marker": "گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به ۱۴۰۰ ̸۰۹̸۳۰",
  "span": [
    0,
    51
  ]
}
---------------------------- input 2----------------------------------------------
Normalized input: ارزش سهام مخابرات ایران امروز کاهش زیادی یافت.
{
  "type": "شرکت",
  "marker": "مخابرات ایران",
  "span": [
    10,
    23
  ]
}
{
  "type": "واقعه",
  "marker": "کاهش زیادی یافت",
  "span": [
    30,
    45
  ],
  "subject": "ارزش سهام مخابرات ایران",
  "span_subject": [
    0,
    23
  ]
}
```


## Convert Number To Text
- Converts numbers to persian text.

### Example
```python
from parsi_io.modules.convert_number_to_text import ConvertNumberToText
num2text = ConvertNumberToText()
examples = [
  '-4713986205.11' ,
  '1402', '2000000',
  '3.14', '0.7'
]

for number in examples :
  output = num2text.run(number)
  print(output)

```
### Output
```
---------------------------------- input 1 -----------------------------------------------------------
normal_input: -4713986205.11
output: "منفی چهار میلیارد و هفتصد و سیزده میلیون و نهصد و هشتاد و شش هزار و دویست و پنج و یازده صدم"

---------------------------------- input 2 -----------------------------------------------------------
normal_input: 1402
output: "یک هزار و چهارصد و دو"

---------------------------------- input 3 -----------------------------------------------------------
normal_input: 2000000
output: "دو میلیون"

---------------------------------- input 4 -----------------------------------------------------------
normal_input: 3.14
output: "سه و چهارده صدم"

---------------------------------- input 5 -----------------------------------------------------------
normal_input: 0.7
output: "هفت دهم"

```


## Task Extractor
- Creates and updates tasks with an enhanced name and date extractor from persian text.

### Example
```python
from parsi_io.modules.task_extractor import TaskRunner
model = TaskRunner()
text = ('باید تسک حل تمرین دوم درس را در یک آذر شروع کنیم و تا ده آذر تمام کنیم. برای اینکار باید اول موضوع را '
            'مشخص کنیم و بعد پیادەسازی را انجام دهیم. افراد مسئول حل این تمرین آرش و ریحانه هستن.')
model.run(text)
```
### Output
```json
{
  "title": "تسک حل تمرین دوم درس",
  "subtasks": [
    "موضوع را مشخص کنیم",
    "پیادەسازی را انجام دهیم"
  ],
  "assign": [
    "آرش",
    "ریحانه"
  ],
  "start_time": "یک آذر",
  "end_time": "ده آذر",
  "is_done": false,
  "is_urgent": false
}
```
If we need to update the deadline:
(this feature supports updates to the task, date, and assignee):
### Example
```python
text = 'ددلاین تسک به ۱۵ آذر منتقل شد'
needsUpdate = True
model.run(text,needsUpdate)
```
### Output
```json
 {
    "title": "تسک حل تمرین دوم درس",
    "subtasks": [
      "موضوع را مشخص کنیم",
      "پیادەسازی را انجام دهیم"
    ],
    "assign": [
      "آرش",
      "ریحانه"
    ],
    "start_time": "یک آذر",
    "end_time": "۱۵ آذر",
    "is_done": false,
    "is_urgent": false
  }
```
Finally we can finish the task:
### Example
```python
text = 'تسک حل تمرین دوم درس تمام شد'
needsUpdate = True
model.run(text,needsUpdate)
```
### Output
```json
 {
    "title": "تسک حل تمرین دوم درس",
    "subtasks": [
      "موضوع را مشخص کنیم",
      "پیادەسازی را انجام دهیم"
    ],
    "assign": [
      "آرش",
      "ریحانه"
    ],
    "start_time": "یک آذر",
    "end_time": "۱۵ آذر",
    "is_done": true,
    "is_urgent": false
  }
```

## Contributors
| Marker                        | Contributors                                                                                                                       |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Quantity Extraction           | Mohammad Hejri, Arshan Dalili, Soroush Jahanzad, Marzieh Nouri, Reihaneh Zohrabi                                                   |
| Address Extraction            | Amirreza Mozayani, Arya Kosari, Seyyed Mohammadjavad Feyzabadi, Omid Ghahroodi, Hessein Partou, Sahar Zal, Moein Salimi            |
| CauseEffect Extraction        | Rozhan Ahmadi, Mohammad Azizmalayeri, Mohammadreza Fereiduni, Saeed Hematian, Seyyed Ali Marashian, Maryam Gheysari                |
| Number Extraction             | Mohammad Ali Sadraei Javaheri, Mohammad Mozafari, Reihaneh Zohrabi, Parham Abedazad, Mostafa Masumi                                |
| Quranic Extraction            | Seyyed Mohammad Aref Jahanmir, Alireza Sahebi, Ali Safarpoor Dehkordi, Mohammad Mehdi Hemmatyar, Morteza Abolghasemi, Saman Hadian | 
| Time Date Extraction          | [_Parstdex Team_](https://github.com/kargaranamir/parstdex)                                                                        | 
| Event Extraction              | Elnaz Rahmati, Zeinab Taghavi, Amir Mohammad Mansourian                                                                            
| Tag-Span Converter            | Omid Ghahroodi                                                                                                                     |
| Vehicle Movement Extraction   | Ahmad Zaferani, Mohammad Hossein Gheisarieh, Alireza Babazadeh, Mahsa Amani                                                        |
| Space and Punctuation Editor  | Amir Pourmand, Pouya Khani, Mahdi Akhi, Mobina Pournemat                                                                           |
| Question Generation           | Sahel Mesforoush                                                                                                                   |
| Product Feature Extractor     | Mohammadhossein Moasseghinia, Hossein Jafarinia, Ali Salamni                                                                       |
| Verb Info Extractor           | Parham Nouranbakht, Mahdi Saeedi, Mohammdreza Kamali                                                                               |
| Stock Market Event Extraction | Vida Ramezanian, Amin Kashiri, Fatemeh Tohidian, Seyyed Alireza Mousavi                                                            |
| Old persian preprocessing     | Arman Mazloum Zadeh, Faranak Karimi                                                                                                |
| Price and Quantity Extraction | Ali Karimi, Ali abdollahi, Amirhossein Hadian                                                                                      |
| Convert Number To Text        | Mostafa Nemati                                                                                                                     |
| Task Management               | Pardis Sadat Zahraei, Mahdi Saadatbakht,  Mohammad Mahdi Gheidi                                                                                         |

Contact: info@language.ml

Natural Language Processing and Digital Humanities Laboratory

PI: Asgari

