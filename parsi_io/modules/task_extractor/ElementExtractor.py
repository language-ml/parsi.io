from TaskExtractor import TaskExtractor


def run(task_extractor, text, change: bool = False):
    task = task_extractor.extract(text, change)
    print(task)
    task_extractor.export_json()


if __name__ == '__main__':
    task_extractor = TaskExtractor()
    text = ('باید تسک حل تمرین دوم درس را در یک آذر شروع کنیم و تا ده آذر تمام کنیم. برای اینکار باید اول موضوع را '
            'مشخص کنیم و بعد پیادەسازی را انجام دهیم. افراد مسئول حل این تمرین آرش و ریحانه هستن.')
    run(task_extractor, text)
    text = 'ددلاین تسک به ۱۵ آذر منتقل شد'
    run(task_extractor, text, True)
    text = 'تسک حل تمرین دوم درس تمام شد.'
    run(task_extractor, text, True)
