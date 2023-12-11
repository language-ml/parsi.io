import json
from datetime import datetime

from DateExtractor import DateExtractor
from NameExtractor import NameExtractor
from StatusChecker import StatusChecker
from TitleExtractor import TitleExtractor

import os

class TaskExtractor:
    OUTPUT_DIR = '../output/'

    def __init__(self):
        self.text = None
        self.task = dict()
        self.title_extractor = TitleExtractor()
        self.name_extractor = NameExtractor()
        self.date_extractor = DateExtractor()
        self.status_checker = StatusChecker()

    def extract(self, text, change: bool = False):
        self.text = text
        is_done, is_urgent = self.status_checker.check_status(text)
        if change:
            title = self.title_extractor.extract_title_change(text)
            assignee = self.name_extractor.extract_name_change(text)
            start_time = self.date_extractor.extract_start_time_change(text)
            end_time = self.date_extractor.extract_end_time_change(text)
            return self.update_task(title, assignee, start_time, end_time, is_done, is_urgent)

        title = self.title_extractor.extract_title(text)
        subtasks = self.title_extractor.extract_subtasks(text)
        assignee = self.name_extractor.extract_names(text, )
        start_time = self.date_extractor.extract_date(text, True)
        end_time = self.date_extractor.extract_date(text, False)
        return self.set_task(title, subtasks, assignee, start_time, end_time, is_done, is_urgent)

    def set_task(self, title: str, subtasks: list, assignee: list, start_time: str, end_time: str, is_done: bool,
                 is_urgent: bool):
        self.task = {
            'title': title,
            'subtasks': subtasks,
            'assign': assignee,
            'start_time': start_time,
            'end_time': end_time,
            'is_done': is_done,
            'is_urgent': is_urgent
        }
        return json.dumps(self.task, indent=2, ensure_ascii=False)

    def update_task(self, title: str = None, assignee: list = None, start_time: str = None, end_time: str = None,
                    is_done: bool = None, is_urgent: bool = None):
        if title:
            self.task['title'] = title
        if assignee:
            self.task['assign'] = assignee
        if start_time:
            self.task['start_time'] = start_time
        if end_time:
            self.task['end_time'] = end_time
        if is_done:
            self.task['is_done'] = is_done
        if is_urgent:
            self.task['is_urgent'] = is_urgent
        return json.dumps(self.task, indent=2, ensure_ascii=False)

    def export_json(self):
        json_data = json.dumps(self.task, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)

        with open(self.OUTPUT_DIR + timestamp + '.json', 'w', encoding='utf-8') as file:
            file.write(json_data)
