# parsi.io
## Supported marker
- Address, Email, URL, Phone Number extractor

## Address extractor
### Example
```python
from parsi_io.modules.address_extractions import AddressExtraction
extractor = AddressExtraction()
extractor.run('آدرس خیابان شهیدبهشتی می‌باشد و برای اطلاعات بیشتر به page.com مراجعه فرمایید')
```
### Output
```
{'address': ['آدرس خیابان شهیدبهشتی'], 'email': [], 'url': ['page.com'], 'number': [], 'address_span': [0, 21], 'email_span': [], 'url_span': [54, 62], 'number_span': []}
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
## Cause and Effect extractor
- Determines whether a sentence is causal

## Supported marker
- Causal marker extarctor

### Example
```python
from parsi_io.modules.cause_effect_extractions import 
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

## Contributors
| Marker      | Contributors |
| ----------- | ----------- |
| Address Extraction      | Amirreza Mozayani, Arya Kosari, Seyyed Mohammadjavad Feyzabadi, Omid Ghahroodi       |
| CauseEffect Extraction      | Rozhan Ahmadi, Mohammad Azizmalayeri, Mohammadreza Fereiduni, Saeed Hematian, Seyyed Ali Marashian, Maryam Gheysari       |
| Number Extraction   | Mohammad Ali Sadraei Javaheri, Mohammad Mozafari        |
