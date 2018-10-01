from robot.libraries.BuiltIn import BuiltIn

class Methods(object):
    def log_step(self, step, expectation=None, logConsole=False, stepPrefix=False):
        '''
        Log a step to TestLink testcase\n
        Default expectation is blank (blank value will not be printed if useSummaryAsStep option is enabled\n
        Set logConsole to True for logged to console during run testcase\n
        Set stepPrefix to True to auto add prefix "Step:" and "Expectation:" before step content
        '''
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
