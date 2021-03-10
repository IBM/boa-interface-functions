# --------------------------------------------------------------------------
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2020 All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# --------------------------------------------------------------------------
import pandas as pd
import numpy as np
import time   # for timing iteration time
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from boaas_sdk import BOaaSClient

import argparse

"""
This example demonstrates BOA usage for a tabulated function stored as a table file.
The BOA SDK has been designed to be simple to use, but flexible in the range of
configurations available for tailoring the optimization. This is achieved using
the BOaaSClient object, which facilitates all communication with the BOA server.
The optimization configuration is handled via a Python dictionary (or
equivalently a JSON file).
"""

## Setup argparse for command-line inputs
argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description = '''
        This example demonstrates basic BOA usage for a simple optimization problem.
        The BOA SDK has been designed to be simple to use, but flexible in the range of
        configurations available for tailoring the optimization. This is achieved using
        the BOaaSClient object, which facilitates all communication with the BOA server.
        The optimization configuration is handled via a Python dictionary (or
        equivalently a JSON file).
        ''')
argparser.add_argument('--hostname',
    dest    = 'clientHost',
    action  = 'store',
    default = 'localhost',
    help    = 'Set hostname to connect to. Defaults to "localhost"')

argparser.add_argument('--port',
    dest    = 'port',
    action  = 'store',
    default = '5000',
    help    = 'http port number for BOA. Defaults to "5000"')

argparser.add_argument('--userid',
    dest    = 'userid',
    action  = 'store',
    default = 'boa_test@test.com',
    help    = 'Use a userid (email) which has been registered to the web UI. Defaults to "boa_test@test.com"')

argparser.add_argument('--password',
    dest    = 'password',
    action  = 'store',
    default = 'password',
    help    = 'The password of the userid. Defaults to "password"')

argparser.add_argument('--epochs',
    dest    = 'epochs',
    action  = 'store',
    type    = int,
    default = 10,
    help    = 'The number of epochs. Defaults to 10')

argparser.add_argument('--seed',
    dest    = 'seed',
    action  = 'store',
    type    = int,
    default = 20200904,
    help    = 'The seed for initial random sampling. Defaults to 20200904. It was None originally')

argparser.add_argument('--dataset',
    dest    = 'dataset',
    action  = 'store',
    default = 'ammp',
    help    = 'The dataset (benchmark) to be optimized. Defaults to "ammp"')

## Parse command-line arguments
args = argparser.parse_args()

#hostname = 'http://{}:80'.format(args.clientHost)
hostname = f"http://{args.clientHost}:{args.port}"
print ("Connecting to host: {}".format(hostname))
boaas = BOaaSClient(host=hostname)

# Read the 18-column data - the last 13 are "design variables":
# config  benchmark  cycle  inst  power
# depth  width  gpr_phys  br_resv  dmem_lat  load_lat  br_lat  fix_lat  fpu_lat
# d2cache_lat  l2cache_size  icache_size  dcache_size
df = pd.read_table("input/data_model_{}.txt".format(args.dataset))
print(df)
# Get bips (billions of instructions per second)
# Ref: http://people.duke.edu/~bcl15/code/core/code_asplos06.txt
df['bips']=df['inst']/1.1*df['depth']/df['cycle']/18
domain = df[['depth',  'width', 'gpr_phys', 'br_resv', 'dmem_lat', 'load_lat', 'br_lat', 'fix_lat', 'fpu_lat', 'd2cache_lat', 'l2cache_size', 'icache_size', 'dcache_size']].to_numpy().tolist()

my_max = df['bips'].max()

# Create an empty DataFrame with column names for storing input parameters and observations
columns = list()
columns.append("iter_no")
for i in range(1,13+1):
   columns.append("x"+str(i))

columns.append("f_value")
columns.append("iter_time")
df_exp = pd.DataFrame(columns=columns)

# Initialize the global iteration count and time keeper
iter = 0
tic = time.perf_counter()

def myfunc(x):
    global iter, df_exp, tic, toc
    iter += 1
    toc = time.perf_counter()
    iter_time = toc - tic
    tic = toc

    # 13-parameter func for core performance simulation
    depth = int(0.5 + x[0])
    width = int(0.5 + x[1])
    gpr_phys = int(0.5 + x[2])
    br_resv = int(0.5 + x[3])
    dmem_lat = int(0.5 + x[4])
    load_lat = int(0.5 + x[5])
    br_lat = int(0.5 + x[6])
    fix_lat = int(0.5 + x[7])
    fpu_lat = int(0.5 + x[8])
    d2cache_lat = int(0.5 + x[9])
    l2cache_size = int(0.5 + x[10])
    icache_size = int(0.5 + x[11])
    dcache_size = int(0.5 + x[12])

    # Get the function value from the corresponding row
    # df.loc[... is a series.   .iloc[0] is the first (only) element of the series - should have a better way
    bips = df.loc[(df.depth==depth) & (df.width==width) & (df.gpr_phys==gpr_phys) & (df.br_resv==br_resv) & (df.dmem_lat==dmem_lat) & (df.load_lat==load_lat) & (df.br_lat==br_lat) & (df.fix_lat==fix_lat) & (df.fpu_lat==fpu_lat) & (df.d2cache_lat==d2cache_lat) & (df.l2cache_size==l2cache_size) & (df.icache_size==icache_size) & (df.dcache_size==dcache_size), 'bips'].iloc[0]

    print("OBS=", iter, depth,  width, gpr_phys, br_resv, dmem_lat, load_lat, br_lat, fix_lat, fpu_lat, d2cache_lat, l2cache_size, icache_size, dcache_size, bips, iter_time)
    df_exp.loc[len(df_exp.index)] = [iter, *x, bips, iter_time]
    with open ("{}.csv".format(args.dataset), 'w') as mycsv:
        df_exp.to_csv (mycsv, header = not mycsv.tell(), index = False)

    return bips

experiment_config = {
    "name": args.dataset,
    "domain": domain,
    "model":{"gaussian_process": {
    "kernel_func": "Matern52",
    "scale_y": True,
    "scale_x": False,
    "noise_kernel": True,
    "use_scikit": True
     }},
    "optimization_type": "max",
    "initialization": {
      "type": "random",
      "random": {
        "no_samples": 3,
        "seed": args.seed
        #"seed": 20200904
      }
    },
    "sampling_function": {
    "type": "expected_improvement",
    "epsilon": 0.03,
    "optimize_acq": False,
    "outlier": False,
    "bounds": None
  }

}

user = {"_id": args.userid, "password": args.password}
user_login = boaas.login(user)

if user_login == None:
    user = {"_id": "boa_test@test.com", "name": "BOA Test",
            "password": "password", "confirm_password": "password" }
    boaas.register(user)
    user_login = boaas.login(user)

print(user_login)
user_token = user_login["logged_in"]["token"]
print("user token")
print(user_token)
create_exp_user_object = { "_id": user["_id"], "token": user_token}
experiment_res = boaas.create_experiment(create_exp_user_object, experiment_config)
print(experiment_res)
experiment_id = experiment_res["experiment"]["_id"]
print("DBG-experiment_id = ", experiment_id)
boaas.run(experiment_id=experiment_id, user_token=user_token, func=myfunc, no_epochs=args.epochs, explain=False)
best_observation = boaas.best_observation(experiment_id, user_token)
print("best observation:")
print(best_observation)
print("True value: ", my_max)
boaas.stop_experiment(experiment_id=experiment_id, user_token=user_token)
