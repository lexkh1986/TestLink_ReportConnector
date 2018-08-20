from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from TestLinkAPI import TestLinkAPI
from ReportPrinter import ReportPrinter

class PythonListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _iTC = None
    _iSyncResults = True
    _iSyncSteps = False

    def __init__(self):
        self.TESTLINK_REPORT = ReportPrinter()
        self.TESTLINK_API = TestLinkAPI(self.TESTLINK_REPORT)

    def start_suite(self, name, attrs):
        self.ROBOT_OUTPUT_DIR = BuiltIn().get_variable_value('${OUTPUT DIR}')

    def start_test(self, name, attrs):
        self._iTC = self._buildTC(name, attrs) #Build testcase object
        self.TESTLINK_API.getTC_TestLink_Details(self._iTC) #Get testlink id

    def end_test(self, name, attrs):
        self._buildResult(self._iTC, attrs) #Build result object
        self.TESTLINK_REPORT.append_tc(self._iTC) #Add testcase with result to testreport list
        self.TESTLINK_API.updateTC_Steps(self._iTC, self._iSyncSteps) #Log auto steps to TestCase sumarry

    def output_file(self, path):
        self.TESTLINK_API.getRP_TestLink_Manual() #Build list of manual testcases
        self.TESTLINK_API.updateRP_Result(self._iSyncResults) #Update auto result to TestLink
        self.TESTLINK_REPORT.parseReport(self.ROBOT_OUTPUT_DIR) # Build html report

    @staticmethod
    def _buildTC(name, attrs):
        iTestCase = TestCase(name_short = name,
                             name_long = attrs['longname'],
                             summary = attrs['doc'],
                             isCritical = attrs['critical'])
        return iTestCase

    @staticmethod
    def _buildResult(iTC_, attrs):
        #If TestCase not found on TestLink: mark as Fail
        if iTC_.testlink_id is None:
            attrs['status'] = 'SKIP'
            attrs['message'] = 'Unidetified ID from TestLink'

        iTC_.setResult(attrs['status'],
                       attrs['id'],
                       attrs['elapsedtime'],
                       attrs['message'])
        
