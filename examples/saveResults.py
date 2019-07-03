from AnimateSwipe import getSwipeResults
from voltage_search_tests import getRandomDn
from utils import parseArgs

def main():
    args = parseArgs()
    if "i" in args:
        startIndex = int(args["i"])
    else:
        startIndex = 0
    if "t" in args:
        times = int(args["t"])
    else:
        times = 20
    for index in range(startIndex, times):
        rel_path = "resultDump%d.kmc"%(index)
        dn = getRandomDn(30, 3)
        try:
            dn.loadSelf(rel_path, True)
        except:
            continue        
        getSwipeResults(dn, 40, 5000000, 40)
        dn.saveSelf(rel_path, True)
        

if __name__== "__main__":
    main()