import libs.curveLib.mvobject as mvobject
import libs.curveLib.segment
import logging
import importlib
import os
import glob

class curve(mvobject.mvobject):
    def __init__(self,  fname = None):
        #internal units
        #  sensitivity nm/V
        #  k pN/nm
        #  speed nm/s
        #  Z nm
        #  F pN
        defaults = {'fzfd':False,'k':1.0, 'relevant':True, 'sensitivity': 50.0}
        self.parseConfig(defaults,'Curve')
        
        self.savedSeg = 0
        
        self.filename = ''
        self.basename = ''
        self.segments=[]
        self.info={}

        if fname != None:
            self.filename = fname
            self.basename = os.path.basename(fname)
            self.open(fname)
        return
    def __iter__(self):
        return self.segments.__iter__()
    def __nonzero__(self):
        return self.relevant
    def __len__(self):
        return len(self.segments)
    def __getitem__(self, index):
        if index=='up':
            index = -1
        if index == 'down':
            index = 0
        return self.segments[index]
    def __delitem__(self,index):
        self.segments = self.segments[:index]+self.segments[-1:index:-1][::-1]

    def append(self,seg):
        if isinstance(seg,segment.segment):
            self.segments.append(seg)
        else:
            logging.error('You need to append a full instance of segment')
        
    def open(self,fname,driver=None):
        if not os.path.isfile(fname):
            logging.error("The file {0} does not exist".format(fname))
            return False

        #search for the specific driver
        import open_all as opa
        op = opa.opener(fname)
        try:
            parameters,info,segments=op.getOpener(driver)
        except:
            raise

        if len(segments)==0:
            logging.error("Empty File {0} not appended".format(fname))
            return False
            
        for k,v in parameters.items():
            setattr(self,k,v)
        self.info = info
        for s in segments:
            self.append(s)

    def save(self,fname=None,newly = False):
        """
        Save the curve in a TXT format compatible with the text export format of JPK IP and DP programs
        """
        if fname == None:
            return False
        
        out_file = open(str(fname),"w")
        out_file.write("# TEXT EXPORT\n")
        out_file.write("# springConstant: {0}\n".format(self.k))
        out_file.write("# units: m N\n")    
        if self.fzfd:
            out_file.write("# fzfd: 1\n")
        else:
            out_file.write("# fzfd: 0\n")
        out_file.write("#\n")  
        i=0
        for p in self.segments:
            if i != 0:
                out_file.write("\n")
            out_file.write("#\n")
            out_file.write("# segmentIndex: {0}\n".format(i))
            ts = 'extend'
            if p.direction == 'far':
                ts = 'retract'
            out_file.write("# segment: {0}\n".format(ts))
            out_file.write("# columns: distance force\n")
            out_file.write("# speed: {0}\n".format(p.speed))
            for i in range(len(p.z)):
                out_file.write("{0} {1}\n".format(p.z[i]*1e-9, -1.0*p.f[i]*1e-12))
            i+=1
        out_file.close()
        return True
    
    
    def appendToFile(self,p,fname=None,appendToCurve=True):
        
        path = self.filename if fname is None else fname
        out_file = open(str(path),"a")
        out_file.write("#\n")
        i = len(self)
        out_file.write("# segmentIndex: {0}\n".format(i))
        ts = 'extend'
        if p.direction == 'far':
            ts = 'retract'
        out_file.write("# segment: {0}\n".format(ts))
        out_file.write("# columns: distance force\n")
        out_file.write("# speed: {0}\n".format(p.speed))
        for i in range(len(p.z)):
            out_file.write("{0} {1}\n".format(p.z[i]*1e-9, -1.0*p.f[i]*1e-12))
        
        if appendToCurve:
            self.segments.append(p)

        out_file.close()
    
    
    def changeK(self,newK):
        
        for s in self.segments:
            s.f /= s.k
            s.f *= newK
            s.k = newK
        self.k = newK
        
    
    def changeSens(self,newSens):
        
        for s in self.segments:
            s.f /= self.sensitivity
            s.f *= newSens
        self.sensitivity = newSens
        
        
    def changeSpeed(self,newSpeed):
        
        for s in self.segments:
            s.speed = newSpeed
    
    
    def getMarkedPeaks(self, segInd, peakFinder = None, peakModel = None, argsPF = [], kwArgsPF = {}):
        
        amount = self.segments[segInd].getPeaks(peakFinder, peakModel, argsPF, kwArgsPF,id = self.filename)
        
        return amount
    
    def getPeaksStats(self,single = False, eStr = False):
        
        stats = '' if eStr else []
        
        for s in self.segments:
            if len(s.peaks)>=1:
                if single:
                    stats+=s.peaks.getSinglePeakStatsEntries(eStr,self.basename)
                else:
                    if eStr:
                        stats+=s.peaks.getStatsFileEntry(eStr,self.basename)
                    else:
                        stats.append(s.peaks.getStatsFileEntry(eStr,self.basename))
                
        return stats
    
    
    def anyPeaks(self):
        
        answer = 0
        for s in self.segments:
            answer += len(s.peaks)
        return answer
            
    
if __name__ == "__main__":
    print('not for direct use')
        