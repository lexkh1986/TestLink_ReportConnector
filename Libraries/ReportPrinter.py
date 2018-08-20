from TestReport import TestReport
from numpy import *
import csv

class ReportPrinter(TestReport):
    REPORT_HTML_PATH = 'testlink_report.html'
    REPORT_AUTO_CSV_PATH = 'run_report.csv'
    REPORT_MANUAL_CSV_PATH = 'manual_report.csv'
    REPORT_TEMPLATE_PATH = './Templates/template.html'
    
    def __init__(self):
        super(ReportPrinter, self).__init__()

    @staticmethod    
    def _toCSV(filepath, source):
        with open(filepath, 'wb') as of:
            writer = csv.writer(of)
            writer.writerows(source)

    def parseReport(self, output_path):
        if not self.isRebot:
            if not self.hasFailTest:
                print 'Did not detected a rerun request. Printing html report...'
                self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                                  '%s' % self.REPORT_TEMPLATE_PATH)
            else:
                print 'Detected a rerun request. Printing csv report...'
                self._toCSV('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH), self._export().tolist())
        elif self.isRebot:
            print 'Detected as a rerun process. Merging result...'
            print 'Printing html report...'
            self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                              '%s' % self.REPORT_TEMPLATE_PATH)

        #Export list of manual tests
        print 'Printing manual testcases list...'
        self._toCSV('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH), self._export_manual_report().tolist())

        #Log notifications
        print 'Automated: %s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH)
        print 'Manual   : %s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH)
        print 'Testlink : %s\%s' % (output_path, self.REPORT_HTML_PATH)

    def _export(self):
        iRpt = [self.iContent[0]._print().keys()]
        tmpContent = [elem._print().values() for elem in self.iContent]
        for i, v in enumerate(tmpContent): iRpt.append(v)
        return array(iRpt)

    def _export_manual_report(self):
        try:
            iRpt = [self.iManualContent[0].keys()]
            tmpContent = [elem.values() for elem in self.iManualContent]
            for i, v in enumerate(tmpContent): iRpt.append(v)
            return array(iRpt)
        except Exception:
            return array([['testlink_id', 'testlink_name', 'status']])

    def _export_manual_csv(self, filepath):
        with open(filepath, 'wb') as of:
            writer = csv.writer(of)
            writer.writerows(self._export_manual_report().tolist())

    def _export_html(self, filepath, templatepath):
        print 'Do something'
