import wfdb , sys
import pprint
import matplotlib.pyplot as plt
from matplotlib import interactive
interactive(True)

class WFDBReader(object):
    
    def __init__(self , *args , **kwargs):
        self.record = None
        self.__dict__.update(kwargs)
    
    def read(self , record = None):
        if record == None:
            if self.record == None:
                sys.exit(1)
            else:
                record = self.record
        else:
            self.record = record
            
        sig0 = []
        sigt = []
        
        siarray = wfdb.WFDB_SiginfoArray(2)
        
        if (wfdb.isigopen(record , siarray.cast() , 2) < 1):
            sys.exit(1)
        
        v = wfdb.WFDB_SampleArray(2)
        
        X_INTERVAL = 20
        pause = 0
        for i in range(siarray.cast().nsamp):
            if ( wfdb.getvec(v.cast()) < 0 ):
                break
            sig0.append(v.__getitem__(0))
            sigt.append(pause)
            pause = pause + X_INTERVAL
            pass
        
        wfdb.wfdbquit()
        
        return sigt , sig0
    

reader = WFDBReader()

xsigs , ysigs = reader.read('aami3b')
 
import numpy as np

pprint.pprint(np.average(xsigs))
#xsigs , ysigs = range(20) , range(20)

print "Reading"
        
print "Reading Done"

plt.plot(xsigs , ysigs)
raw_input('press return to end')