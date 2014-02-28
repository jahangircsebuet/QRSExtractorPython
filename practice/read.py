import wfdb , sys
import pprint
import matplotlib.pyplot as plt
from matplotlib import interactive
#from practice.highpass_filter import HighpassFilter

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
        
        
        #Getting X Axes Interval
        #Appending data to array
        X_INTERVAL = 20
        pause = 0
        for i in range(siarray.cast().nsamp):
            if ( wfdb.getvec(v.cast()) < 0 ):
                break
            sig0.append(v.__getitem__(0))
            sigt.append(pause)
            pause = pause + X_INTERVAL
            pass
        
        #High Pass Filtering
        highpass_filter = HighpassFilter()
        high_pass = highpass_filter.process(sig0,siarray.cast().nsamp)
        #Low pass Filtering
        lowpass_filter = LowpassFilter()
        low_pass = lowpass_filter.process(high_pass, len(high_pass))
        
        sig0 = low_pass
          
        
        wfdb.wfdbquit() 
        
        return sigt , sig0
    
class QRSDetector(object):
    def __init__(self , *args , **kwargs):
        #self.M = float(30) # Window Size
        self.__dict__.update(kwargs)
    
    def process(self , lowpass , nsamp = None):
        if nsamp == None:
            nsamp = len(lowpass)
        
        threshold = 0
        
    
class LowpassFilter(object):
    def __init__(self , *args , **kwargs):
        self.M = float(30) # Window Size
        self.__dict__.update(kwargs)
        
    def process(self , sig0 , nsamp = None):
        if nsamp == None:
            nsamp = len(sig0)
        
        low_pass = [0 for i in range(nsamp)]
            
        for i in range(nsamp):
            sum = float(0)
            M = self.M
            
            if( (i + M) < nsamp ):
                j = i
                while(j < (i + M)):
                    current = sig0[j] * sig0[j]
                    sum = sum +  current
                    
                    j = j + 1
                    pass
                pass
            elif( (i + M) >= nsamp ):
                over = i+ M - nsamp
                j = i
                while( j < nsamp):
                    current = sig0[j] * sig0[j]
                    sum  = sum + current
                    j = j + 1
                    pass
                
                j = 0
                while(j < over):
                    current = sig0[j] * sig0[j]
                    sum = sum + current
                    j = j + 1
                    pass
                pass
            
            low_pass[i] = sum
            pass
        
        return low_pass
        

class HighpassFilter(object):

    def __init__(self , *args , **kwargs):
        '''
        Constructor
        '''
        self.M = float(5) # Window Size
        self.__dict__.update(kwargs)
    
    def process(self , sig0 , nsamp):
        low_pass = [0 for i in range(len(sig0))]
        M = self.M
        constant = float(1/M)  
        
        for i in range(len(sig0)):
            y1 = 0
            y2 = 0
            
            y2_index = int(i-((self.M+1)/2))
            if y2_index < 0:
                y2_index = nsamp + y2_index
            y2 = sig0[y2_index] 
            
            y1_sum = 0
            j = i
            while (j > (i - M)):
                x_index = i- (i-j);
                if (x_index < 0):
                    x_index = nsamp + x_index
                    
                y1_sum = y1_sum + sig0[x_index]
                
                j = j-1
            
            y1 = constant * y1_sum
            low_pass[i] = y2 - y1
        
        return low_pass
    

reader = WFDBReader()

xsigs , ysigs = reader.read('aami3b')
 
import numpy as np

pprint.pprint(np.average(xsigs))
#xsigs , ysigs = range(20) , range(20)

print "Reading"
        
print "Reading Done"

plt.plot(xsigs , ysigs)
raw_input('press return to end')