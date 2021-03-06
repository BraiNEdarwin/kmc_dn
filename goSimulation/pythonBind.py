from ctypes import *
from numpy import float64
import numpy as np
import time as time_lib

def flattenDouble(arr2):
    d = len(arr2[0])
    arr = []
    for row in arr2:
        if len(row) != d:
            raise Exception("array dimensions not uniform!")
        for ele in row:
            arr.append(c_double(float64(ele).item()))
        
    return (c_double * len(arr))(*arr), d, len(arr)

def getGoSlice(arr, log=False):
    rArr = []
    for ele in arr:
        rArr.append(c_double(ele))
        if log:
            print("ele pointer: %s"%(str(rArr[-1].__repr__)))
    if log:
        print("arr pointer: %s"%(str(rArr.__repr__)))
    return GoSlice((c_double * len(rArr))(*rArr), len(rArr), len(rArr))


class GoSlice(Structure):
    _fields_ = [("data", POINTER(c_double)),
                ("len", c_longlong), ("cap", c_longlong)]
                

def getSliceValues(slice, log=False):
    r = []
    for i in range(slice.len):
        r.append(slice.data[i])
    return r

def getDeflattenedSliceValues(slice, d1, d2):
    r = []
    count = 0
    for i in range(d1):
        r.append([])
        for j in range(d2):
            r[i].append(slice.data[count])
            count+=1
    return r

def callGoSimulation(N_acceptors, N_electrodes, nu, kT, I_0, R, time, occupation, 
		distances , E_constant, site_energies, transitions_constant, transitions, 
        problist, electrode_occupation, hops, record, goSpecificFunction, prune_threshold=0.0):
    newDistances, d, s = flattenDouble(distances)
    N = N_acceptors + N_electrodes
    newTransConstants, _, tcs = flattenDouble(transitions_constant)
    #print ("d is %d and s is %d"%(d, s))
    newDistances = GoSlice(newDistances, s, s)
    newTransConstants = GoSlice(newTransConstants, tcs, tcs)
    newOccupation = getGoSlice(occupation)
    newE_constant = getGoSlice(E_constant)
    newSite_energies = getGoSlice(site_energies)
    traffic = getGoSlice(np.zeros(N*N))
    average_occupation = getGoSlice(np.zeros(N_acceptors))
    newElectrode_occupation = getGoSlice(electrode_occupation)
    lib = cdll.LoadLibrary("./goSimulation/libSimulation.so")
    getattr(lib, goSpecificFunction).argtypes = [c_longlong, c_longlong, c_double, c_double, c_double, c_double, c_double,
        GoSlice, GoSlice, GoSlice, GoSlice, GoSlice, GoSlice, c_int, c_bool, GoSlice, GoSlice]

    getattr(lib, goSpecificFunction).restype = c_double
    #printSlice(newElectrode_occupation)
    args = [N_acceptors, N_electrodes, nu, kT, I_0, R, time, newOccupation, 
		newDistances , newE_constant, newTransConstants, newElectrode_occupation, 
        newSite_energies, hops, record, traffic, average_occupation]
    if goSpecificFunction == "wrapperSimulatePruned":
        getattr(lib, goSpecificFunction).argtypes = [c_longlong, c_longlong, c_double, c_double, c_double, c_double, c_double, c_double,
            GoSlice, GoSlice, GoSlice, GoSlice, GoSlice, GoSlice, c_int, c_bool, GoSlice, GoSlice]

        args = [N_acceptors, N_electrodes, prune_threshold, nu, kT, I_0, R, time, newOccupation, 
		    newDistances , newE_constant, newTransConstants, newElectrode_occupation, 
            newSite_energies, hops, record, traffic, average_occupation]

    time = getattr(lib, goSpecificFunction)(*args)
    #printSlice (newElectrode_occupation)
    rElectrode_occupation = np.array([int(i) for i in getSliceValues(newElectrode_occupation)])
    occupation = np.array([int(i) for i in getSliceValues(newOccupation)])
    #print (rElectrode_occupation)

    if not record:
        return (time, occupation, rElectrode_occupation)
    else:
        return time, occupation, rElectrode_occupation, np.array(getDeflattenedSliceValues(traffic, N, N)), np.array(getSliceValues(average_occupation))


