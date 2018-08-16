class TestReport(object):
    def __init__(self):
        self.hasFailTest = False
        self.isRebot = False
        self.iContent = []

    def append_tc(self, testCase):
        if 'run_status' in testCase.__dict__.keys():
            if testCase.run_status.lower() in ('fail','p'):
                self.hasFailTest = True
        self.iContent.append(testCase)

class TestCase:
    def __init__(self, id_testlink, name_short, name_long, summary, isCritical):
        self.id_testlink = id_testlink
        self.name_short = name_short
        self.name_long = name_long
        self.summary = summary
        self.isCritical = isCritical

    def setResult(self, status, report_link, duration, message):
        self.run_status = status
        self.run_rp_id = report_link
        self.run_duration = duration
        self.run_msg = message

    def _print(self):
        iDetails = {}
        iDetails.update({'id_testlink':self.id_testlink})
        iDetails.update({'name_short':self.name_short})
        iDetails.update({'name_long':self.name_long})
        iDetails.update({'summary':self.summary})
        iDetails.update({'isCritical':self.isCritical})
        iDetails.update({'status':self.run_status})
        iDetails.update({'report_link':self.run_rp_id})
        iDetails.update({'run_duration':self.run_duration})
        iDetails.update({'fail_msg':self.run_msg})
        return iDetails
