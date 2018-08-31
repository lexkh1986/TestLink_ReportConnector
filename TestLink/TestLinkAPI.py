from robot.libraries.BuiltIn import BuiltIn
from TestReport import TestReport, TestCase
from testlink import *
from numpy import *
import os

class TestLinkAPI(object):
    STATUS = {'p':'PASS', 'f':'FAIL', 'n':'NOT RUN', 'b':'BLOCK'}
    ISAUTOMATED = {False:1, True:2}
    EXEC_PATH =  os.path.dirname(__file__) + '/TL_Exec_Info.txt'
    CONFIG_PATH =  os.path.dirname(__file__) + '/TL_Config.txt'
    
    def __init__(self, TestReport_):
        #TestLink report
        self.TESTLINK_REPORT = TestReport_

        #TestLink connection attributes
        _getVarFromFile(self.EXEC_PATH)
        self.SERVER_URL = 'http://testlink.nexcel.vn/lib/api/xmlrpc/v1/xmlrpc.php'
        self.DEVKEY = data.DEVKEY
        self._report().PROJECT_NAME = data.PROJECT
        self._report().TESTPLAN_NAME = data.TESTPLAN
        self._report().TESTBUILD_NAME = data.TESTBUILD
        self._report().OWNER_NAME = data.RUNOWNER

        _getVarFromFile(self.CONFIG_PATH)
        self._report().IS_JENKIN_RUN = data.isJenkinRun
        self._report().IS_LOG_STEPS = data.isLogSteps
        print self._report().IS_LOG_STEPS, self._report().IS_JENKIN_RUN

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
            iTestLink_details = self.CONN.getTestCase(testcaseexternalid = iTestLink_id)
            TestCase_.setDetail(testlink_id = iTestLink_id, testlink_name = iTestLink_details[0]['name'])
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

    def updateTC_Result(self, TestCase_, switcher):
        #Do synchronize automation results to TestLink...
        if switcher:
            if TestCase_.testlink_id is not None:
                self.CONN.reportTCResult(testcaseexternalid = TestCase_.testlink_id,
                                         status = _dict_getkey(self.STATUS, TestCase_.run_status),
                                         testplanid = self._report().TESTPLAN_ID,
                                         buildname = self._report().TESTBUILD_NAME,
                                         notes = TestCase_.run_msg,
                                         execduration = (TestCase_.run_duration/(1000.0*60))%60)

    def updateTC_Step(self, TestCase_, switcher):
        #Do synchronize automation steps to TestLink...
        if switcher:
            if TestCase_.testlink_id is not None:
                #print self._report().IS_LOG_STEPS
                if not TestCase_.steps:
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                         summary = _parse_html(TestCase_.summary),
                                         executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                         steps=[])
                elif self._report().IS_LOG_STEPS is False:
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                         summary = _parse_html(TestCase_.summary),
                                         executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                         steps=TestCase_.steps)
                else:
                    self.CONN.updateTestCase(testcaseexternalid = TestCase_.testlink_id,
                                         summary = _parse_html(TestCase_.summary + '\n' + '\n'.join('Step: %s\n\tVerify point: %s' % (d['actions'], d['expected_results']) for d in TestCase_.steps)),
                                         executiontype = self.ISAUTOMATED.get(TestCase_.isAutomated),
                                         steps=[])

def _parse_html(string):
    val = string.split('''\n''')
    for i, v in enumerate(val):
        val[i] = '%s<br/>' % v
        val[i] = val[i].replace('Step:','<strong>&emsp;Step:</strong>')
        val[i] = val[i].replace('Checkpoint:','<strong>&emsp;Checkpoint:</strong>')
        val[i] = val[i].replace('Verify point:','<strong>&emsp;Verify point:</strong>')
        val[i] = val[i].replace('*TC Steps:*','<strong>&emsp;*TC Steps:*</strong>')
        val[i] = val[i].replace('*VP:*','<strong>&emsp;*VP:*</strong>')
    completedStr = ''.join(val)
    return completedStr

def _dict_getkey(dict_, value):
    return next((key for key, val in dict_.items() if val == value), None)

def _getVarFromFile(filename):
    import imp
    with open(filename) as f:
        global data
        data = imp.new_module('data')
        exec(f.read(), data.__dict__)
