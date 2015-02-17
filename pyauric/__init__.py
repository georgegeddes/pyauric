import os, subprocess, threading, re, traceback
import numpy as np

class AURICManager( object ):
    """Keep track of the directory where you want to run AURIC."""
    auricroot = str(os.getenv("AURIC_ROOT"))
    def __init__( self, path=auricroot ):
        assert os.path.isdir(path), "Invalid AURIC path, '{}'".format( path )
        self.path = os.path.abspath( path )
        self.batchfile = os.path.join( path, "onerun.sh" )
        self.batch_command = Command( ["bash", self.batchfile] )
        #^ add some logic to see if auric needs to be setup

    def runbatch( self, timeout=10 ):
        """Execute batch file."""
        ret = self.batch_command.run( timeout )
        return ret

    def customrun( self, commands, timeout=10 ):
        commands = map(Command, commands)
        for cmd in commands:
            cmd.run(timeout)

    def retrieve( self, filename, 
        features=['O+e 832 A (initial)','O+e 833 A (initial)','O+e 834 A (initial)',
        'O+hv 832 A (initial)','O+hv 833 A (initial)','O+hv 834 A (initial)'] ):
        """Retrieve desired features from file 'filename'."""
        data = read_auric_file( self.pathto( filename ) )
        out={}
        out["ALT"] = np.asarray(data["ALT"])
        out["ZA"] = np.asarray(data["ZA"])
        for feature in features:
            out[feature] = np.asarray(data["profiles"][feature])
        return out

    def read( self, fname ):
        """Parse data from an auric input or output file."""
        fpath = self.pathto( fname )
        out=None
        try:
            if fname == 'view.inp':
                out = read_view( fpath )
            elif fname == 'radtrans.opt':
                out = read_radtrans_options( fpath )
            else:
                out = read_auric_file( fpath )
        except Exception, err:
            traceback.print_exc()
            print "pyauric doesn't recognize this type of file."
        finally:
            return out

    def write( self, fname, ftype=None, **kwargs ):
        fpath = self.pathto( fname )
        if fname == "view.inp" or ftype == "view":
            write_view( filename=fpath, **kwargs )
        elif fname == "radtrans.opt" or ftype == "radtrans":
            write_radtrans_options( filename=fpath, **kwargs )
        else:
            raise Exception("pyauric doesn't know how to write that kind of file yet.")

    def pathto( self, fname ):
        """Absolute path to file 'fname' in the auric directory."""
        return os.path.abspath( os.path.join( self.path, fname ) )

class Command(object):
      #http://stackoverflow.com/questions/1191374/subprocess-with-timeout?lq=1
      def __init__(self, cmd):
            self.cmd  = cmd
            self.process = None
            
      def run(self, timeout):
            def target():
                  print 'Thread started'
                  print( "".join( self.cmd ) )
                  #   self.process = subprocess.Popen(self.cmd,stderr=subprocess.STDOUT, stdout=subprocess.PIPE)#, shell=True)
                  self.process = subprocess.check_call( self.cmd )#, shell=True)
                  #self.process.communicate()
                  print 'Thread finished'
                  
            thread = threading.Thread( target=target )
            thread.start()
            
            thread.join(timeout)
            if thread.is_alive():
                  print 'Terminating process'
                  self.process.terminate()
                  thread.join()
                  print self.process.returncode        

def read_auric_file( filename ):
    """Reads a file from AURIC and returns a dictionary of the file's contents.
    
    All data for the line named ### are returned in out['profiles']['###']."""
    with open(filename,'r') as f:
        lines=f.readlines()
    heading = None
    out = {}
    out["ZA"]=[]
    out["ALT"]=[]
    out["profiles"]={}
    pattern="This probably won't match anything, right?"
    data = []
    # headings are not consistent across all auric files T.T
    if re.search("observer altitude \(km\)",lines[0]):
        out['ZOBS'] = re.search(".[0-9]+\.[0-9]+",lines[0]).group(0)
        heading="Zenith Angles (deg)"
    for i, line in enumerate(lines[1:]): # skip the first line, because it just describes the size of the data.
        if re.search("\A[^ ]",line):
            heading = re.search("[^\=]*",line).group(0).strip() # match all non-equals signs
        if "ZOBS" == heading:
            m = re.search("(?<=ZOBS \= )[0-9]{3}\.[0-9]{3}",line) # match ###.### after 'ZOBS = '
            if m: 
                out['ZOBS']=float(m.group(0))
                continue
        elif "Zenith Angles (deg)" in heading:
            pattern = "([ ]*[0-9]*\.[0-9]*[ ]*)*" # match decimal numbers separated by whitespace
            data = out["ZA"]
        elif "Altitudes (km)" in heading:
            pattern = "([ ]*[0-9]*\.[0-9]*[ ]*)*" # match decimal numbers separated by whitespace
            data = out["ALT"]
        elif re.search("\A[A-Z][a-z][a-z]+",heading):
            out['type'] = heading
        elif re.search("\A[0-9]{3,4} A|\A[A-Z.*[0-9].*|\A\[",heading): # match a wavelength, transition name, or initial bracket
            if heading not in out["profiles"]: 
                out["profiles"][heading] = []
                continue
            pattern = "([ ]*[0-9]\.[0-9]{3}E(\+|-)[0-9]{2}[ ]*)*" # match floats in sci. notation
            data = out["profiles"][heading]
 
        m = re.search(pattern,line)
        if m:
            data.extend([float(n) for n in m.group(0).split()])
    return out

def read_view(filename="view.inp"):
    """Read view.inp, which has a weird format."""
    with open(filename,'r') as f:
        lines=f.readlines()
    h = float(lines[0].split()[0].strip())
    za=[float(line.strip()) for line in lines[1:]]
    return h, np.asarray( za )

def write_view(filename="view.inp", h=0, za=[0] ):
    with open(filename,'w') as f:
        f.write("{: 11.4f}   observer altitude (km)\n".format(h))
        for i in za:
            f.write("{: 12.5f}\n".format(i))

def read_radtrans_options(filename='radtrans.opt'):
    """Takes the name of a radtrans option file and returns a dictionary of the options."""
    with open(filename,'r') as f:
        lines = f.readlines()
    options={}
    for line in lines:
        m = re.search("([0-9]{3,4}) *\= (ON|OFF)",line) # match a 3-4 digit number followed by ' = ON' or ' = OFF'
        if m:
            options[m.group(1)]=m.group(2)
    return options

def write_radtrans_options( filename='radtrans.opt', options={} ):
    """Takes a dictionary of options and a filename and writes a radtrans options file for use with AURIC."""
    keylist=['832', '833', '834', '1304', '1356', '1040', '1026', '989', '1048', '1066', '1135', '1199']
    for key in keylist:
        if key not in options.keys():
            options[key] = "OFF" #set any missing keys to OFF
    with open(filename,'w') as f:
        f.write("Options for code RADTRANS:\n")
        f.write("-------------------------------------------------------\n")
        for key in keylist:
            s=" "*9+"{:4s} = {}\n".format(key,options[key])
            f.write(s)
        f.write("-------------------------------------------------------\n")
