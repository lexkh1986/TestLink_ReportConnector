from TestReport import TestReport
from numpy import *
import csv

class ReportPrinter(TestReport):
    REPORT_HTML_PATH = 'testlink_report.html'
    REPORT_CSV_PATH = '1st_run_report.csv'
    REPORT_TEMPLATE_PATH = 'template.html'
    
    def __init__(self):
        super(ReportPrinter, self).__init__()

    def setpath_html_report(self, path):
        self.REPORT_HTML_PATH = path

    def setpath_csv_report(self, path):
        self.REPORT_CSV_PATH = path

    def setpath_template_report(self, path):
        self.REPORT_TEMPLATE_PATH = path
    
    def parseReport(self):
        if not self.isRebot:
            if not self.hasFailTest:
                print 'Did not detected a rerun request. Printing html report...'
                self._export_html(self.REPORT_HTML_PATH,
                                  self.REPORT_TEMPLATE_PATH)
            else:
                print 'Detected a rerun request. Printing csv report...'
                self._export_csv(self.REPORT_CSV_PATH)
        elif self.isRebot:
            print 'Detected as a rerun process. Merging result...'
            print 'Printing html report...'

    def _export(self):
        return array([elem._print() for elem in self.iContent])

    def _export_csv(self, filepath):
        keys = self._export()[0].keys()
        with open(filepath, 'wb') as of:
            writer = csv.DictWriter(of, keys)
            writer.writeheader()
            writer.writerows(self._export())

    def _export_html(self, filepath, templatepath):
        print 'Do something'
