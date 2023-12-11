from .TaskExtractor import TaskExtractor

class TaskRunner:
    def __init__(self):
        self.task_extractor = TaskExtractor()

    def run(self, text, change: bool = False):
        task = self.task_extractor.extract(text, change)
        print(task)
        self.task_extractor.export_json()
        return task
