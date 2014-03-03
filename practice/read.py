import wfdb , sys
import pprint
import matplotlib.pyplot as plt
from matplotlib import interactive
from random import random
import numpy as np

#from practice.highpass_filter import HighpassFilter

interactive(True)

datasets = ["aami3a" , "aami3b" , "aami3c" , "aami3d" , "aami4a" , "aami4b"]

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
        
        qrs = QRSDetector()
        qrs_data = qrs.process(low_pass, len(low_pass))
        
        feature_extractor = FeatureExtractor()
        features = feature_extractor.get_RR_interval(sig0, qrs_data)
        
        #sig0 = qrs_dat
          
        
        wfdb.wfdbquit() 
        
        return sigt , sig0 , features
    
    
class QRSDetector(object):
    def __init__(self , *args , **kwargs):
        #self.M = float(30) # Window Size
        self.__dict__.update(kwargs)
    
    def process(self , lowpass , nsamp = None):
        if nsamp == None:
            nsamp = len(lowpass)
        
        QRS = [None for I in range(nsamp)]
        
        threshold = 0
        
        INIT_THRESHOLD = 200
        I = 0
        while (I < INIT_THRESHOLD):
            if lowpass[I] > threshold:
                threshold = lowpass[I]
            I  = I + 1
            pass
        
        FRAME = 250
        I = 0
        while(I < nsamp ):
            max_value = 0
            index = 0
            
            if (I + FRAME > nsamp ):
                index = nsamp
            else:
                index = I + FRAME
                
            J = I
            while ( J < index ):
                if ( lowpass[J] > max_value ):
                    max_value = lowpass[J]
                    pass
                J = J + 1
                pass
            
            
            added = False
            J = I
            while ( J < index ):
                if ((lowpass[J] > threshold) and (not added)):
                    QRS[J] =1
                    added = True
                    pass
                else:
                    QRS[J] = 0
                    
                J = J + 1
                pass
            
            if (random() > 0.5):
                gamma = 0.15
            else: 
                gamma =  0.20;
            
            alpha = 0.01 + (random() * ((0.1 - 0.01)))
            threshold = alpha * gamma * max_value + (1 - alpha) * threshold
            
            I  = I + FRAME
            pass
        
        return QRS
    
class FeatureExtractor(object):
    def __init__(self , *args , **kwargs):
        # Window Size
        self.__dict__.update(kwargs)
        
    def get_RR_interval(self , isig=None , qrs = None):
        if isig is None:
            isig  = self.isig
            
        if qrs is None:
            qrs = self.qrs
        
        intervals = []
        R_values = []
        
        nsamp = len(isig)
        
        I = 0
        while (I < nsamp):
            if qrs[I] == 1:
                """
                R value is detected
                """
                R1_value = isig[I]
                
                J = I + 1
                while ( (J < nsamp) and (qrs[J] != 1) ):
                    J = J + 1
                
                if (J== nsamp):
                    break
                elif (qrs[J] == 1):
                    R2_value = qrs[J] 
                    interval = J - I
                else:
                    R2_value = 0 # In case of Low pass 0 means Not applicable
                    interval = 0
                
                intervals.append(interval)
                R_values.append(R1_value)
                
            I = I + 1
        
        mean_interval = np.mean(intervals)
        avg_interval = sum(intervals)/float(len(intervals))
        
        mean_R_value = np.mean(R_values)
        avg_R_value  = sum(R_values)/float(len(R_values))
        
        print "Mean Interval: " + unicode(mean_interval)
        print "Mean Average Interval: " + unicode(avg_interval)
        
        print "Mean R Value: " + unicode(mean_R_value)
        print "Average R Value: " + unicode(avg_R_value)
        
        return  {
                    'mean_interval': mean_interval,
                    'avg_interval': avg_interval,
                    'mean_R_value': mean_R_value,
                    'avg_R_value': avg_R_value,
                 }

    def set_qrs(self , qrs):
        self.qrs = qrs
        
    def set_isig(self , isig):
        self.isig = isig  

class Stats(object):
    def __init__(self , *args , **kwargs):
        # Window Size
        self.__dict__.update(kwargs)
    
           
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

"""
We have 5 datasets. We analyze everyone and collect the stats
Then we publish each result in a graph with only mean values

Then in a graph for R values
"""
X_VALUES = []
Y_VALUES = []

I = 1
for dataset in datasets:
    reader = WFDBReader()
    xsigs , ysigs , features = reader.read(dataset)
    
    """
    {
                    'mean_interval': mean_interval,
                    'avg_interval': avg_interval,
                    'mean_R_value': mean_R_value,
                    'avg_R_value': avg_R_value,
                 }
    """
    X_VALUES.append(features.get('mean_R_value'))
    Y_VALUES.append(features.get('mean_interval'))
    
    I = I + 1

pprint.pprint(np.average(xsigs))
#xsigs , ysigs = range(20) , range(20)

print "Reading"
        
print "Reading Done"

plt.plot(X_VALUES , Y_VALUES)
raw_input('press return to end')