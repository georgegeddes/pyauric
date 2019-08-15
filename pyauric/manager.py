import os, re, traceback
import numpy as np
from .reader import auric_file_reader
from .command import Command, InputCommand
from .switch import Switch
from .batch import assemble_batch_run
from .bands import _bands
from collections import OrderedDict, ChainMap

_AURIC_ROOT = os.getenv("AURIC_ROOT")
if _AURIC_ROOT is None:
    _AURIC_ROOT=os.path.join(os.getenv("HOME"),"auric")
_AURIC_BIN_DIR=os.path.join(_AURIC_ROOT,"bin",os.uname().sysname)

_band_options_default = { k:False for k in _bands }
                            
class AURICManager( object ):
    """Keep track of the directory where you want to run AURIC.
    
    The band options may be passed as a dictionary or as keywords.
    Keyword settings will override the same settings passed in a dictionary.

    Parameters
    ----------
    path: [ $AURIC_ROOT | string ]
        Directory to use as the auric root

    band_options: dictionary
        Dictionary of synthetic spectrum options. Default is all False
    use_eflux: bool, optional
        Whether to use eflux vs peflux
    n2_lbh: bool, optional
        N2 Lyman-Birge-Hopfield (LBH)
    n2_vk: bool, optional
        N2 Vegard Kaplan (VK)
    n2_1pg: bool, optional
        N2 First Positive (1PG)
    n2_2pg: bool, optional
        N2 2nd Positive (2PG)
    n2p_1ng: bool, optional
        N2+ 1st Negative (1NG)
    n2p_mnl: bool, optional
        N2+ Meinel
    no_bands: bool, optional
        NO Bands (Gamma, Delta, Epsilon)

    Attributes
    ----------
    TODO
    """
    def __init__( self, path=_AURIC_ROOT,
                  band_options=_band_options_default,
                  use_eflux = False,
                  **band_kwds):
        assert os.path.isdir(path), "Invalid AURIC path, '{}'".format( path )
        self.path = os.path.abspath( path )
        self.env = { "AURIC_ROOT":_AURIC_ROOT,
                     "PATH":":".join([_AURIC_BIN_DIR,
                                        os.getenv("PATH")])
        }
        self.batchfile = os.path.join( path, "onerun.sh" )
        self.batch_command = self.new_command( ["bash", self.batchfile] )
        self._reader = auric_file_reader()
        self.band_options = band_options
        self.use_eflux = use_eflux
        for k,v in band_kwds.items():
            self.band_options[k] = v

    def new_command(self,cmd):
        """Create a process for an auric command with the proper environment."""
        return Command(cmd,env=self.env,cwd=self.path)

    def runbatch( self, timeout=10 ):
        """Execute batch file."""
        #self.batch_command.run( timeout )
        for cmd in self.batch:
            cmd.run()
        #return "running onerun.sh"

    def customrun( self, commands, timeout=10 ):
        commands = map(self.new_command, commands)
        for cmd in commands:
            cmd.run(timeout)
        return "running {}".format(" ".join( [ c.cmd for c in commands ] ) )

    def run_geoparm(self,compute_F107_and_Ap):
        """The command `geoparm` derives the geomagnetic coordinates, solar zenith angle, and solar local time from the mandatory parameters. It requires user input to specify whether F10.7 and Ap should be computed or left alone.

        Parameters
        ----------
        compute_F107_and_Ap: bool
            Whether to compute F10.7 and Ap index.
        
        Returns
        -------
        out: int
            return code of geoparm
        """
        input_string = b'Y\n' if compute_F107_and_Ap else b'N\n'
        geoparm = InputCommand(cmd='geoparm',env=self.env,cwd=self.path)
        out = geoparm.run(input_string)
        return out
    
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
        except Exception as err:
            traceback.print_exc()
            print("pyauric doesn't recognize this type of file.")
        finally:
            return out

    def write( self, fname, ftype=None, options={}, **kwargs ):
        fpath = self.pathto( fname )
        if fname == "view.inp" or ftype == "view":
            h, za = self.view
            viewdict = ChainMap(options, {'ZOBS': h, 'ZA': za})
            h, za = viewdict["ZOBS"], viewdict["ZA"]
            write_view( filename=fpath, h=h, za=za )
        elif fname == "radtrans.opt" or ftype == "radtrans":
            write_radtrans_options( filename=fpath, options=options, **kwargs )
        else:
            raise Exception("pyauric doesn't know how to write that kind of file yet.")

    def pathto( self, fname ):
        """Absolute path to file 'fname' in the auric directory."""
        return os.path.abspath( os.path.join( self.path, fname ) )

    def set_params( self, paramdict ):
        """Change the values in param.inp using a dictionary."""
        filename = self.pathto('param.inp')
        update_params( filename, paramdict )
        return paramdict

    def load(self, filename,**kwargs):
        """Load data from `filename`. Default behavior returns a pandas data frame. Pass returnDataFrame=False to get a dictionary instead."""
        df = self._reader.read(os.path.join(self.path,filename),**kwargs)
        return df

    def exists(self,fname):
        return os.path.isfile(self.pathto(fname))
    
    @property
    def radtrans_options( self ):
        return self.read('radtrans.opt')
    
    @property
    def view( self ):
        return self.read( 'view.inp' )
    
    @property
    def params( self ):
        p = [x for x in parse_params( self.pathto( 'param.inp' ) ) if len(x)>1]
        return {x[0]:x[1] for x in p}
        #return parse_params( self.pathto( 'param.inp' ) )

    @property
    def batch(self):
        return list(assemble_batch_run(self))

