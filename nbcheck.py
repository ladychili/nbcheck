#! /usr/bin/env python3

import requests
import json
import subprocess
import pandas as pd
import argparse

def nb_check():
    parser = argparse.ArgumentParser(description='List active ipython notebook kernels and corresponding process information')
    parser.add_argument('-s', '--server', type=str, default='localhost', help='Jupyter server address, default: localhost')
    parser.add_argument('-p', '--port', type=int, default=8888, help='Jupyter server port, default: 8888')
    parser.add_argument('-t', '--token', type=str, default=None, help='Token is required')
    args = parser.parse_args()

    server = args.server
    port = args.port
    token = args.token
    url = 'http://{server}:{port}/api/sessions?token={token}'.format(server=server, port=port, token=token)

    if token==None:
        print('Abort: Token is missing')
        exit()

    # api
    response = requests.get(url)
    sessions = json.loads(response.text)
    nb_session = []
    for s in sessions:
        row = {'notebook':s['path'].split('/')[-1],
            'exec':s['kernel']['execution_state'],
            'KID':s['kernel']['id']}
        nb_session.append(row)
    nb_session = pd.DataFrame(nb_session)


    # prc
    grep_list = subprocess.getoutput('ps aux| grep ipy').splitlines()
    nb_procs = []
    for proc in grep_list:
        proc_info = proc.split()
        if not 'ipykernel_launcher' in proc_info:
            continue
        row = {'PID': proc_info[1],
                '%CPU': proc_info[2],
                '%MEM': proc_info[3],
                'VSZ': str(round(int(proc_info[4])/1024))+'M',
                'RSS': str(round(int(proc_info[5])/1024))+'M',
    #             'STAT': proc_info[7],
                'STARTED': proc_info[8],
                'KID': proc_info[-1][-41:-5]}
        nb_procs.append(row)
    nb_procs = pd.DataFrame(nb_procs)

    # merge
    try:
        nb = pd.merge(nb_session,nb_procs,how='outer')[['notebook', 'exec','VSZ','RSS', 'PID', '%CPU', '%MEM',  'STARTED', 'KID']]
        print(nb)
    except:
        print('Error: Failed to merge nb_sessions and nb_process...')
    

if __name__ == "__main__":
    nb_check()