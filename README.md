# hlm_helper 
----
Set of tools facilitating use of Hillslope-link Model. 
<br>

## Documentation 
----
    from hlm_helper.input_manager import GlobalFileCreator
    args = {'begin':1522584000, 
            'end':1543665600, 
            'Parameters':'0.33  0.2    -0.1', 
            'rvr_path': 'turkey.rvr', 
            'prm_path': 'turkey.prm', 
            'initialCond_path':'initialconditions_20180401.dbc', 
            'rainfall_path':'unirain.ustr', 
            'evap_path':'evap_average.mon', 
            'output_path':'output.h5', 
            'scratch_path':'/nfsscratch/Users/gurbuz/tmp',
            'dam_path':'test.dam',
            'sav_path':'test.sav'
            }

    f = GlobalFileCreator(args, model_type=255,out_resolution=15.0, component2print=['Time', 'LinkID', 'State0','State1'])
    f.WriteGlobal('testing_255')



The docstring can be accesed via `help(GlobalFileCreator)`.

----

