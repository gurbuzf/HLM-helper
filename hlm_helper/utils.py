import numpy as np
import pandas as pd

def read_rvr(path):
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
            connectivity.append(conn[1:]) #First element, number of parents,not included
    return links, connectivity

def read_prm(path):
    '''Returns infromation in rvr file
    input:
        path = rvr directory
    returns:
        A_i:list,  Area of total upstream area of a link [km^2]
        L_i:list, Length of the link [m]
        A_h:list, Area of the hillslope [m^2]
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


def Set_InitialConditions(qmin, At_up, A_up, k3=340):
    ''' Returns a dictionary including initial conditions for states(i.e channels, )

    INPUT:
        qmin:float,  baseflow observed at the outlet [m3/s]
        At_up :float,  Total upstream area [km2]
        A_up:np.array, upstram area of all links [km2]
        k3:float, number of days ground water flow reaches adjacent stream 
    OUTPUT:
        q: initial condition od channel flow
        s_p: initial condition of ponding, set zero for all
        s_t: initial condition of top layer, set 1.000000e-6 for all
        s_s: initial condition of subsurface
    '''
    dim  = len(A_up)
    k3 = 1/(k3 * 24 * 60)
    factor = 60/1e6
    q = ((qmin / At_up) * A_up).tolist()
    s_p = [0.0 for _ in range(dim)]
    s_t = [1.000000e-6 for _ in range(dim)]
    ss = qmin / (At_up * k3) * factor
    ss = round(ss, 5)
    s_s = [ss for _ in range(dim)]

    return q, s_p, s_t, s_s

def Create_IniFile(links, q, s_p, s_t, s_s, f_name, model_type, initial_time=0):
    n_links = len(links)
    if model_type == 190:
        with open(f_name, 'w') as ini:
            ini.write(f'{model_type}\n')
            ini.write(f'{n_links}\n')
            ini.write(f'{initial_time}\n')
            i = 0
            for link in links:
                ini.write(f'{link}\n')
                ini.write(f'{q[i]} {s_p[i]} {s_s[i]}\n\n')
                i += 1
    elif model_type == 254:
        with open(f_name, 'w') as ini:
            ini.write(f'{model_type}\n')
            ini.write(f'{n_links}\n')
            ini.write(f'{initial_time}\n')
            i = 0
            for link in links:
                ini.write(f'{link}\n')
                ini.write(f'{q[i]} {s_p[i]}  {s_t[i]} {s_s[i]}\n\n')
                i += 1
    print('Done!')