def read_auric_file( filename ):
    """Reads a file from AURIC and returns a dictionary of the file's contents.
    
    All data for the line named ### are returned in out['profiles']['###']."""
    with open(filename,'r') as f:
        lines=f.readlines()
    heading = None
    out = OrderedDict()
    out["ZA"] = []
    out["ALT"] = []
    out["profiles"] = OrderedDict()
    # https://stackoverflow.com/questions/940822/regular-expression-syntax-for-match-nothing
    pattern = r"(?!)"           # Matches nothing (not even the empty string)
    data = []
    # headings are not consistent across all auric files T.T
    if re.search(r"observer altitude \(km\)", lines[0]):
        out['ZOBS'] = re.search(r".[0-9]+\.[0-9]+", lines[0]).group(0)
        heading = "Zenith Angles (deg)"
    for i, line in enumerate(lines[1:]): # skip the first line, because it just describes the size of the data.
        if re.search(r"\A[^ ]",line):
            heading = re.search(r"[^\=]*",line).group(0).strip() # match all non-equals signs
        if "ZOBS" == heading:
            m = re.search(r"(?<=ZOBS \= )[0-9]{3}\.[0-9]{3}",line) # match ###.### after 'ZOBS = '
            if m: 
                out['ZOBS']=float(m.group(0))
                continue
        elif "Zenith Angles (deg)" in heading:
            pattern = r"([ ]*[0-9]*\.[0-9]*[ ]*)*" # match decimal numbers separated by whitespace
            data = out["ZA"]
        elif "Altitudes (km)" in heading:
            pattern = r"([ ]*[0-9]*\.[0-9]*[ ]*)*" # match decimal numbers separated by whitespace
            data = out["ALT"]
        elif re.search(r"\A[A-Z][a-z][a-z]+",heading):
            out['type'] = heading
        elif re.search(r"\A[0-9]{3,4} A|\A[A-Z.*[0-9].*|\A\[",heading): # match a wavelength, transition name, or initial bracket
            if heading not in out["profiles"]: 
                out["profiles"][heading] = []
                continue
            pattern = r"([ ]*[0-9]\.[0-9]{3}E(\+|-)[0-9]{2}[ ]*)*" # match floats in sci. notation
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
        m = re.search(r"([0-9]{3,4}) *\= (ON|OFF)",line) # match a 3-4 digit number followed by ' = ON' or ' = OFF'
        if m:
            options[m.group(1)]=Switch(m.group(2))
    return options

def write_radtrans_options( filename='radtrans.opt', options={} ):
    """Takes a dictionary of options and a filename and writes a radtrans options file for use with AURIC."""
    keylist=['832', '833', '834', '1304', '1356', '1040', '1026', '989', '1048', '1066', '1135', '1199']
    for key in keylist:
        if key not in options.keys():
            options[key] = Switch("OFF") #set any missing keys to OFF
    with open(filename,'w') as f:
        f.write("Options for code RADTRANS:\n")
        f.write("-------------------------------------------------------\n")
        for key in keylist:
            s=" "*9+"{:4s} = {}\n".format(key,Switch(options[key]))
            f.write(s)
        f.write("-------------------------------------------------------\n")

def update_params( filename, paramdict ):
    data = parse_params( filename )
    modify_params( data, paramdict )
    write_params( filename, data)
    return data

def parse_params( filename ):
    """Reads AURIC's param.inp file and returns a list containing the unformatted data one each line."""
    with open( filename, 'r' ) as f:
        lines=f.readlines()        
    parsed_lines=[]
    for i, line in enumerate(lines):
        if re.search(r":$",line): 
            parsed_lines.append(line) 
            continue
        x = re.search(r'.*(?==)',line)                         # Everything before =
        y = re.search(r'(?<==)*[0-9 -]*?\.*[0-9 ]*(?=:)',line) # Number between = and :
        z = re.search(r'(?<=:).*',line)                        # Anything after :
        key = x.group(0).strip()
        value = float( y.group(0).strip() )
        desc = z.group(0).strip()
        parsed_lines.append( [ key, value, desc ] )
    return parsed_lines

def modify_params( parsed_lines, paramdict ):
    """Takes a list of parsed lines from parse_params and makes the changes specified in paramdict."""
    for line in parsed_lines: # Replace values to be modified
        if line[0] in paramdict.keys():
            line[1] = paramdict[line[0]]

def write_params( filename, parsed_lines ):
    """Writes a set of lines parsed by parse_params to *filename*."""
    intkeys = ['NALT', 'YYDDD'] 
    lines=[None]*32
    for i, line in enumerate(parsed_lines):
        if isinstance(parsed_lines[i], str):
            lines[i]=parsed_lines[i]
        elif parsed_lines[i][0] in intkeys:
            lines[i] = "{: >12s} = {: >10.0f} : {:<s}\n".format(*parsed_lines[i])
        elif parsed_lines[i][1] == -1:
            lines[i] = "{: >12s} = {: >10.0f} : {:<s}\n".format(*parsed_lines[i])
        else:
            lines[i] = "{: >12s} = {: >10.2f} : {:<s}\n".format(*parsed_lines[i])
    with open( filename, 'w' ) as f:
        for line in lines:
            f.write(line)
