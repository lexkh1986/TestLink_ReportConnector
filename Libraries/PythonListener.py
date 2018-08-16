from TestReport import TestReport, TestCase
import HTMLParser

class PythonListener:
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _iTC = None

    def __init__(self):
        self.TESTLINK_REPORT = TestReport()

    def start_test(self, name, attrs):
        self._iTC = self._buildTC(name, attrs)

    def end_test(self, name, attrs):
        self._iTC.setResult(attrs['status'],
                            attrs['id'],
                            attrs['elapsedtime'],
                            attrs['message'])
        self.TESTLINK_REPORT.append_tc(self._iTC)

    def output_file(self, path):
        print self.TESTLINK_REPORT.export()
        self.TESTLINK_REPORT.export_csv('report.csv')

    @staticmethod
    def _buildTC(name, details):
        iTestCase = TestCase(id_testlink = 'id',
                             name_short = name,
                             name_long = details['longname'],
                             summary = details['doc'],
                             isCritical = details['critical'])
        return iTestCase
