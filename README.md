# hlm_helper 

Set of tools facilitating use of Hillslope-Link Model. 
<br>

## Documentation 

 * **Creating Global File** 
---

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
            'scratch_path':'tmp',
            'dam_path':'test.dam',
            'sav_path':'test.sav'
            }

    f = GlobalFileCreator(args, model_type=255,out_resolution=15.0, component2print=['Time', 'LinkID', 'State0','State1'])
    f.WriteGlobal('testing_255')



The docstring can be accesed via `help(GlobalFileCreator)`.

 * **Creating 'ini' File** 
---

    from hlm_helper.utils import (read_prm,
                                  initialcondition4hillslopes, 
                                  create_ini_file)

    links, A_i, L_i, A_h = read_prm('../GeneralFiles/turkey.prm')
    q, s_p, s_t, s_s = initialcondition4hillslopes(30, max(A_i), A_i, k3=340, s_toplayer=0.2)
    create_ini_file(254, '../GeneralFiles/initial_conditions254.ini', links, q, s_p, s_s, s_t)
    create_ini_file(190, '../GeneralFiles/initial_conditions190.ini', links, q, s_p, s_s, s_t=None)


Use `help()` to access the docstring for each function used here.  

