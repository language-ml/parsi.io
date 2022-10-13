import re
import os
from parsanonymizer.utils import const


def process_file(path):
    with open(path, 'r', encoding='utf-8-sig') as file:
        text = file.readlines()
        text = [x.strip() for x in text if not x.startswith('#') and len(x.strip()) > 0]  # remove \n
        return text



class Annotation:
    """
    Annotation class is used to create annotation dictionary which will be used for creating regex from patterns
    in following steps.
    """

    annotation_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'annotation')
    annotations_dict = {}
    
    def __init__(self):
        # regex_annotations
        regex_annotations = self.create_regex_annotation_dict()
        # time annotation dictionary includes all annotations of time folder
        main_annotations = self.create_annotation_dict(self.annotation_path)


        self.annotations_dict = {**regex_annotations,
                                 **main_annotations}




    @staticmethod
    def create_annotation(path):
        text = process_file(path)
        annotation_mark = "|".join(text)
        return annotation_mark

    @staticmethod
    def create_regex_annotation_dict():
        annotation_dict = {
            'ACCNUM': r"""(شماره)? (حساب).{0,15}[0-9]{8,16}""",
            'ADV_ACCNUM': r"""(شماره)? (حساب) \\D{0,15}""",
            'NC1': r"""(کد)(\\s)?(ملی).{0,15}[0-9]{10}""",
            'NC2': r"""[0-9]{10}.{0,10}(کد)(\\s)?(ملی)""",
            'ADV_NC': r"""(کد)(\\s)?(ملی) \\D{0,15}""",
            'LICNUM': r"""(شماره)? (گواهینامه).{0,15}[0-9]{10}""",
            'ADV_LICNUM': r"""(شماره)? (گواهینامه) \\D{0,15}""",
            'SHABA': r"""IR[0-9]{22,24}""",
            'NUM10': r'\\d{10}', 
            'NUMR10': r'[0-9]{10}',
            'PASSNO': r'[A-Z][0-9]{8}',
            'FMPF': fr'(\\u200c)?[{const.FA_ALPHABET}]+(\\s)',
            'EMAIL': r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])",
            'URL': r"""((http|ftp|https):\\/\\/)?([\\w_-]+(?:(?:\\.[\\w_-]+)+))([\\w.,@?^=%&:\\/~+#-]*[\\w@?^=%&\\/~+#-])""",          'PHONENUMBER': r"""(((([+]|00)98)[-\\s]?)|0)?9\\d{2}[-\\s]?\\d{3}[-\\s]?\\d{2}[-\\s]?\\d{2}(?!\\d)""",
            'CARDNUM': r'(\\d{2})(-|_|\\s{1,3})?(\\d{4})(-|_|\\s{1,3})?(\\d{4})',
            'ONE_W': fr"""([{const.FA_ALPHABET}]|[0-9])+[^\\s]""",
            'PSPACE': r'[\\s|\\u200c]?',
            'HOMENUMBER': fr"""(((([+]|00)98)[-\\s]?)|0)?({const.HOME_PRE_NUM})[1-9][0-9]{{7}}""",
        }

        return annotation_dict

    def create_annotation_dict(self, annotation_path):
        """
        create_annotation_dict will read all annotation text files in utilities/annotations folder and
        create corresponding regex for the annotation folder
        :return: dict
        """
        annotation_dict = {}
        files = os.listdir(annotation_path)
        for f in files:
            key = f.replace('.txt', '')
            annotation_dict[key] = self.create_annotation(f"{annotation_path}/{f}")

        return annotation_dict


class Patterns:
    """
    Patterns class is used to create regexes corresponding to patterns defined in utilities/pattern folder.
    """
    regexes = {}
    cumulative_annotations = {}
    cumulative_annotations_keys = []

    def __init__(self):
        annotations = Annotation()
        self.patterns_path = os.path.join(os.path.dirname(__file__), 'pattern', "")
        self.cumulative_annotations = annotations.annotations_dict
        self.cumulative_annotations_keys = sorted(self.cumulative_annotations, key=len, reverse=True)
        files = os.listdir(self.patterns_path)
        for f in files:
            self.regexes[f.replace('.txt', '').lower()] = self.create_regexes_from_patterns(f"{self.patterns_path}/{f}")

        self.regexes['space'] = [rf"\u200c+", rf"\s+"]

    def pattern_to_regex(self, pattern):
        """
        pattern_to_regex takes pattern and return corresponding regex
        :param pattern: str
        :return: str
        """
        pattern = pattern.replace(" ", r'[\u200c\s]{1,3}')
        annotation_keys = "|".join(self.cumulative_annotations_keys)
        matches = re.findall(annotation_keys, pattern)
        for key in matches:
            pattern = re.sub(f'{key}', fr"(?:{self.cumulative_annotations[key]})", pattern)

        pattern = pattern.replace("<>", r'(?:[\s\u200c])*')
        return pattern

    def create_regexes_from_patterns(self, path):
        """
        create_regexes_from_patterns takes path of pattern folder and return list of regexes corresponding to
        pattern folder.
        :param path: str
        :return: list
        """
        patterns = process_file(path)
        regexes = [self.pattern_to_regex(pattern) for pattern in patterns]
        return regexes
