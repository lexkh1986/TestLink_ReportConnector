from TestReport import TestReport

def printHTML(TestReport_):
    if not TestReport_.isRerun:
        print 'No rerun found. Print report now:'
        print TestReport_.export()
    else:
        print 'Rerun found. Merge first'
        print 'Report the merged result'
        print TestReport_.export()

def test():
    print 'x'
