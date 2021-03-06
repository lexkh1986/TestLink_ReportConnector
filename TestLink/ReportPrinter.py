from TestReport import TestReport
from numpy import *
import re, os, csv, traceback

class ReportPrinter(TestReport):
    REPORT_HTML_PATH = 'testlink_report.html'
    REPORT_AUTO_CSV_PATH = 'run_report.csv'
    REPORT_MANUAL_CSV_PATH = 'manual_report.csv'
    REPORT_CSV_DELIMETER = '|'
    REPORT_TEMPLATE_PATH = '%s/%s' % (os.path.dirname(__file__), 'Templates/template.html')
    
    def __init__(self):
        super(ReportPrinter, self).__init__()

    def parseReport(self, output_path):
        if not self.isRebot:
            if self.hasFailTest:
                #Export list of automated tests in csv for 2nd run case
                print 'Printing automated testcases list...'
                toCSV('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH), self._export().tolist(), self.REPORT_CSV_DELIMETER)

            #Export list of manual tests
            print 'Printing manual testcases list...'
            toCSV('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH), self._export_manual_report().tolist(), self.REPORT_CSV_DELIMETER)

            #Print html report
            print 'Printing html report...'
            self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                              self.REPORT_TEMPLATE_PATH,
                              self._export(),
                              self._export_manual_report(),
                              output_path)

        else:
            print 'This run is a rerun process. Merging result...'
            array_auto_1 = genfromtxt('%s\%s' % (output_path, self.REPORT_AUTO_CSV_PATH), delimiter=self.REPORT_CSV_DELIMETER, dtype=str)
            array_auto_2 = self._export()
            
            for item in array_auto_2: array_auto_1[where((array_auto_1[:,0]==item[0]) & (array_auto_1[:,3]==item[3])), 1] = item[1]

            array_manual = genfromtxt('%s\%s' % (output_path, self.REPORT_MANUAL_CSV_PATH), delimiter=self.REPORT_CSV_DELIMETER, dtype=str)
            
            print 'Re-printing html report...'
            self._export_html('%s\%s' % (output_path, self.REPORT_HTML_PATH),
                              self.REPORT_TEMPLATE_PATH,
                              array_auto_1,
                              array_manual,
                              output_path)

        #Log notifications
        if os.path.isfile('%s\%s' % (output_path, self.REPORT_HTML_PATH)):
            print 'TestLink:%s\%s' % (output_path, self.REPORT_HTML_PATH)
        else:
            print 'Failed to build html report. An error occur!!!'

    def _export(self):
        iRpt = [self.iContent[0]._print().keys()]
        for elem in self.iContent: iRpt.append(elem._print().values())
        return array(iRpt)

    def _export_manual_report(self):
        try:
            iRpt = [self.iManualContent[0].keys()]
            tmpContent = [elem.values() for elem in self.iManualContent]
            for i, v in enumerate(tmpContent): iRpt.append(v)
            return array(iRpt)
        except Exception:
            return array([['testlink_id', 'testlink_name', 'status']])

    def _export_html(self, filepath, templatepath, nyreport, nymanual, output_path):
        '''
            Export to file html (for show report in Jenkins)
            filepath: path save file html\n
            templatepath: template of html file\n
            nyreport: report automation\n
            nymanual: report manual test\n
        '''
        
        project = self.PROJECT_NAME
        plan = self.TESTPLAN_NAME
        build = self.TESTBUILD_NAME
        runowner = self.OWNER_NAME
        
        # get build url from jenkins
        stringbuild = 'None'
        if os.path.isfile(output_path + '/../Build.txt'):
            stringbuild = _read_txt_to_string(output_path + '/../Build.txt').replace('%20',' ') + 'robot/report/log.html#'

        if self.IS_JENKIN_RUN is False:
            stringbuild = output_path + '/log.html#'
        
        # get template html
        reporthtml = _read_txt_to_string(templatepath)
        
        # info result status of all testcase
        try:
            num_rows = size(nyreport,0)
            numpass = count_nonzero(nyreport[:,1]=='PASS')
            numfail = count_nonzero(nyreport[:,1]=='FAIL')
            numskip = count_nonzero(nyreport[:,1]=='SKIP')
            try:
                numpassmanual = count_nonzero(nymanual[:,0]=='PASS')
                numfailmanual = count_nonzero(nymanual[:,0]=='FAIL')
                numnotrunmanual = count_nonzero(nymanual[:,0]=='NOT RUN')
            except Exception, err:
                numpassmanual = 0
                numfailmanual = 0
                numnotrunmanual = 0
                print 'Dont have manual testcase'
                
            per = '0' if numpassmanual == 0 else str(round(float(numpassmanual) / (numpassmanual + numfailmanual + numnotrunmanual) * 100))
            for r in (('${ac_count_pass}', str(numpass + numpassmanual)),('${ac_count_fail}', str(numfail + numfailmanual)), ('${ac_count_notrun}', str(numnotrunmanual)), ('${ac_runowner}', runowner), ('${ac_project}', project),
                      ('${ac_plan}', plan), ('${ac_plan_id}', self.TESTPLAN_ID), ('${ac_build}', build), ('${ac_link_build}', stringbuild), ('${ac_auto_percent}', str(round(float(numpass) / (numpass + numfail + numskip) * 100))), ('${ac_auto_pass}', str(numpass)), ('${ac_auto_fail}', str(numfail)), ('${ac_auto_skip}', str(numskip)),
                      ('${ac_manual_percent}', per), ('${ac_manual_pass}', str(numpassmanual)), ('${ac_manual_fail}', str(numfailmanual)), ('${ac_manual_notrun}', str(numnotrunmanual)),
                      ('${ac_status}', 'JOB SUCCESS') if numfail == 0 and numfailmanual == 0 else ('${ac_status}', 'JOB FAILURE'), ('${ac_color}', '#00A98F') if numfail == 0 and numfailmanual == 0 else ('${ac_color}', '#ff0000')):
                reporthtml = reporthtml.replace(*r)
            
            html_string=''''''
            i = 0
            string = ''    
            for item in nyreport:
                if item[0] == 'name_short': continue
                suite = item[7].replace('.' + item[0], '')
                if suite != string:
                    suite_string = '''<tr>
                                        <td class="suite" colspan='5'>'''+suite.replace(".", " >> ")+'''</td>
                                        </tr>'''
                    html_string = html_string + suite_string
                    string = suite

                ID, shortID, name, steps, fullpath, address = 'None', 'None', item[2], None, None, None
                status = item[1]
                duration = str(round((float(item[6])/(1000.00*60))%60, 2)) + ' m'
                if (item[3] not in (None, '')):
                    ID = item[3]
                    shortID = ID[len(self.PROJECT_PREFIX) + 1 - len(ID):]
                    steps = self.apiRef.getTC_Steps(ID)
                    address = self.apiRef.getTC_Testlink_Path(shortID, name)
                if status.lower() == 'skip':
                    if ID == 'None':
                        name = 'Unidetified ID from TestLink'
                    elif ID not in 'None':
                        iTC_Asignee = self.apiRef.getTC_Assigned(ID, self.TESTPLAN_ID, self.TESTBUILD_ID)
                        if iTC_Asignee is None:
                            name = '%s (Not included in TestPlan)' % name
                        elif iTC_Asignee[0]['login'] in ('', None):
                            name = '%s (Not assigned to anyone)' % name
                if steps not in ('<br/>', '', None):
                    name = '''<details><summary>''' + name + '''</summary><p><b>Steps:</b></br>''' + steps + '''</p></details>'''
                if address not in ('', None):
                    name = '''<div title="''' + address + '''">''' + name + '''</div>'''
                if status.lower() in ('pass','fail','skip'):
                    status = '''<a class="status-''' + status.lower() + '''" value="p" target="_blank" rel="noopener" href="''' + stringbuild + item[5]+'''">''' + item[1] + '''</a>'''
                
                table_string = '''<tr>''' +\
                        '''<td>''' + ID + '''</td>''' +\
                        '''<td>''' + name + '''</td>''' +\
                        '''<td>''' + item[0] + '''</td>''' +\
                        '''<td>''' + duration + '''</td>''' +\
                        '''<td>''' + status + '''</td>''' +\
                        '''</tr>'''
                html_string = html_string + table_string
                
            reporthtml = reporthtml.replace('${ac_list_testcase_auto}', html_string)
            html_string = ''''''
            flag = 0
        except Exception, err:
            traceback.print_exc()
            
        html_string=''''''
        try:
            numpassmanual = count_nonzero(nymanual[:,0]=='PASS')
            if nymanual.shape[0] > 1:
                reporthtml = reporthtml.replace('${ac_have_manual_list}', '')
                for tc in nymanual:
                    if tc[0] == 'status': continue
                    ID = tc[2]
                    shortID = ID[len(self.PROJECT_PREFIX)+1-len(ID):]
                    name = tc[1]
                    steps = self.apiRef.getTC_Steps(ID)
                    address = self.apiRef.getTC_Testlink_Path(shortID, name)
                    status = tc[0]
                    if steps not in ('<br/>', '', None):
                        name = '''<details><summary>''' + name + '''</summary><p><b>Steps:</b></br>''' + steps + '''</p></details>'''
                    if address not in ('', None):
                        name = '''<div title="''' + address + '''">''' + name + '''</div>'''
                    
                    note_string = '''<tr><td>''' + ID + '''</td>'''
                    note_string = note_string + '''<td>''' + name + '''</td>'''
                    if status == 'PASS': note_string = note_string + '''<td><p class="status-pass">PASS</p></td></tr>'''
                    elif status == 'FAIL': note_string = note_string + '''<td><p class="status-fail">FAIL</p></td></tr>'''
                    else: note_string = note_string + '''<td><p class="status-notrun">NOT RUN</p></td></tr>'''
                    html_string = html_string + note_string
        except IndexError:
            reporthtml = reporthtml.replace('${ac_have_manual_list}', 'None')
            print 'Dont have manual testcase'
        reporthtml = reporthtml.replace('${ac_list_testcase_manual}', html_string)
        reporthtml = re.sub('\xa0', '', reporthtml).encode('utf8','ignore')
        f = open(filepath,'w')
        f.write(reporthtml)
        f.close()
        
def _read_txt_to_string(path):
    filename = os.path.realpath(path)
    file = open(filename, 'r')
    return file.read()
  
def toCSV(filepath, source, delimeter):
    with open(filepath, 'wb') as of:
        writer = csv.writer(of, delimiter=delimeter)
        writer.writerows(source)
