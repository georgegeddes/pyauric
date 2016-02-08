import fortranformat as ff 
import numpy as np 
import pandas as pd

class _dummy_reader( object ):
    def __init__(self):
        pass

    def read(self, s):
        return [s.strip()]

class auric_file_reader( object ):
    def __init__(self,
        headingformat='A',
        indexformat='6F12.2',
        dataformat='6E12.3'):
        self.heading_reader = _dummy_reader()
        self.index_reader = ff.FortranRecordReader(indexformat)
        self.data_reader = ff.FortranRecordReader(dataformat)

    def read(self, filename, returnDataFrame=True):
        with open(filename) as f:
            lines = f.readlines()

        hr = self.heading_reader
        ir = self.index_reader
        dr = self.data_reader

        # store all the lines in info
        info = [line.strip('\n') for line in lines]

        data = {}
        data_list = []
        index_mode = False
        name = ""
        # now read from the bottom up
        while not index_mode:
            line = info.pop()
            try:
                # try to interpret the line as data
                data_line = dr.read(line)
                # remove None's
                data_line = [x for x in data_line if x is not None]
                # build a list of lists
                data_list.append(data_line)
            except ValueError:
                header = hr.read(line)[0]
                if data_list==[]:
                    #two headers in a row means we have hit the top of the data section
                    name = header[:]
                    index_mode = True
                    continue
                # the lines are stored in reversed order, so reverse the list
                data_array =  np.hstack( data_list[::-1] )
                data[header] = data_array
                data_list = []

        index = {}
        header = ''
        data_list = []
        while not header:
            line = info.pop()
            try:
                # try to interpret the line as index data
                data_line = ir.read(line)
                # remove None's
                data_line = [x for x in data_line if x is not None]
                # build a list of lists
                data_list.append(data_line)
            except ValueError:
                header = hr.read(line)[0]
                # the lines are stored in reversed order, so reverse the list
                data_array =  np.hstack( data_list[::-1] )
                index[header] = data_array

        if returnDataFrame:
            idx = pd.Index(index.values()[0],name=index.keys()[0])
            df = pd.DataFrame(data,index=idx)
            df.ylabel = name
            df.filename = filename
            df.title = "Data from {}".format(filename.split('/')[-1])
            df.extra_info = info
            return df
        else:
            return { 'info':info, 'index':index, 'data':data }


