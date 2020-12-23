# Licensed Materials - Property of IBM “Restricted Materials of IBM” 5765-R17
# © Copyright IBM Corp. 2020 All Rights Reserved. US Government Users
# Restricted Rights - Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp

from boaas_sdk import BOaaSClient
from code_aster_utils import pre_process, post_process

import subprocess

boaServiceURL = input("Enter IBM Bayesian Optimization Accelerator services "
                      "URL : ")
userId = input("Enter User ID for white listed BOA user : ")
password = input("Enter User password to run the BOA experiment : ")
baseDir = input("Enter Directory path that holds the input .comm, .mmed and "
                ".export files :  ")


def objective_func(x):
    """
    This objective function calculates the displacement of a rectangular
    steel plate along the x-axis after applying a force for 1.2 milliseconds
    for various values of design variables i.e. length, breadth and
    thickness. These values of design variables will be generated as input on
    every iteration of optimization of IBM Bayesian Optimization Accelerator.

    It has 3 sub process inside it and returns a float displacement(y)
    value/result of the simulation for that epoch using the 3 design
    variables(X - x1, x2, x3). Takes in these 3 parameters and perform
    pre-processing, simulation process for the epoch and then post-process
    the result for the epoch and return the result.

    PARAMS : x is a vector of 3 values
    x1 - Length of the plate
    x2 - Thickness of the plate
    x3 - Breadth/Width of the Plate
    returns displacement(y) of the plate
    """

    x1 = x[0]
    x2 = x[1]
    x3 = x[2]

    # Calling an Utility 'pre-process' function to pre-process the design
    # variable values before running the simulation
    export_file = pre_process(baseDir, x1, x2, x3)

    # Printing the design variables value used during the simulation on the
    # console
    print("\nLength Used: {} m".format(x1))
    print("Thickness Used: {} m".format(x2))
    print("Width Used: {} m".format(x3))

    # Running the Code Aster simulation to get the displacement
    proc = subprocess.Popen(['as_run', export_file], stdout=subprocess.PIPE,
                            cwd=baseDir)

    # Printing the Exit status of Code aster simulation on the console
    res = proc.communicate()[0].decode("utf-8")
    print("Exit Status of Code Aster Simulation is: ",
          res.split("DIAGNOSTIC JOB :")[1].split("\n")[0])

    # Calling an utility function'post-process' which will get the
    # displacement value from the result file
    y = post_process(baseDir)

    # Printing the displacement value on the console
    print("Displacement is: {} m".format(y))

    return y


# Setting up of the BOA experiment configuration dictionary to be  used in
# experiment creation and execution. Details of all these experiment
# configuration parameters are explained in the readme file.
codeAster_experiment = {
    "name": "Code Aster Example",
    "domain": [
        {
            "name": "x1",
            "min": 1.0,
            "max": 5.0,
            "step": 0.01
        }, {
            "name": "x2",
            "min": 0.1,
            "max": 0.5,
            "step": 0.001
        },
        {
            "name": "x3",
            "min": 1.0,
            "max": 5.0,
            "step": 0.01

        }
    ],
    "model": {"gaussian_process": {
        "kernel_func": "Matern52",
        "scale_y": True,
        "scale_x": False,
        "noise_kernel": True,
        "use_scikit": False
    }},
    "optimization_type": "max",
    "initialization": {
        "type": "random",
        "random": {
            "no_samples": 3,
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
            "features_idx": [0, 1]
        }
    }
}

# Connect to the desired BOaaS API
boaas = BOaaSClient(host=boaServiceURL)

user = {"_id": userId, "password": password}
user_login = boaas.login(user)
user_token = user_login["logged_in"]["token"]

# Construct the BOA experiment
exp_user_object = {"_id": user["_id"], "token": user_token}
experiment_res = boaas.create_experiment(exp_user_object, codeAster_experiment)
experiment_id = experiment_res["experiment"]["_id"]

# Run the BOA experiment
boaas.run(experiment_id=experiment_id, user_token=user_token,
          func=objective_func, no_epochs=40, explain=True)
best_observation = boaas.best_observation(experiment_id, user_token)
print("best observation:")
print(best_observation)
boaas.stop_experiment(experiment_id=experiment_id, user_token=user_token)
