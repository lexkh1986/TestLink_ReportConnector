from TestReport import TestReport
from numpy import *
import csv
import os

class ReportPrinter(TestReport):
    REPORT_HTML_PATH = 'testlink_report.html'
    REPORT_AUTO_CSV_PATH = 'run_report.csv'
    REPORT_MANUAL_CSV_PATH = 'manual_report.csv'
    REPORT_TEMPLATE_PATH = '/Templates/template.html'
    
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
                                  '%s' % self.REPORT_TEMPLATE_PATH, self._export(), self._export_manual_report())
            else:
                print 'Detected a rerun request. Printing csv report...'
                self._toCSV('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH), self._export().tolist())
                #Export list of manual tests
                print 'Printing manual testcases list...'
                self._toCSV('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH), self._export_manual_report().tolist())

        elif self.isRebot:
            print 'Detected as a rerun process. Merging result...'
            array_auto_1 = genfromtxt('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH), delimiter=',',dtype=str)
            array_auto_2 = self._export()
            
            for item in array_auto_2: array_auto_1[where((array_auto_1[:,0]==item[0]) & (array_auto_1[:,4]==item[4])), 1] = item[1]
            array_manual = genfromtxt('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH), delimiter=',',dtype=str)
            print 'Printing html report...'
            self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                              '%s' % self.REPORT_TEMPLATE_PATH, array_auto_1, array_manual)

        #Log notifications
        print 'Automated: %s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH)
        print 'Manual   : %s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH)
        print 'Testlink : %s\%s' % (output_path, self.REPORT_HTML_PATH)

    def _export(self):
        iRpt = [self.iContent[0]._print().keys()]
        del iRpt[0][7]
        for elem in self.iContent:
            v = elem._print().values()
            del v[7]
            iRpt.append(v)
        
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

    def _export_html(self, filepath, templatepath, nyreport, nymanual):
        '''
            Export to file html (for show report in Jenkins)
            filepath: path save file html\n
            templatepath: template of html file\n
            nyreport: report automation\n
            nymanual: report manual test\n
        '''
           
        project = self.PROJECT_NAME
        plan = self.TESTPLAN_NAME
        runowner = 'Jane Dinh'
        build = self.TESTBUILD_NAME
        
        # get build url from jenkins
        stringbuild = self.read_txt_to_string('./Build.txt').replace('%20',' ')
        # get template html
        reporthtml = self.read_txt_to_string(templatepath)
        # info result status of all testcase
        num_rows = size(nyreport,0)
        numpass = count_nonzero(nyreport[:,1]=='PASS')
        numfail = count_nonzero(nyreport[:,1]=='FAIL')
        numskip = count_nonzero(nyreport[:,1]=='SKIP')
        if nymanual.shape[0] > 1:
            numpassmanual = count_nonzero(nymanual[:,0]=='PASS')
            numfailmanual = count_nonzero(nymanual[:,0]=='FAIL')
            numnotrunmanual = count_nonzero(nymanual[:,0]=='NOT RUN')
        else:
            numpassmanual = 0
            numfailmanual = 0
            numnotrunmanual = 0
            print 'Dont have manual testcase'
            
        per = '0' if numpassmanual == 0 else str(round(float(numpassmanual) / (numpassmanual + numfailmanual + numnotrunmanual) * 100))
        for r in (('${ac_count_pass}', str(numpass + numpassmanual)),('${ac_count_fail}', str(numfail + numfailmanual)), ('${ac_count_notrun}', str(numnotrunmanual)), ('${ac_runowner}', runowner), ('${ac_project}', project),
                  ('${ac_plan}', plan), ('${ac_build}', build), ('${ac_link_build}', stringbuild), ('${ac_auto_percent}', str(round(float(numpass) / (numpass + numfail) * 100))), ('${ac_auto_pass}', str(numpass)), ('${ac_auto_fail}', str(numfail)), ('${ac_auto_skip}', str(numskip)),
                  ('${ac_manual_percent}', per), ('${ac_manual_pass}', str(numpassmanual)), ('${ac_manual_fail}', str(numfailmanual)), ('${ac_manual_notrun}', str(numnotrunmanual)), ('${ac_status}', 'JOB SUCCESS') if numfail == 0 and numfailmanual == 0 else ('${ac_status}', 'JOB FAILURE')):
            reporthtml = reporthtml.replace(*r)
        
        html_string=''''''
        i = 0
        string = ''    
        for item in nyreport:
            if item[0] == 'name_short': continue
            suite = item[8].replace('.' + item[0], '')
            if suite != string:
                suite_string = '''<tr>
                                    <td class="suite" colspan='5'>'''+suite.replace(".", " >> ")+'''</td>
                                    </tr>'''
                html_string = html_string + suite_string
                string = suite 
                
            table_string = ""

            s = str(round((float(item[7])/(1000.00*60))%60, 2)) + ' m'
            
            testlinkID = 'None' if (item[4]==None or item[4]=='') else item[4]
            testname = 'None' if (item[3]==None or item[3]=='') else item[3]
            table_string = '''
                <tr>
                    <td>'''+ testlinkID +'''</td>
                    <td>'''+testname+'''</td>
                    <td>'''+item[0]+'''</td>
                    <td>'''+s+'''</td>'''
            if item[1] == 'PASS':
                table_string = table_string + '''
                    <td><a class="status-pass" value="p" target="_blank" rel="noopener" href="''' + stringbuild +'''robot/report/log.html#''' +item[6]+'''">'''+item[1]+'''</a></td>
                </tr>
                '''
            else:
                table_string = table_string + '''
                    <td><a class="status-fail" value="f" target="_blank" rel="noopener" href="'''+ stringbuild + '''robot/report/log.html#'''+item[6]+'''">'''+item[1]+'''</a></td>
                </tr>
                '''   
            html_string = html_string + table_string
            
        reporthtml = reporthtml.replace('${ac_list_testcase_auto}', html_string)
        html_string = ''''''
        flag = 0
        
        try:
            if nymanual.shape[0] > 1:
                for tc in nymanual:
                    if tc[0] == 'status':
                        continue
                    if flag == 0:
                        html_string = html_string + '''<table> 
                        <thead>                        
                            <tr id="title"><th style="background: white; color:black" colspan="5">List manual testcases: </th></tr>
                            <tr id="title" style="background: #00A98F">
                                <th style="width: 19%;">Testlink ID</th>
                                <th style="width: 73%;">Testcase name</th>
                                <th style="width: 8%;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>'''
                        flag = 1
                    note_string = '''<td>''' + tc[2] + '''</td>'''
                    note_string = note_string + '''<td>''' + tc[1] + '''</td>'''
                    if tc[0] == 'PASS':
                        note_string = note_string + '''<td><a class="status-pass" value="p" target="_blank" rel="noopener">PASS</a></td>
                                </tr>
                        <tr>'''
                    elif tc[0] == 'FAIL':
                        note_string = note_string + '''<td><a class="status-fail" value="f" target="_blank" rel="noopener">FAIL</a></td>
                                </tr>
                        <tr>'''
                    else:
                        note_string = note_string + '''<td><a class="status-notrun" value="f" target="_blank" rel="noopener">NOT RUN</a></td>
                                </tr>
                        <tr>'''
                    html_string = html_string + note_string
        except IndexError:
            print 'Dont have manual testcase'
        reporthtml = reporthtml.replace('${ac_list_testcase_manual}', html_string)
        f = open(filepath,'w')
        f.write(reporthtml)
        f.close()
        
    def read_txt_to_string(self, path):
        filename = os.path.realpath(path)
        file = open(filename, 'r')
           
        return file.read()
