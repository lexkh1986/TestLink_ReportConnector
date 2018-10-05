from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from TestLinkAPI import TestLinkAPI
from ReportPrinter import ReportPrinter
from Misc import *
import sys, os

class TestLinkListener(object):
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _iTC = None
    _iSyncResults = True
    _iSyncSteps = True

    def __init__(self):
        self.TESTLINK_REPORT = ReportPrinter()
        self.TESTLINK_API = TestLinkAPI(self.TESTLINK_REPORT)
        self.TESTLINK_REPORT.apiRef = self.TESTLINK_API
        if set(sys.argv) & set(['-R','--rerunfailed']):
            self.TESTLINK_REPORT.isRebot = True

    def start_suite(self, name, attrs):
        self.ROBOT_OUTPUT_DIR = BuiltIn().get_variable_value('${OUTPUT DIR}')
        isMeta, iCSVMeta = self._syncTLMapper(attrs['tests'], attrs['source'])
        if isMeta:
            iSuiteMeta = BuiltIn().get_variable_value('${SUITE METADATA}')
            for iTC in [(elem.get('Test'), elem.get('TestLink_ID')) for elem in iCSVMeta]:
                if iTC[0] not in iSuiteMeta.keys():
                    BuiltIn().set_suite_metadata(iTC[0], iTC[1], True)

    def start_test(self, name, attrs):
        self._iTC = self._buildTC(name, attrs) #Build testcase object
        BuiltIn().set_test_variable('${TESTLINK_iTC}', self._iTC)

    def end_test(self, name, attrs):
        self._buildTCResult(self._iTC, attrs) #Build result object
        self.TESTLINK_API.getTC_TestLink_Details(self._iTC) #Get testlink id
        self.TESTLINK_REPORT.append_tc(self._iTC) #Add testcase with result to testreport list
        self.TESTLINK_API.updateTC_Step(self._iTC, self._iSyncSteps) #Log auto steps to TestCase sumarry
        self.TESTLINK_API.updateTC_Result(self._iTC, self._iSyncResults) #Update auto result to TestLink

    def output_file(self, path):
        if self.TESTLINK_REPORT.isRebot == False:
            self.TESTLINK_API.getRP_TestLink_Manual() #Build list of manual testcases
        self.TESTLINK_REPORT.parseReport(self.ROBOT_OUTPUT_DIR) # Build html report

    @staticmethod
    def _buildTC(name, attrs):
        iTestCase = TestCase(name_short = name,
                             name_long = attrs['longname'],
                             summary = attrs['doc'],
                             isCritical = attrs['critical'],
                             isAutomated = True)
        return iTestCase

    @staticmethod
    def _buildTCResult(iTC_, attrs):
        iTC_.setResult(attrs['status'],
                       attrs['id'],
                       attrs['elapsedtime'],
                       attrs['message'])
        iTC_.summary = attrs['doc']
        
    @staticmethod
    def _syncTLMapper(tcList, source):
        if tcList:
            iMapperPath = '%s.csv' % source[:-4]
            iMapperExists = os.path.isfile(iMapperPath)
            if iMapperExists:
                iCurDict = read_csv_dict(iMapperPath)
                iCurName = [elem.get('Test') for elem in iCurDict]
                for iNew in tcList:
                    if iNew not in iCurName: iCurDict.append({'Test':iNew, 'TestLink_ID':''})
                write_csv_dict(iMapperPath, iCurDict)
            else:
                iCurDict = [{'Test':elem, 'TestLink_ID':''} for elem in tcList]
                #write_csv_dict(iMapperPath, iCurDict)
            return iMapperExists, iCurDict
        return False, []
