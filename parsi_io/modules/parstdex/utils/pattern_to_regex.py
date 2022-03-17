import re
import os
from parsi_io.modules.parstdex.utils.normalizer import Normalizer
from parsi_io.modules.parstdex.utils import const


class Annotation:
    """
    Annotation class is used to create annotation dictionary which will be used for creating regex from patterns
    in following steps.
    """
    annotation_path = os.path.join(os.path.dirname(__file__), 'annotation')
    normalizer = Normalizer()
    annotations_dict = {}

    def __init__(self):
        annotations = self.create_annotation_dict()
        # annotation dictionary includes all annotation folders values
        self.annotations_dict = {
            "RD": annotations['relativeDays'],
            "WD": annotations['weekDays'],
            "Month": annotations['months'],
            "Season": annotations['seasons'],
            "RT": annotations['relativeTime'],
            "TU": annotations['timeUnits'],
            "DU": annotations['dateUnits'],
            "Prev": annotations['prev'],
            "DP": annotations['dayPart'],
            "Next": annotations['next'],
            "SN": annotations['sixtyNum'],
            "HN": annotations['hoursNum'],
            "DN": annotations['dayNumbers'],
            "Hour": annotations['hours'],
            "Min": annotations['minute'],
            "Twelve": annotations['twelve'],
            "ThirtyOne": annotations['thirtyOne'],
            "RY": annotations['relativeYears'],
            "Num": annotations['numbers'],
            "PY": annotations["persianYear"]
            }

    def create_annotation_dict(self):
        """
        create_annotation_dict will read all annotation text files in utilities/annotations folder and
        create corresponding regex for the annotation folder
        :return: dict
        """
        annotation_dict = {}
        files = os.listdir(self.annotation_path)
        for f in files:
            key = f.replace('.txt', '')
            annotation_dict[key] = self.normalizer.normalize_annotation(f"{self.annotation_path}/{f}")

        # all 1 to 4 digit numbers
        annotation_dict['numbers'] = r'\\d{1,4}'

        # supports persian numbers from one to four digits written with persian alphabet
        # example: سال هزار و سیصد و شصت و پنج
        ONE_TO_NINE_JOIN = "|".join(const.ONE_TO_NINE.keys())
        MAGNITUDE_JOIN = "|".join(const.MAGNITUDE.keys())
        HUNDREDS_TEXT_JOIN = "|".join(const.HUNDREDS_TEXT.keys())
        ONE_NINETY_NINE_JOIN = "|".join(list(const.ONE_NINETY_NINE.keys())[::-1])
        annotation_dict["persianYear"] = rf'(?:(?:{ONE_TO_NINE_JOIN})?\\s*(?:{MAGNITUDE_JOIN})?\\s*(?:{const.JOINER})?\\s*(?:{HUNDREDS_TEXT_JOIN})?\\s*(?:{const.JOINER})?\\s*(?:{ONE_NINETY_NINE_JOIN}))'

        return annotation_dict


class Patterns:
    """
    Patterns class is used to create regexes corresponding to patterns defined in utilities/pattern folder.
    """
    annotations = {}
    normalizer = Normalizer()
    patterns_path = os.path.join(os.path.dirname(__file__), 'pattern')
    regexes = {}

    def __init__(self):
        self.annotations = Annotation()
        files = os.listdir(self.patterns_path)
        for f in files:
            self.regexes[f.replace('.txt', '')] = self.create_regexes_from_patterns(f"{self.patterns_path}/{f}")

    def pattern_to_regex(self, pattern):
        """
        pattern_to_regex takes pattern and return corresponding regex
        :param pattern: str
        :return: str
        """
        pattern = pattern.replace(" ", '+\\s')

        for key, value in self.annotations.annotations_dict.items():
            pattern = re.sub(f'{key}', "(?:" + value + ")", pattern)

        pattern = pattern + '+\\s'
        return pattern

    def create_regexes_from_patterns(self, path):
        """
        create_regexes_from_patterns takes path of pattern folder and return list of regexes corresponding to
        pattern folder.
        :param path: str
        :return: list
        """
        patterns = self.normalizer.preprocess_file(path)
        regexes = [self.pattern_to_regex(pattern) for pattern in patterns]
        return regexes

