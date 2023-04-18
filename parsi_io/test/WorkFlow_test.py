from parsi_io.modules.work_flow_extractor import work_flow

from .base import *


class WorkFlow(BaseTest):
    def test_work_flow(self):
        obj = work_flow()
        self.run_test(obj, "/test/testcases/WorkFlow.json")
