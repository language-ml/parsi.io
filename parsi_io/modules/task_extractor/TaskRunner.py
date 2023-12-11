from TaskExtractor import TaskExtractor

class TaskRunner:
    def __init__(self):
        self.task_extractor = TaskExtractor()

    def run(self, text, change: bool = False):
        task = self.task_extractor.extract(text, change)
        print(task)
        self.task_extractor.export_json()
        return task
if __name__ == '__main__':
    model = TaskRunner()
    text = ('باید تسک حل تمرین دوم درس را در یک آذر شروع کنیم و تا ده آذر تمام کنیم. برای اینکار باید اول موضوع را '
            'مشخص کنیم و بعد پیادەسازی را انجام دهیم. افراد مسئول حل این تمرین آرش و ریحانه هستن.')
    model.run(text)

