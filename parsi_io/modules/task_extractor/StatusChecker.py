class StatusChecker:
    def __init__(self):
        self.finish_status = ['تموم شد', 'اتمام یافت', 'تمام شد', 'تمام است', 'پایان یافت', 'تمومه', 'تمام شده',
                              'اوکی شد',
                              'اوکی شده', 'تموم شده', 'به اتمام رسید']
        self.urgency_status = ['حتما', 'فورا', 'سریعا', 'به سرعت', 'به شدت', 'حتماً', 'فوراً', 'سریعاً', 'قطعاً']

    def check_status(self, text):
        is_done = False
        is_urgent = False
        text_words = text.split()
        for bigram in self.finish_status:
            if bigram in text:
                is_done = True
                break
        if any(word in text_words for word in self.urgency_status):
            is_urgent = True
        return is_done, is_urgent


