from TestReport import TestReport
from numpy import *
import csv
import imp

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

   def _export_html(self, filepath, templatepath, nyreport, listmanual):
        '''
            Export to file html (for show report in Jenkins)
            filepath: path save file html\n
            templatepath: template of html file\n
            nyreport: report automation\n
            listmanual: report manual test\n
        '''
            
        pathj = os.path.dirname(__file__)
        runbuild = imp.load_source('cf_run_build', 'cf_run_build.py')
        
        project = runbuild.cfProject
        plan = runbuild.cfPlan
        runowner = runbuild.cfOwner
        build = runbuild.cfBuild
        
        # get build url from jenkins
        pathtxtj = pathj + '/../Build.txt'
        stringbuild = self.read_txt_to_string(pathtxtj).replace('%20',' ')
        # get template html
        reporthtml = self.read_txt_to_string(templatepath)
        
        
        # info result status of all testcase
        num_rows = np.size(nyreport,0)
        numpass = np.count_nonzero(nyreport[:,5]=='PASS')
        numfail = np.count_nonzero(nyreport[:,5]=='FAIL')
        numpassmanual = np.count_nonzero(listmanual[:,2]=='PASS')
        numfailmanual = np.count_nonzero(listmanual[:,2]=='FAIL')
        numnotrunmanual = np.count_nonzero(listmanual[:,2]=='NORUN')
        
        if numfail == 0 and numfailmanual == 0:
            html_string = '''<tr id="title">
                        <th style="background: #00A98F" colspan="5">JOB SUCCESS (PASSED: ''' + str(numpass + numpassmanual) + ''', FAILED: ''' + str(numfail + numfailmanual) + ''', NOT RUN: ''' + str(numnotrunmanual) + ''')</th>
                    </tr>'''
        else:
            html_string = '''<tr id="title">
                        <th style="background: #ff0000" colspan="5">JOB FAILURE (PASSED: ''' + str(numpass + numpassmanual) + ''', FAILED: ''' + str(numfail + numfailmanual) + ''', NOT RUN: ''' + str(numnotrunmanual) + ''')</th>
                    </tr>'''
            
        reporthtml = reporthtml.replace('${ac_title_head}', html_string)
        html_string = '''
                                        <p><span>Run owner:</span> '''+runowner+'''</p>
                                        <ul>
                                            <li><span>Project:</span> '''+project+'''</li>
                                            <li><span>Plan:</span> '''+plan+'''</li>
                                            <li><span>Build:</span> '''+build+'''</li>
                                        </ul>'''
        reporthtml = reporthtml.replace('${ac_info_plan}', html_string)
        html_string = '''
                                            <li><a href="''' + stringbuild +'''robot/report/report.html">Detailed Report</a></li>
                                            <li>Pass Percentage: ''' + str(round(float(numpass) / (numpass + numfail) * 100)) +'''%</li>
                                            <li>PASSED: ''' + str(numpass) + ''', FAILED: ''' + str(numfail) + '''</li>'''
        reporthtml = reporthtml.replace('${ac_info_auto}', html_string)
        if numpassmanual == 0:
            html_string = '''                               
                                        <li><a href="http://testlink.nexcel.vn/lib/results/resultsTC.php?format=0&tplan_id='''+ testPlanID + '''">Detailed Report</a></li>
                                            <li>Pass Percentage: 0%</li>
                                            <li>PASSED: ''' + str(numpassmanual) + ''', FAILED: ''' + str(numfailmanual) + ''', NOT RUN: ''' + str(numnotrunmanual) + '''</li>'''
        else:
            html_string = '''                               
                                        <li><a href="http://testlink.nexcel.vn/lib/results/resultsTC.php?format=0&tplan_id='''+ testPlanID + '''">Detailed Report</a></li>
                                            <li>Pass Percentage: ''' + str(round(float(numpassmanual) / (numpassmanual + numfailmanual + numnotrunmanual) * 100)) +'''%</li>
                                            <li>PASSED: ''' + str(numpassmanual) + ''', FAILED: ''' + str(numfailmanual) + ''', NOT RUN: ''' + str(numnotrunmanual) + '''</li>'''
        reporthtml = reporthtml.replace('${ac_info_manual}', html_string)
        
        html_string=''''''
        i = 0
        string = ''    
        for item in nyreport:
            if item[0] == 'name_short':
                continue
            if item[0] != string:
                suite_string = '''<tr>
                                    <td class="suite" colspan='5'>'''+item[6].replace(".", " >> ")+'''</td>
                                    </tr>'''
                html_string = html_string + suite_string
                string = item[6] 
                
            table_string = ""
            a = int(float(item[7]) // 60)
            if a == 0:
                s = str(int(float(item[7]) % 60)) + "s"
            else:
                s = str(a) + "m " + str(int(float(item[7]) % 60)) + "s"
            if item[1] == 'PASS':
                table_string = '''
                <tr>
                    <td>'''+item[3]+'''</td>
                    <td>'''+item[4]+'''</td>
                    <td>'''+item[0]+'''</td>
                    <td>'''+s+'''</td>
                    <td><a class="status-pass" value="p" target="_blank" rel="noopener" href="''' + stringbuild +'''robot/report/log.html#''' +item[5]+'''">'''+item[1]+'''</a></td>
                </tr>
                '''
            else:
                table_string = '''
                <tr>
                    <td>'''+item[3]+'''</td>
                    <td>'''+item[4]+'''</td>
                    <td>'''+item[0]+'''</td>
                    <td>'''+s+'''</td>
                    <td><a class="status-fail" value="f" target="_blank" rel="noopener" href="'''+ stringbuild + '''robot/report/log.html#'''+item[5]+'''">'''+item[1]+'''</a></td>
                </tr>
                '''
                
            html_string = html_string + table_string
                
        reporthtml = reporthtml.replace('${ac_list_testcase_auto}', html_string)
        html_string = ''''''
        flag = 0
        if listmanual != '':
            for tc in listmanual:
                if tc[0] == 'testlink_id':
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
                note_string = '''<td>''' + tc[0] + '''</td>'''
                note_string = note_string + '''<td>''' + tc[1] + '''</td>'''
                if tc[2] == 'PASS':
                    note_string = note_string + '''<td><a class="status-pass" value="p" target="_blank" rel="noopener">PASS</a></td>
                            </tr>
                    <tr>'''
                elif tc[2] == 'FAIL':
                    note_string = note_string + '''<td><a class="status-fail" value="f" target="_blank" rel="noopener">FAIL</a></td>
                            </tr>
                    <tr>'''
                else:
                    note_string = note_string + '''<td><a class="status-notrun" value="f" target="_blank" rel="noopener">NOT RUN</a></td>
                            </tr>
                    <tr>'''
                html_string = html_string + note_string
        reporthtml = reporthtml.replace('${ac_list_testcase_manual}', html_string)
        
        f = open(filepath,'w')
        f.write(reporthtml)
        f.close()
        
    def read_txt_to_string(self, path):
        filename = os.path.realpath(path)
        file = open(filename, 'r')
           
        return file.read()
