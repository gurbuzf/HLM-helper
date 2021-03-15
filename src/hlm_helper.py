#-----------------------------------------------------#
# Author: Faruk Gurbuz
# Date: 03/15/2021
#-----------------------------------------------------#

from string import Template
import os
from secrets import choice
import string
from datetime import datetime as dt

class GlobalFileCreator:
    ''' 
    Creates global file for HLM
        Parameters:
            args:dict, includes key, item pairs used to create gbl file. Items are in string format.
                keys: ['begin' 'end' 'Parameters' 'rvr_path' 'prm_path' 'initialCond_path' 'rainfall_path' 'evap_path' 
                    'output_path' 'sav_path' 'scratch_path','dam_path', 'snapshot_path']
                if rain_type is 2 or 5, add 'chunk_size', 'time_resolution', 'bin_unix1', 'bin_unix2' in args.

            model_type:int, 190 or 254
            rain_type:int, if binary (2) or forecasting (i.e.irregular binary) (5) is used, 
                    provide this information. otherwise an error will be raised.
            out_resolution: the output hydriograph time resolution (min)
            sav_type:int, if 3, the hydrographs for all links will be saved.
                        In that case, no need to add sav_path in args.
            component2print:list, a list of strings including the states to be printed.
                        default: ['Time', 'LinkID', 'State0'] 

        NOTE: All path variables, except scratch_path, must include relevant extension.
              'begin' and 'end' must be unix_time
              For model_type=190: Parameter order [v_r  lambda_1  lambda_2  RC    v_h  v_g]
              For model_type=254: Parameter order [v_0 lambda_1 lambda_2 v_h  k_3       k_I_factor h_b S_L  A   B    exponent vb]
    '''

    def __init__(self, args, model_type=190, rain_type=None, out_resolution=60.0, sav_type=None,component2print=None):
        self.model_type = model_type 
        self.rain_type = rain_type
        self.out_resolution = out_resolution
        self.sav_type = sav_type

        if component2print == None:
            self.comp2print = ['Time', 'LinkID', 'State0']
        self.comp2print = self._CombineList(self.comp2print)

        try:
            self.__unpack_args(args)
            self.sav_path = self._CheckNone(self.sav_path)
            self.dam_path = self._CheckNone(self.dam_path)
            self.snapshot_path = self._CheckNone(self.snapshot_path)
            self.__fileFlags()
        except (TypeError, KeyError):
             raise('Invalid or Missing input!')
        
        if rain_type in [2,5]:
            if self.chunk_size==None or self.time_resolution==None or self.bin_unix1==None or self.bin_unix2==None:
                raise('Missing arguments. Provide arguments for binary rainfall!')
        else:
            self.chunk_size = self._CheckNone(self.chunk_size)
            self.time_resolution = self._CheckNone(self.time_resolution)
            self.bin_unix1 = self._CheckNone(self.bin_unix1)
            self.bin_unix2 = self._CheckNone(self.bin_unix2)
        

      

    def __unpack_args(self, args):
        self.begin =  args.get('begin')
        self.end = args.get('end')
        self.Parameters = args.get('Parameters')
        self.rvr_path = args.get('rvr_path')
        self.prm_path = args.get('prm_path')
        self.initialCond_path = args.get('initialCond_path')
        self.rainfall_path = args.get('rainfall_path')
        self.chunk_size = args.get('chunk_size')
        self.time_resolution = args.get('time_resolution')
        self.bin_unix1 = args.get('bin_unix1')
        self.bin_unix2 = args.get('bin_unix2')
        self.evap_path = args.get('evap_path')
        self.output_path = args.get('output_path')
        self.sav_path = args.get('sav_file')
        self.scratch_path = args.get('scratch_path')
        self.dam_path = args.get('dam_path')
        self.snapshot_path = args.get('snapshot_path')
        
    
    def __fileFlags(self):
        topo_flags = {'rvr':0, 'prm':0,'dbc':3,}
        rvr_type = self.rvr_path.split('.')[-1]
        prm_type = self.prm_path.split('.')[-1]
        self.rvr_type = topo_flags[rvr_type]
        self.prm_type = topo_flags[prm_type]


        ini_flags = {'ini':0, 'uini':1, 'rec':2, 'dbc':3, 'h5':4}
        ini_type = self.initialCond_path.split('.')[-1]
        self.ini_type = ini_flags[ini_type]
        
        if self.rain_type==None: 
            rain_flags = {'str':1, 'dbc':3, 'ustr':4}
            rain_type = self.rainfall_path.split('.')[-1]
            self.rain_type = rain_flags[rain_type]

        evap_flags = {'mon':7}
        evap_type = self.evap_path.split('.')[-1]
        self.evap_type = evap_flags[evap_type]

        out_flags = {'dat':1, 'csv':2, 'h5':5}
        out_type = self.output_path.split('.')[-1]
        self.out_type = out_flags[out_type]
       
        if self.sav_type !=3:
            sav_flags = {'%':0, 'sav':1, 'dbc':2}
            sav_type = self.sav_path.split('.')[-1]
            self.sav_type = sav_flags[sav_type]
        elif self.sav_type == 3:
            self.sav_path = ''
        
        dam_flags = {'%':0, 'dam':1, 'qvs':2}
        dam_type = self.dam_path.split('.')[-1]
        self.dam_type = dam_flags[dam_type]

        snap_flags = {'%':0, 'rec':1, 'dbc':2,'h5':3}
        snap_type = self.snapshot_path.split('.')[-1]
        self.snap_type = snap_flags[snap_type]
    
    def _CheckNone(self,s):
        return '%' if s is None else s
    
    def _CombineList(self, s):
        temp = [ss+'\n' for ss in s]
        return ''.join(temp[:])
    
    def WriteGlobal(self, gbl_name=None):
        '''
            Parameters:
                gbl_name:str, the name of global file to be saved without extension (optional)
                              full path can be given together with the gbl_name
        '''
        gbl_params = self.Parameters.split(' ')
        n_params = len([i for i in gbl_params if i!=''])
        if self.model_type == 190:
            _Template = '../base_files/190BaseGlobal.gbl'
            assert n_params == 6
        elif self.model_type == 254:
            _Template = '../base_files/254BaseGlobal.gbl'
            assert n_params == 12

        file_gbl = open(_Template, 'r') 
        template_gbl = file_gbl.read()
        file_gbl.close()
        content_gbl = Template(template_gbl)
        new_gbl = content_gbl.safe_substitute(n_component=len(self.comp2print.split('\n'))-1,
                                      list_component=self.comp2print,                                      
                                      date1=dt.utcfromtimestamp(int(self.begin)).strftime("%Y-%m-%d %H:%M"),
                                      date2=dt.utcfromtimestamp(int(self.end)).strftime("%Y-%m-%d %H:%M"), 
                                      Parameters=self.Parameters,
                                      rvr_type=self.rvr_type, rvr_file=self.rvr_path,
                                      prm_type=self.prm_type, prm_file=self.prm_path ,
                                      ini_type=self.ini_type , initial_file=self.initialCond_path,
                                      rain_type=self.rain_type , rain_file=self.rainfall_path,
                                      chunk_size=self.chunk_size,
                                      time_resolution=self.time_resolution,
                                      bin_unix1=self.bin_unix1, 
                                      bin_unix2=self.bin_unix2,
                                      unix1=self.begin , unix2=self.end , 
                                      evap_type=self.evap_type, evap_file=self.evap_path,
                                      out_type=self.out_type, out_resolution=self.out_resolution, 
                                      output=self.output_path,
                                      save_type= self.sav_type, sav_file=self.sav_path,
                                      scratch_file=self.scratch_path,
                                      dam_type = self.dam_type, dam_file=self.dam_path,
                                      snap_type = self.snap_type,
                                      snapshot_path = self.snapshot_path)


        if gbl_name==None:
            gbl_name = ''.join([choice(string.ascii_lowercase + string.digits) for _ in range(8)])

        file = open(gbl_name+'.gbl', 'w')
        file.write(new_gbl)
        file.close()
        print(f'{gbl_name}.gbl is created!')