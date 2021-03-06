import sys
sys.path.insert(0,'../')
import kmc_dopant_networks as kmc_dn
import numpy as np
import matplotlib.pyplot as plt
import cProfile
import time, random, json

# Used to print tables for Latex.

#%% Parameters

def printTable(headings, data):
    ptable = """\\begin{table}[h!]\n\\caption{Table caption}\n\\scalebox{0.7}{\n\\begin{center}\n\\begin{tabular}{ %s }\n\\hline\n"""%("|"+"c|"*len(headings))
    ptable+=headings[0]
    for i in range(1, len(headings)):
        ptable+="& %s"%(headings[i])
    ptable += "\\\\\n\\hline\n"
    for row in data:
        ptable+="%s"%(row[0])
        j = 1
        while j < len(row):
            ptable+=" & %s"%(row[j])
            j+=1
        ptable+="\\\\\n"
    
    ptable+="""\\hline\\end{tabular}\n\\end{center}\n}\\label{table:X}\n\\end{table}"""
    print (ptable)

def profile(N = 30, M=3, hops= 1100000, tests = 100):
    xdim = 1  # Length along x dimension
    ydim = 1  # Length along y dimension
    zdim = 0  # Length along z dimension
    #res = 1  # Resolution of laplace grid


    
    #%% Initialize simulation object

    for i in range(0, tests):
        # Define electrodes
        electrodes = np.zeros((8, 4))
        voltage_range = 600
        electrodes[0] = [0, ydim/4, 0, (random.random()-0.5)*voltage_range]
        electrodes[1] = [0, 3*ydim/4, 0, (random.random()-0.5)*voltage_range]
        electrodes[2] = [xdim, ydim/4, 0, (random.random()-0.5)*voltage_range]
        electrodes[3] = [xdim, 3*ydim/4, 0, (random.random()-0.5)*voltage_range]
        electrodes[4] = [xdim/4, 0, 0, (random.random()-0.5)*voltage_range]
        electrodes[5] = [3*xdim/4, 0, 0, (random.random()-0.5)*voltage_range]
        electrodes[6] = [xdim/4, ydim, 0, (random.random()-0.5)*voltage_range]
        electrodes[7] = [3*xdim/4, ydim, 0, 0]
        kmc = kmc_dn.kmc_dn(N, M, xdim, ydim, zdim, electrodes = electrodes)
        print ("i:%d\n"%(i))
        kmc.go_simulation(hops=hops,goSpecificFunction="wrapperSimulateRecord")

def compile(splits, hops):
    with open('reusing.log') as f:
        data = json.load(f)
        print (data)

        pdata = []
        keys = []
        key = 10
        i = 0
        while key < hops:
            ru_sum = [0]*len(splits)
            s_sum = [0]*len(splits)
            j = 0
            cur = 0
            for result in data:
                if j >= splits[cur][0]:
                    j = 0
                    cur+=1
                ru_sum[cur]+= result['Reuses'][i]
                s_sum[cur]+= result['States'][i]
                j+=1
            arr = [str(key)]
            for j in range(len(splits)):
                arr.append("%.1f"%(ru_sum[j]/splits[j][0]))
                arr.append("%.1f"%(s_sum[j]/splits[j][0]))
            pdata.append(arr)
            key*=10
            i+=1
        print (pdata)
        ptable = """\n\\begin{center}\n\\begin{tabular}{ %s }\n\\hline\nhops"""%("|c|"+"c|c|"*len(splits))
        for split in splits:
            ptable+=" & %s reuses & %s states"%(split[1], split[1])
        ptable += "\\\\\n\\hline\n"
        for row in pdata:
            ptable+="%s"%(row[0])
            j = 1
            while j < len(row):
                ptable+=" & %s & %s"%(row[j], row[j+1])
                j+=2
            ptable+="\\\\\n"
       
        ptable+="""\\hline\\end{tabular}\n\\end{center}\n"""
        print (ptable)

