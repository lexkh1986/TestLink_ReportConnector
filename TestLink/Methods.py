from robot.libraries.BuiltIn import BuiltIn

class Methods(object):
    def log_step(self, step, expectation=None, logConsole=True, stepPrefix=False):
        '''
        Log a step to TestLink testcase\n
        Default expectation is blank (blank value will not be printed if useSummaryAsStep option is enabled\n
        Set logConsole to True for logged to console during run testcase\n
        Set stepPrefix to True to auto add prefix "Step:" and "Expectation:" before step content
        '''
        try:            
            iTC = BuiltIn().get_variable_value('${TESTLINK_iTC}')
            if expectation is None: expectation = ''
            if stepPrefix:
                step = 'Step: %s' % step
                expectation = 'Expectation: %s' % expectation
            if logConsole:
                txtMsg = step
                if expectation != '': txtMsg = 'Step: %s\nVP: %s' % (step, expectation) 
                BuiltIn().log_to_console(txtMsg)
            iTC.setSteps(step, expectation)
        except Exception, err:
            pass

    def register_testlink_id(self, *testlink_id):
        '''
        Register this testcase name with one or more testlink id\n
        Note: If 1-1 link setting method is selected. Only the first id param will be used\n
        '''
        try:            
            if testlink_id:
                iTC = BuiltIn().get_variable_value('${TESTLINK_iTC}')
                iTC.testlink_id = testlink_id[0].strip()

                tcName = BuiltIn().get_variable_value('${TEST_NAME}')
                BuiltIn().set_suite_metadata(tcName, testlink_id[0].strip())
        except Exception, err:
            pass
