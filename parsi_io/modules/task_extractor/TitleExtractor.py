import re


class TitleExtractor:
    def __init__(self):
        self.title_patterns = [
            r'باید\s+(.*?)\s+را',
            r'باید\s+(.*?)\s+انجام دهیم',
            r'باید\s+(.*?)\s+شروع کنیم',
            r'تسک\s+(.*?)\s+است',
            r'وظیفه\s+(.*?)\s+است',
            r'ضروری است\s+(.*?)\s+را',
            r'نیاز به\s+(.*?)\s+داریم',
            r'مهم است\s+(.*?)\s+را',
            r'در دستور کار\s+(.*?)\s+است',
        ]

        self.subtask_patterns = [
            r'ابتدا\s+(.*?)\s+و\s+سپس\s+([^\.و]+)',
            r'اول\s+(.*?)\s+و بعد\s+([^\.و]+)',
            r'اول\s+(.*?)\s+بعد\s+([^\.و]+)',
            r'در مرحله اول\s+(.*?)\s+سپس\s+([^\.و]+)',
            r'از یک سو\s+(.*?)\s+و از سوی دیگر\s+([^\.و]+)',
            r'شروع با\s+(.*?)\s+و در نهایت\s+([^\.و]+)',
        ]

        self.change_patterns = [
            r'عنوان\s+(.*?)\s+به\s+(.*?)\s+تغییر (کرد|یافت)',
            r'عنوان\s+(.*?)\s+به\s+(.*?)\s+عوض (کرد|یافت)',
        ]

    def extract_title(self, text):
        for pattern in self.title_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def extract_subtasks(self, text):
        for pattern in self.subtask_patterns:
            match = re.search(pattern, text)
            if match:
                return match.groups()
        return []

    def extract_title_change(self, text):
        for pattern in self.change_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None


if __name__ == '__main__':
    title_extractor = TitleExtractor()

    text = ('باید تسک حل تمرین دوم درس را در یک آذر شروع کنیم و تا ده آذر تمام کنیم. برای اینکار باید اول موضوع را '
            'مشخص کنیم و بعد پیادەسازی را انجام دهیم.')

    title = title_extractor.extract_title(text)
    subtasks = title_extractor.extract_subtasks(text)

    print('title:', title)
    print('subtasks:', subtasks)
