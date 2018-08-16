from TestReport import TestReport, TestCase

class HTMLParser:

    @staticmethod
    def printHTML(TestReport_):
        if TestReport_.isRerun:
            print 'No rerun found. Print report now:'
            print TestReport_.export()
        else:
            print 'Rerun found. Merge first'
            print 'Report the merged result'
            print TestReport_.export()
