"""
Crawled from https://shadima.com/%D8%A7%D8%B3%D9%85-%D9%BE%D8%B3%D8%B1/
Thanks!!
"""
import re
from pathlib import Path
class NameExtractor:
    def __init__(self):
        with open(Path(__file__).parent / 'data/Modified_Girls.txt', 'r', encoding='utf-8') as f:
            self.lines_women = f.readlines()
        with open(Path(__file__).parent / 'data/Boys.txt', 'r', encoding='utf-8') as f:
            self.lines_men = f.readlines()

        self.words_men = [line.split('\t')[0] for line in self.lines_men]
        self.words_women = [line.split('\t')[0] for line in self.lines_women]

        self.me_pronoun = ['من', 'می کنم', 'می‌کنم', 'می دهم', 'میدهم']
        self.you_pronoun = ['تو', 'برو', 'بکن', 'بخر', 'بده']
        self.change_pattern = (
            r'(انجام دهنده|مسئول|افراد مسئول|مسئولیت).*?(کار|تسک)?.*?(منتقل شد|انتقال یافت|عوض شد|تغییر '
            r'کرد)?.*?به (.*?)(منتقل شد|انتقال یافت|عوض شد|تغییر کرد)')

    def extract_names(self, text):
        women_names, men_names = self.words_women, self.words_men
        full_names = []
        words = text.split()
        women_prefixes = ['خانم', 'مهندس', 'دکتر', 'استاد']
        men_prefixes = ['آقای', 'آقا', 'دکتر', 'استاد', 'مهندس', 'جناب']
        all_prefixes = women_prefixes + men_prefixes
        i = 0
        while i < len(words):
            if words[i].lower() in women_prefixes:
                if i < len(words) - 1 and words[i + 1].lower() not in all_prefixes:
                    if words[i + 1].lower() in women_names:
                        if i < len(words) - 2:
                            full_names.append(words[i] + ' ' + words[i + 1] + ' ' + words[i + 2])
                            i += 1
                        else:
                            full_names.append(words[i] + ' ' + words[i + 1])
                    else:
                        full_names.append(words[i] + ' ' + words[i + 1])
            elif words[i].lower() in men_prefixes:
                if i < len(words) - 1 and words[i + 1].lower() not in all_prefixes:
                    if words[i + 1].lower() in men_names:
                        if i < len(words) - 2:
                            full_names.append(words[i] + ' ' + words[i + 1] + ' ' + words[i + 2])
                            i += 1
                        else:
                            full_names.append(words[i] + ' ' + words[i + 1])
                    else:
                        full_names.append(words[i] + ' ' + words[i + 1])
            elif words[i].lower() in women_names or words[i].lower() in men_names:
                full_names.append(words[i])
            i += 1

        words = text.split()
        if not full_names:
            for word in words:
                if word in self.me_pronoun:
                    full_names.append('گوینده')
                    break
                if word in self.you_pronoun:
                    full_names.append('شنونده')
                    break
        if not full_names:
            full_names.append('نامعلوم')

        return full_names

    def extract_name_change(self, text):
        match = re.search(self.change_pattern, text)
        if match:
            return match.group(4).strip()
        else:
            return None