def main():
    # hops = 10000005
    # tests = 100
    # profile(10, 1, hops, tests)
    # profile(20, 2, hops, tests)
    # l = [20, 30, 60]
    # l2 = [2, 3, 6]
    # profile(l[0], l2[0], hops, tests)
    # profile(l[1], l2[1], hops, tests)
    # profile(l[2], l2[2], hops, tests)

    # compile([(tests, "%dD "%(l[0])), (tests, "%dD "%(l[1])), (tests, "%dD "%(l[2]))], hops)
    
    
    # headings = ["setup", "RND time", "XOR time", "RND $E_{DB}$", "RND $\sigma_{DB}$", "XOR $E_{DB}$", "XOR \sigma_{DB}"]
    # data = [
    #     ["Python 1E6 hops", "11881s", "12231s", 0.14, 0.16, 0.34, 1.4],
    #     ["Go 1E6 hops", "12394s", "13343s", 0.55, 4.6, 0.59, 2.1],
    #     ["Go recording 1E6 hops", "139s", "85s", 0.19, 0.65, 0.36, 1.1],
    #     ["Go recording 5E6 hops", "494s", "377s", 0.3, 0.26, 0.47, 1.1],
    #     ["Go pruning 1E6 hops 1E-5 threshold", "2879s", "2977s", 120, 770, 58, 230],
    #     ["Go pruning 1E6 hops 1E-7 threshold", "4291s", "4373s", 0.91, 8.5, 0.63, 2.3],
    #     ["Go pruning 1E6 hops 1E-9 threshold", "5898s", "6115s", 0.54, 3.6, 0.68, 3.3],
    #     ["Probability occupation 2K hops", "47s", "46s", "4.1E6", "1E8", "2.3E10", "4.7E11"],
    #     ["Probability occupation 5K hops", "114s", "118s", "4.3E7", "1.1E9", "3E8", "5.1E9"],
    #     ["Probability occupation 25K hops", "585s", "576s", "1.9E8", "5.1E9", "2.9E10", "5.9E11"],
    #     ["Probability occupation 100K hops", "2291s", "2319s", "8.2E6", "1.7E8", "4.6E10", "9.2E11"], 
    #     ]


    
    # headings = ["setup", "RND time", "XOR time", "RND $E_{DB}$", "RND $\sigma_{DB}$", "XOR $E_{DB}$", "XOR \sigma_{DB}"]
    # data = [
    #     ["Python 1E6 hops", "11929s", "12058s", 0.3, 0.4, 0.49, 1.2],
    #     ["Go 1E6 hops", "13176s", "14084s", 0.46, 4.3, 2.5, 44],
    #     ["Go recording 1E6 hops", "138s", "81s", 0.34, 0.73, 3.7, 53],
    #     ["Go recording 5E6 hops", "484s", "352s", 0.17, 0.19, 0.2, 0.67],
    #     ["Go pruning 1E6 hops 1E-5 threshold", "3668s", "3522s", 340, 2200, 290, 1300],
    #     ["Go pruning 1E6 hops 1E-7 threshold", "5077s", "5035s", 2, 25, 2.2, 24],
    #     ["Go pruning 1E6 hops 1E-9 threshold", "6651s", "6800s", 0.4, 1.5, 3.1, 62],
    #     ]
    
    # headings = ["setup", "successes", "failures"]
    # data = [
    #     ["U1000", 47, 53],
    #     ["M5", 38, 62],
    #     ["M30", 46, 54],
    #     ["U5kto1k", 41, 59],
    #     ]

    # headings = ["sample", "VC 4", "VC 5", "average absolute current VC 4", "average absolute current VC 5"]
    # data = [
    #     ["30 DOP, 1", "14/14", "28/30", "139.7nA", "123.9nA"],
    #     ["30 DOP, 2", "13/14", "29/30", "107.5nA", "85.4nA"],
    #     ["30 DOP, 3", "14/14", "25/30", "68.8nA", "59.7nA"],
    #     ["30 DOP, 4", "14/14", "30/30", "252.3nA", "210.2nA"],
    #     ["20 DOP, 1", "14/14", "29/30", "84.9nA", "130.7nA"],
    #     ["20 DOP, 2", "14/14", "30/30", "418.5nA", "498.6nA"],
    #     ["20 DOP, 3", "14/14", "30/30", "272.9nA", "28.5nA"],
    #     ["20 DOP, 4", "14/14", "30/30", "198.8nA", "155.5nA"],
    #     ["10 DOP, 1", "14/14", "28/30", "525.1nA", "488.8nA"],
    #     ["10 DOP, 2", "13/14", "30/30", "876.6nA", "823.0nA"],
    #     ["10 DOP, 3", "11/14", "30/30", "296.0nA", "520.6nA"],
    #     ["10 DOP, 4", "14/14", "26/30", "280.7nA", "275.8nA"],
    #     ]

    # headings = ["Number of dopants", "success rate", "average model current", "average supposed physical current"]
    # data = [
    #     ["5 DOP", "52/100", "0.00267", "2674.8nA"],
    #     ["10 DOP", "48/100", "0.000673", "673.4nA"],
    #     ["20 DOP", "42/100", "0.000219", "218.9nA"],
    #     ["30 DOP", "41/100", "7.75e-05", "77.5nA"],
    #     ["45 DOP", "22/100", "3.3e-05", "33.0nA"],
    #     ["60 DOP", "9/100", "1.49e-05", "14.9nA"],
    #     ]

    # headings = ["test", "average model current", "average supposed physical current"]
    # data = [
    #     ["30 DOP, 1", "0.000129", "129.5nA"],
    #     ["20 DOP, 1", "0.000222", "222.2nA"],
    #     ["10 DOP, 1", "0.000502", "502.1nA"],
    #     ["10 DOP, 2", "0.00134", "1339.4nA"],
    #     ["10 DOP, 3", "0.000323", "322.8nA"],
    #     ["10 DOP, 4", "0.000887", "886.8nA"],
    #     ]
    printTable(headings, data)

if __name__== "__main__":
  main()
