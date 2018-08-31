from robot.libraries.BuiltIn import BuiltIn

class Methods(object):
    def log_step(self, step, expectation):
        iTC = BuiltIn().get_variable_value('${TESTLINK_iTC}')
        iTC.setSteps(step, expectation)
        
