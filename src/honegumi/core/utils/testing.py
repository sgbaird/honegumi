import time
from typing import List

import _pytest
import pytest


class ResultsCollector:
    """A class for collecting and summarizing results of pytest test runs.

    https://stackoverflow.com/a/72278485/13697228

    Attributes
    ----------
    reports : List[pytest.TestReport]
        A list of test reports generated during the test run.
    collected : int
        The number of test items collected for the test run.
    exitcode : int
        The exit code of the test run.
    passed : List[pytest.TestReport]
        A list of test reports for tests that passed.
    failed : List[pytest.TestReport]
        A list of test reports for tests that failed.
    xfailed : List[pytest.TestReport]
        A list of test reports for tests that were expected to fail but passed.
    skipped : List[pytest.TestReport]
        A list of test reports for tests that were skipped.
    total_duration : float
        The total duration of the test run in seconds.

    Examples
    --------
    >>> collector = ResultsCollector()
    >>> # run pytest tests
    >>> collector.total_duration
    10.123456789
    """

    def __init__(self) -> None:
        self.reports: List[pytest.TestReport] = []
        self.collected: int = 0
        self.exitcode: int = 0
        self.passed: List[pytest.TestReport] = []
        self.failed: List[pytest.TestReport] = []
        self.xfailed: List[pytest.TestReport] = []
        self.skipped: List[pytest.TestReport] = []
        self.total_duration: float = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(
        self, item: pytest.Item, call: pytest.CallInfo
    ) -> None:
        """A pytest hook for collecting test reports.

        Parameters
        ----------
        item : pytest.Item
            The test item being run.
        call : pytest.CallInfo
            The result of running the test item.

        Examples
        --------
        >>> item = ...
        >>> call = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_runtest_makereport(item, call)
        """

        outcome = yield
        report = outcome.get_result()
        if report.when == "call":
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items: List[pytest.Item]) -> None:
        """A pytest hook for modifying collected test items.

        Parameters
        ----------
        items : List[pytest.Item]
            A list of pytest.Item objects representing the collected test items.

        Examples
        --------
        >>> items = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_collection_modifyitems(items)
        """

        self.collected = len(items)

    def pytest_terminal_summary(
        self, terminalreporter: _pytest.terminal.TerminalReporter, exitstatus: int
    ) -> None:
        """A pytest hook for summarizing test results.

        Parameters
        ----------
        terminalreporter : pytest.terminal.TerminalReporter
            The terminal reporter object used to report test results.
        exitstatus : int
            The exit status code of the test run.

        Examples
        --------
        >>> terminalreporter = ...
        >>> exitstatus = ...
        >>> collector = ResultsCollector()
        >>> collector.pytest_terminal_summary(terminalreporter, exitstatus)
        """

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
