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
## Address extractor

### Supported marker
- Address, Email, URL, Phone Number extractor

### Example
```python
from parsi_io.modules.address_extractions import AddressExtraction
extractor = AddressExtraction()
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

## Question Generation

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





## Contributors
| Marker      | Contributors |
| ----------- | ----------- |
| Address Extraction      | Amirreza Mozayani, Arya Kosari, Seyyed Mohammadjavad Feyzabadi, Omid Ghahroodi  |
| CauseEffect Extraction      | Rozhan Ahmadi, Mohammad Azizmalayeri, Mohammadreza Fereiduni, Saeed Hematian, Seyyed Ali Marashian, Maryam Gheysari       |
| Number Extraction   | Mohammad Ali Sadraei Javaheri, Mohammad Mozafari, Reihane Zohrabi, Parham Abedazad, Mostafa Masumi  |
| Quranic Extraction    | Seyyed Mohammad Aref Jahanmir, Alireza Sahebi, Ali Safarpoor Dehkordi, Mohammad Mehdi Hemmatyar, Morteza Abolghasemi, Saman Hadian      | 
| Time Date Extraction    | [_Parstdex Team_](https://github.com/kargaranamir/parstdex) | 
| Tag-Span Converter      |  Omid Ghahroodi  |
| Vehicle Movement Extraction | Mahsa Amani |
| Space and Punctuation Editor | Amir Pourmand, Pouya Khani, Mahdi Akhi, Mobina Pournemat |
| Question Generation | Sahel Mesforoush |


Contact: info@language.ml

Natural Language Processing and Digital Humanities Laboratory

PI: Asgari

