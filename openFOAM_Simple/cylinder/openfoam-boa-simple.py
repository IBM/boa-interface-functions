#Licensed Materials - Property of IBM
#“Restricted Materials of IBM”
#5765-R17
#© Copyright IBM Corp. 2020 All Rights Reserved.
#US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp

from boaas_sdk import BOaaSClient

import numpy as np
import datetime

import warnings
warnings.filterwarnings('ignore')

import subprocess
import sys

boaServiceURL = input("Enter IBM Bayesian Optimization Accelerator services URL : ")
userId = input("Enter User ID for white listed BOA user : ")
password = input("Enter User password to run the BOA experiment : ")
baseDir = input("Enter Directory that holds the Template folder :  ")

def objective_func(x):
    """CFD flow optimisation
    This is objective function for the optimization. This will be called and executed 
    in the Openfoam environment on client side. This function is used to calculate 
    the value of Kinetic energy after getting values of various design variables from 
    IBM Bayesian Optimization Accelerator server.
    It has 4 sub process inside it and returns a float kinetic energy(Y) value/result 
    of the simulation for that epoch using the 5 design variables(X - x1, x2, x3, x4, x5).
    Takes in these 5 parameters and perform Preprocessing , set boundary consitons ,
    simulation process for the epoch and then postprocess the result for the epoch
    and return the result.

    PARAMS : x is a vector of 5 values
    x1 - FVEL Flow Velocity
    x2 - PRESS Pressure
    x3 - TKE Turbulent Kinetic energy
    x4 - TEPS Turbulent Epsilon
    x5 - U wall Velocity
    returns kinetic energy(Y) at a specific point (2,0,0) 

    """

    # Create simulation skeleton
    args=[str(el) for el in x]
    cmd=args
    args.insert(0, baseDir+"/preprocess")
    subprocess.call(cmd, cwd=baseDir)

    # Deform the geometry based on this function's arguments 
    args=[str(el) for el in x]
    cmd=args
    args.insert(0, baseDir+"/setBCs")
    subprocess.call(cmd, cwd=baseDir)

    # Run an OpenFOAM simulation to compute the flow around the cylinder
    args=[str(el) for el in x]
    cmd=args
    args.insert(0, baseDir+"/simCFD")
    subprocess.call(cmd, cwd=baseDir)

    # Collect the kinetic energy and pass it to this function
    args=[str(el) for el in x]
    cmd=args
    args.insert(0, baseDir+"/postprocess")
    stdout = subprocess.check_output(cmd, cwd=baseDir).decode('utf-8').strip()

    print("Epoch ran at : " + str(datetime.datetime.now()) + " with following Deformation parameters : " + str(args))
    print("Epoch result = " + str(stdout))

    return float(stdout)

# Setting up of the BOA experiment configuration dictionary to be  used in experiment creation and execution. 
# Details of all these experiment configuration parameters are explained in the readme file.
openFOAM_experiment = {
    "name": "Simple OpenFOAM example",
      "domain": [
      {
        "name": "x1",
        "min": 0,
        "max": 20,
        "step": 0.01
      }, {
        "name": "x2",
        "min": 0,
        "max": 0.01,
        "step": 0.001
      }, {
        "name": "x3",
        "min": 1.4,
        "max": 1.6,
        "step": 0.01
      }, {
        "name": "x4",
        "min": 0.85,
        "max": 0.9,
        "step": 0.01
      }, {
        "name": "x5",
        "min": -0.5,
        "max": 0.5,
        "step": 0.01
      }
      ],
    "model":{"gaussian_process": {
    "kernel_func": "Matern52",
    "scale_y": True,
    "scale_x": False,
    "noise_kernel": True,
    "use_scikit": True
     }},
    "optimization_type": "min",
    "initialization": {
      "type": "random",
      "random": {
        "no_samples": 1,
        "seed": None
      }
    },
    "sampling_function": {
    "type": "expected_improvement",
    "epsilon": 0.03,
    "optimize_acq": False,
    "outlier": False,
    "bounds": None,
    "scale": False,
    "explain": {
      "feature_importance": True,
      "feature_interaction": ['PDP', 'H_statistic'],
      "features_idx": [0,1]
    }
    }
}

# Connect to the desired BOaaS API

boaas = BOaaSClient(host=boaServiceURL)
user = {"_id": userId , "password": password }
user_login = boaas.login(user)
user_token = user_login["logged_in"]["token"]

# Construct the BOA experiment
exp_user_object = { "_id": user["_id"], "token": user_token}
experiment_res = boaas.create_experiment(exp_user_object, openFOAM_experiment)
experiment_id = experiment_res["experiment"]["_id"]

# Run the BOA experiment
boaas.run(experiment_id=experiment_id, user_token=user_token, func=objective_func, no_epochs=5, explain=True)
best_observation = boaas.best_observation(experiment_id, user_token)
print("best observation:")
print(best_observation)
boaas.stop_experiment(experiment_id=experiment_id, user_token=user_token)
