from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from testlink import *
from numpy import *
import sys, os

class TestLinkAPI(object):
    STATUS = {'p':'PASS', 'f':'FAIL', 'n':'NOT RUN', 'b':'BLOCK'}
    CONFIG_PATH = './Config/TestLink_connection.py'
    
    def __init__(self, TestReport_):
        #TestLink report
        self.TESTLINK_REPORT = TestReport_

        #TestLink connection attributes
        sys.path.append(os.path.dirname(os.path.expanduser(self.CONFIG_PATH)))
        import TestLink_connection as tl
        self.SERVER_URL = tl.SERVER_URL
        self.DEVKEY = tl.DEVKEY
        self._report().PROJECT_NAME = tl.PROJECT
        self._report().TESTPLAN_NAME = tl.TESTPLAN
        self._report().TESTBUILD_NAME = tl.TESTBUILD

        #Init connection
        self.CONN = TestLinkHelper(self.SERVER_URL, self.DEVKEY).connect(TestlinkAPIGeneric)

        #Get information from TestLink server
        self._project()
        self._testplan()
        self._testbuild()

    def _report(self):
        return self.TESTLINK_REPORT

    def _project(self):
        for elem in self.CONN.getProjects():
            if elem['name'] == self._report().PROJECT_NAME:
                self._report().PROJECT_ID = elem['id']
                self._report().PROJECT_PREFIX = elem['prefix']
                return
        raise Exception('Could not found project name %s' % self._report().PROJECT_NAME)

    def _testplan(self):
        self._report().TESTPLAN_ID = self.CONN.getTestPlanByName(testprojectname = self._report().PROJECT_NAME,
                                                                 testplanname = self._report().TESTPLAN_NAME)[0]['id']

    def _testbuild(self):
        iBuilds = self.CONN.getBuildsForTestPlan(self._report().TESTPLAN_ID)
        for i in iBuilds:
            if self._report().TESTBUILD_NAME == i['name']:
                self._report().TESTBUILD_ID = i['id']
                return
        raise Exception('Could find specified TestBuild %s in TestPlan %s' % (self._report().TESTBUILD_NAME,
                                                                              self._report().TESTPLAN_NAME))

    def getTC_TestLink_Details(self, TestCase_):
        iTestLink_id = BuiltIn().get_variable_value('${SUITE METADATA}').get(TestCase_.name_short)
        if iTestLink_id is not None:
            iTestLink_details = self.CONN.getTestCase(testcaseexternalid = '%s-%s' \
                                                      % (self._report().PROJECT_PREFIX, str(iTestLink_id)))
            TestCase_.setDetail(testlink_id = '%s-%s' % (self._report().PROJECT_PREFIX, str(iTestLink_id)),
                                testlink_name = iTestLink_details[0]['name'])
        else:
            TestCase_.setDetail(testlink_id = None,
                                testlink_name = None)

    def getRP_TestLink_Manual(self):
        iTC_Auto = [elem._print()['testlink_id'] for elem in self._report().iContent]
        iTC_TestLink = self.CONN.getTestCasesForTestPlan(testplanid = self._report().TESTPLAN_ID,
                                                         buildid = self._report().TESTBUILD_ID,
                                                         details = 'simple').values()
        self._report().iManualContent = [{'testlink_id':elem[0]['full_external_id'],
                                          'testlink_name':elem[0]['tcase_name'],
                                          'status':self.STATUS.get(elem[0]['exec_status'])} \
                                         for elem in iTC_TestLink \
                                         if elem[0]['full_external_id'] not in iTC_Auto]

    def updateRP_Result(self, switcher):
        if switcher:
            print '\nDo synchronize automation results to TestLink...'

    def updateTC_Steps(self, TestCase_, switcher):
        if switcher:
            if TestCase_.testlink_id is not None:
                print '\nDo synchronize TestCase steps to TestLink...'
