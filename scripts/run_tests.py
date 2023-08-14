import time

import pytest


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        print(exitstatus, dir(exitstatus))
        self.exitcode = exitstatus
        self.passed = terminalreporter.stats.get("passed", [])
        self.failed = terminalreporter.stats.get("failed", [])
        self.xfailed = terminalreporter.stats.get("xfailed", [])
        self.skipped = terminalreporter.stats.get("skipped", [])
        self.num_passed = len(self.passed)
        self.num_failed = len(self.failed)
        self.num_xfailed = len(self.xfailed)
        self.num_skipped = len(self.skipped)

        self.total_duration = time.time() - terminalreporter._sessionstarttime


collector = ResultsCollector()
retcode = pytest.main(["-v", "tests/test_capstd.py"], plugins=[collector])

report = collector.reports[0]

print(report.capstderr)
print(report.capstdout)

1 + 1
