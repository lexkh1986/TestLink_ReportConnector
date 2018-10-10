from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from Misc import *
from testlink import *
from numpy import *
import os, traceback

class TestLinkAPI(object):
    STATUS = {'p':'PASS', 'f':'FAIL', 'n':'NOT RUN', 'b':'BLOCK'}
    ISAUTOMATED = {False:1, True:2}
    EXEC_PATH =  os.path.dirname(__file__) + '\TL_Exec_Info.txt'
    CONFIG_PATH =  os.path.dirname(__file__) + '\TL_Config.txt'
    
    def __init__(self, TestReport_):
        #TestLink report
        self.TESTLINK_REPORT = TestReport_

        #TestLink connection attributes
        data = getVarFromFile(self.EXEC_PATH)
        self.SERVER_URL = 'http://testlink.nexcel.vn/lib/api/xmlrpc/v1/xmlrpc.php'
        self.DEVKEY = data.DEVKEY
        self._report().PROJECT_NAME = data.PROJECT
        self._report().TESTPLAN_NAME = data.TESTPLAN
        self._report().TESTBUILD_NAME = data.TESTBUILD
        self._report().OWNER_NAME = data.RUNOWNER

        data = getVarFromFile(self.CONFIG_PATH)
        self._report().IS_JENKIN_RUN = data.isJenkinRun
        self._report().USE_SUMMARY_AS_STEP = data.useSummaryAsStep
        self._report().USE_CSV_MAPPER = data.useCSVTestLinkMapper
        self._report().SYNC_STEPS = data.syncTestCaseSteps
        self._report().SYNC_RESULTS = data.syncTestCaseResult

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

    def getTC_Steps(self, iTestLink_id):
        try:
            if self._report().USE_SUMMARY_AS_STEP is False:
                return parse_steps(self.CONN.getTestCase(testcaseexternalid = str(iTestLink_id))[0]['steps'], True)
            else:
                return self.CONN.getTestCase(testcaseexternalid = str(iTestLink_id))[0]['summary']
        except Exception, err:
            traceback.print_exc()
            return ''

    def getTC_TestLink_Details(self, TestCase_):
        iTestLink_id = TestCase_.testlink_id
        if iTestLink_id is None:
            iTestLink_id = BuiltIn().get_variable_value('${SUITE METADATA}').get(TestCase_.name_short)
        if iTestLink_id not in (None, ''):
            iTestLink_details = self.CONN.getTestCase(testcaseexternalid = iTestLink_id)
            TestCase_.setDetail(testlink_id = iTestLink_id,
                                testlink_name = iTestLink_details[0]['name'])

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

    def getTC_Testlink_Path(self, iTestLink_id, iTestLink_name):
        iTC_full_path = ''
        if iTestLink_id is not None and iTestLink_name is not None:
            try:
                for iTC_Testlink in self.CONN.getTestCaseIDByName(testcasename=str(iTestLink_name)):
                    iTC_ExternalID = iTC_Testlink['tc_external_id']
                    iTC_ParentID = iTC_Testlink['parent_id']
                    if iTC_ExternalID == iTestLink_id: break
                iTC_full_path = iTestLink_name
                isParent = 1
                while isParent == 1:
                    isParent = 0
                    try:
                        iTC_Testsuite = self.CONN.getTestSuiteByID(testsuiteid=iTC_ParentID)
                        iTC_ParentID = iTC_Testsuite['parent_id']
                        iTC_Name = iTC_Testsuite['name']
                        iTC_full_path = iTC_Name + ' >> ' + iTC_full_path
                        isParent = 1
                    except Exception, err: isParent = 0
            except Exception, err: print 'Testcase is not included in TestPlan'
        return iTC_full_path

    def updateTC_Result(self, TestCase_, switcher):
        #Do synchronize automation results to TestLink...
            if switcher:
                if TestCase_.testlink_id is not None:
                    try:
                        self.CONN.reportTCResult(testcaseexternalid = TestCase_.testlink_id,
                                                 status = dict_getkey(self.STATUS, TestCase_.run_status),
                                                 testplanid = self._report().TESTPLAN_ID,
                                                 buildname = self._report().TESTBUILD_NAME,
                                                 notes = TestCase_.run_msg,
                                                 execduration = (TestCase_.run_duration/(1000.0*60))%60)
                    except Exception, err:
                        if str(err).find('3030') == 0:
                            print '\nNOTE: This testcase not linked to testplan: %s (%s). Run result will be tosssed out.'\
                                  % (TestCase_.testlink_id, TestCase_.testlink_name)
                            TestCase_.testlink_name = '%s (Not included in TestPlan)' % TestCase_.testlink_name
                            TestCase_.run_status = 'SKIP'
                else:
                    TestCase_.testlink_name = 'Unidetified ID from TestLink'
                    TestCase_.run_status = 'SKIP'
                    print '\nNOTE: This testcase has no linked id to TestLink. Run result will be tosssed out.'

    def updateTC_Step(self, TestCase_, switcher):
        #Do synchronize automation steps to TestLink...
        if switcher:
            if TestCase_.testlink_id is not None:
                if not TestCase_.steps:
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                         summary = parse_summary(TestCase_.summary),
                                         executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                         steps=[])
                elif self._report().USE_SUMMARY_AS_STEP is False:
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                         summary = parse_summary(TestCase_.summary),
                                         executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                         steps=TestCase_.steps)
                else:
                    stepStr = '\n'.join('%s\n%s' % (d['actions'], d['expected_results'])
                                        if d['expected_results'] not in ('', None)
                                        else '%s' % d['actions'] for d in TestCase_.steps)
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                             summary = parse_summary('%s\n%s' % (TestCase_.summary, stepStr) if TestCase_.summary not in (None, '') else '%s' % stepStr),
                                             executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                             steps=[])
