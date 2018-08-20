from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from testlink import *
from numpy import *

class TestLinkAPI(object):
    STATUS = {'p':'PASS', 'f':'FAIL', 'n':'NOT RUN', 'b':'BLOCK'}
    
    def __init__(self, TestReport_):
        self.TESTLINK_REPORT = TestReport_
        self.SERVER_URL = 'http://testlink.nexcel.vn/lib/api/xmlrpc/v1/xmlrpc.php'
        self.DEVKEY = 'e0c8ddc5cbfb54db815a85b4bab5cf31'
        self.CONN = TestLinkHelper(self.SERVER_URL, self.DEVKEY).connect(TestlinkAPIGeneric)
        self._project('NAP Special Delete')
        self.TESTPLAN = 'Demo RobotFramework TestPlan'
        self.TESTBUILD = 'Demo Build 2'

    def _report(self):
        return self.TESTLINK_REPORT

    def _project(self, project_name):
        for elem in self.CONN.getProjects():
            if elem['name'] == project_name:
                self.PROJECT_ID = elem['id']
                self.PROJECT_PREFIX = elem['prefix']
                self.PROJECT_NAME = elem['name']
                return
        raise Exception('Could not found project name %s' % project_name)

    def getTP_ID(self):
        return self.CONN.getTestPlanByName(testprojectname = self.PROJECT_NAME,
                                           testplanname = self.TESTPLAN)[0]['id']

    def getTB_ID(self):
        iBuilds = self.CONN.getBuildsForTestPlan(self.getTP_ID())
        for i in iBuilds:
            if self.TESTBUILD == i['name']:
                return i['id']
        raise Exception('Could find specified TestBuild %s in TestPlan %s' % (self.TESTBUILD, self.TESTPLAN))

    def getTC_TestLink_Details(self, TestCase_):
        iTestLink_id = BuiltIn().get_variable_value('${SUITE METADATA}').get(TestCase_.name_short)
        if iTestLink_id is not None:
            iTestLink_details = self.CONN.getTestCase(testcaseexternalid = '%s-%s' \
                                                      % (self.PROJECT_PREFIX, str(iTestLink_id)))
            TestCase_.setDetail(testlink_id = '%s-%s' % (self.PROJECT_PREFIX, str(iTestLink_id)),
                                testlink_name = iTestLink_details[0]['name'])
        else:
            TestCase_.setDetail(testlink_id = None,
                                testlink_name = None)

    def getRP_TestLink_Manual(self):
        iTC_Auto = [elem._print()['testlink_id'] for elem in self.TESTLINK_REPORT.iContent]
        iTC_TestLink = self.CONN.getTestCasesForTestPlan(testplanid = self.getTP_ID(),
                                                         buildid = self.getTB_ID(),
                                                         details = 'simple').values()
        self.TESTLINK_REPORT.iManualContent = [{'testlink_id':elem[0]['full_external_id'],
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
