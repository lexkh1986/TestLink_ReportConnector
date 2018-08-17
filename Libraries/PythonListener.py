from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from ReportPrinter import ReportPrinter

class PythonListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _iTC = None

    def __init__(self):
        self.TESTLINK_REPORT = ReportPrinter()

    def _start_test(self, name, attrs):
        self._iTC = self._buildTC(name, attrs)

    def _end_test(self, name, attrs):
        self._iTC.setResult(attrs['status'],
                            attrs['id'],
                            attrs['elapsedtime'],
                            attrs['message'])
        self.TESTLINK_REPORT.append_tc(self._iTC)

    def _output_file(self, path):
        self.TESTLINK_REPORT.parseReport()
   
    @staticmethod
    def _buildTC(name, details):
        iTestCase = TestCase(id_testlink = 'id',
                             name_short = name,
                             name_long = details['longname'],
                             summary = details['doc'],
                             isCritical = details['critical'])
        return iTestCase
