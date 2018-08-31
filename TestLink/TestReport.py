class TestReport(object):
    def __init__(self):
        self.hasFailTest = False
        self.isRebot = False
        self.iContent = []
        self.iManualContent = []

    def append_tc(self, testCase):
        if 'run_status' in testCase.__dict__.keys():
            if testCase.run_status.lower() in ('fail','p'):
                self.hasFailTest = True
        self.iContent.append(testCase)

class TestCase:
    def __init__(self, name_short, name_long, summary, isAutomated, isCritical):
        self.name_short = name_short
        self.name_long = name_long
        self.summary = summary
        self.isAutomated = isAutomated
        self.isCritical = isCritical
        self.steps = []

    def setSteps(self, actions, expected_results):
        self.steps.append({'step_number':len(self.steps)+1,
                           'actions':actions,
                           'expected_results':expected_results,
                           'execution_type':2})

    def setDetail(self, testlink_id, testlink_name):
        self.testlink_id = testlink_id
        self.testlink_name = testlink_name

    def setResult(self, status, report_link, duration, message):
        self.run_status = status
        self.run_rp_id = report_link
        self.run_duration = duration
        self.run_msg = message

    def _print(self):
        iDetails = {}
        iDetails.update({'testlink_id':self.testlink_id})
        iDetails.update({'testlink_name':self.testlink_name})
        iDetails.update({'name_short':self.name_short})
        iDetails.update({'name_long':self.name_long})
        #iDetails.update({'summary':self.summary})
        iDetails.update({'isCritical':self.isCritical})
        iDetails.update({'status':self.run_status})
        iDetails.update({'report_link':self.run_rp_id})
        iDetails.update({'run_duration':self.run_duration})
        #iDetails.update({'test_msg':self.run_msg})
        return iDetails
