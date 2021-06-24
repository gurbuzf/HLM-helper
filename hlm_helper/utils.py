import numpy as np
import pandas as pd
import h5py

def read_rvr(path):
    '''Returns information in the rvr file

    Parameters
    -----------
        path : str
            rvr file directory
    Returns
    --------
        links : list
            list of link_ids

        connectivity : list  
            connectivity of the links [km^2]

    '''

    rvr = []
    with open(path) as _:
        for line in _:
            line = line.strip()
            if line:
                rvr.append(line)
    # n_links = int(rvr[0])
    links = []
    connectivity = []
    for i in range(1,len(rvr)):
        line = rvr[i]
        if i%2 != 0:
            links.append(int(line))
        else:
            conn = list(map(int, rvr[i].split(' ')))
            if conn==[0]:conn=[]
            connectivity.append(conn[1:]) #First element, number of parents, not included
    return links, connectivity

def read_prm(path):
    '''Returns information in the prm file

    Parameters
    -----------
        path : str
            prm file directory
    Returns
    --------
        links : list
            list of link_ids

        A_i : list  
            Area of total upstream area [km^2]

        L_i : list 
            Length of the link [m]
        
        A_h : list 
            Area of the hillslope [m^2]
    '''
    prm = []
    with open(path) as _:
        for line in _:
            line = line.strip()
            if line:
                prm.append(line)
    links = []
    params = []
    for i in range(1, len(prm)):
        line = prm[i]
        if i%2 != 0:
            links.append(int(line))
        else:
            prms = list(map(float, prm[i].split(' ')))
            params.append(prms)#
    params =np.array(params)
    A_i = params[:, 0]
    L_i = params[:, 1]*10**3
    A_h = params[:, 2]*10**6

    return links, A_i, L_i, A_h


def initialcondition4hillslopes(qmin, At_up, A_up, k3=340, s_ponded=0.0, s_toplayer=1e-6):
    ''' Returns a dictionary including initial conditions for states(i.e channels, )

    Parameters
    -----------
        qmin : float  
            baseflow observed at the outlet [m3/s]
        
        At_up : float,  
            drainage area of the catchment [km2]
        
        A_up : np.array 
            upstram area of the links [km2]
        
        k3 : float 
            number of days ground water flow reaches adjacent stream (default 340 days)

        s_ponded : float [optional]
            initial condition for ponding (default 0.0)

        s_toplayer : float [optional]  ---CAUTION: bounded variable---
            initial condition for top layer (default 1e-6 --very dry soil condition---)
    Returns
    ---------
        q : list
            initial condition for channel flow

        s_p : list 
            initial condition for ponding 

        s_t : list 
            initial condition for top layer 

        s_s : list 
            initial condition for subsurface
    '''
    dim  = len(A_up)
    k3 = 1/(k3 * 24 * 60)
    factor = 60/1e6
    q = ((qmin / At_up) * A_up).tolist()
    s_p = [s_ponded for _ in range(dim)]
    s_t = [s_toplayer for _ in range(dim)]
    ss = qmin / (At_up * k3) * factor 
    ss = round(ss, 5)
    s_s = [ss for _ in range(dim)]

    return q, s_p, s_t, s_s


def read_h5(h5_file_path):
    """Read h5 file 

    Parameters
    ----------
    hdf_file_path : str
        full path of the h5 file

    Returns
    ------
        hdf_file_content : np.array
            data in the h5 file as a numpy array 
        headers : 
            data headers in the array
    
    """
    
    with h5py.File(h5_file_path, "r") as hdf_file:
        hdf_file_content = np.array(hdf_file.get("outputs"))
        headers = hdf_file_content.dtype.names
    
    return hdf_file_content, headers

def filter_state(hdf_file_content, link_id, state='State0'):
    """Get the time series of a state for a link
    
    Parameters
    ----------
    hdf_file_content : np.array
        data in the h5 file as a numpy array

    link_id : int
        link_id to be filtered
    
    state : str , ex. State0(default), State1 ... 
        state to be retrieved from h5 file

    Returns
    ------
    time : np.array
        array of timesteps
    
    state: np.array
        state time series
    
    """

    index = hdf_file_content['LinkID'] == link_id
    time = hdf_file_content['Time'][index]
    state = hdf_file_content[state][index]

    return time, state 

def write_ustr(rainfall_ts, time, fullpath):
    """Writes rainfall data in  a 'ustr' file

    Parameters
    ----------
    rainfall_ts : np.array or list
        rainfall time series
    
    time : np.array or list
        timesteps
    
    fullpath : path for the ustr file --with 'ustr' extension--

    Returns
    --------
        None   
    
    """
    with open(fullpath, 'w') as ustr:
        ustr.write(str(len(time)))
        ustr.write('\n')
        for i, t in enumerate(time):
            ustr.write(f'{t} {rainfall_ts[i]}\n')

def create_ini_file(model_type, ini_path, links, q, s_p, s_s, s_t=None, \
                    dam_links=None, S=None, initial_time=0):
    """Writes initial conditions in  a 'ini' file

    Parameters
    ----------
    model_typr : int
        type of the HLM model (190, 254, 255)
    
    ini_path : str
        path for the 'ini' file --with 'ini' extension--
    
    links : list
        list of the link ids

    q : list
        initial condition for channel flow
    
    s_p : list
        initial condition for ponding 
    
    s_s : list 
        initial condition for subsurface

    s_t : list  (default None)
        initial condition for top layer. 190 does not have this state. 
            if model_type is 254, this state must be given
    
    dam_links : list (default None)
        links where a dam is located. Only for model_type=255

    S : list (default None)
        list of the initial storages of the dams. Only for model_type=255.
            the order must follow  'dam_links' 
    
    Returns
    --------
        None   
    
    """
    n_links = len(links)
    if model_type == 190:
        with open(ini_path, 'w') as ini:
            ini.write(f'{model_type}\n')
            ini.write(f'{n_links}\n')
            ini.write(f'{initial_time}\n')
            for i, link in enumerate(links):
                ini.write(f'{link}\n')
                ini.write(f'{q[i]} {s_p[i]} {s_s[i]}\n\n')
        
    elif model_type == 254:
        with open(ini_path, 'w') as ini:
            ini.write(f'{model_type}\n')
            ini.write(f'{n_links}\n')
            ini.write(f'{initial_time}\n')
            for i, link in enumerate(links):
                ini.write(f'{link}\n')
                ini.write(f'{q[i]} {s_p[i]}  {s_t[i]} {s_s[i]}\n\n')

    elif model_type == 255:
        with open(ini_path, 'w') as ini:
            ini.write('255\n')
            ini.write(f'{n_links}\n')
            ini.write(f'{initial_time}\n')
            
            for i, link in enumerate(links):
                ini.write(f'{link}\n')
                if link in dam_links:
                    ind = dam_links.index(link)
                    _S = S[ind]
                else:
                    _S = 0
                ini.write(f'{q[i]} {_S}  {s_p[i]}  {s_t[i]} {s_s[i]}\n\n')    

