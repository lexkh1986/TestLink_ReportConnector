from TestReport import TestReport
from numpy import *
import csv

class ReportPrinter(TestReport):
    REPORT_HTML_PATH = 'testlink_report.html'
    REPORT_AUTO_CSV_PATH = 'run_report.csv'
    REPORT_MANUAL_CSV_PATH = 'manual_report.csv'
    REPORT_TEMPLATE_PATH = 'template.html'
    
    def __init__(self):
        super(ReportPrinter, self).__init__()
    
    def parseReport(self, output_path):
        if not self.isRebot:
            if not self.hasFailTest:
                print 'Did not detected a rerun request. Printing html report...'
                self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                                  '%s\%s' % (output_path, self.REPORT_TEMPLATE_PATH))
            else:
                print 'Detected a rerun request. Printing csv report...'
                self._export_csv('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH))
                print 'Auto result in casv: %s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH)
        elif self.isRebot:
            print 'Detected as a rerun process. Merging result...'
            print 'Printing html report...'

        print 'Printing manual testcases list...'
        self._export_manual_csv('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH))
        print 'Manual report in casv: %s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH)

    def _export(self):
        return array([elem._print() for elem in self.iContent])

    def _export_manual_report(self):
        return array(self.iManualContent)

    def _export_csv(self, filepath):
        keys = self._export()[0].keys()
        with open(filepath, 'wb') as of:
            writer = csv.DictWriter(of, keys)
            writer.writeheader()
            writer.writerows(self._export())

    def _export_manual_csv(self, filepath):
        keys = self._export_manual_report()[0].keys()
        with open(filepath, 'wb') as of:
            writer = csv.DictWriter(of, keys)
            writer.writeheader()
            writer.writerows(self._export_manual_report())

    def _export_html(self, filepath, templatepath):
        print 'Do something'
