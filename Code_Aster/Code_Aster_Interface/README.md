+ Licensed Materials - Property of IBM
+ “Restricted Materials of IBM”
+ 5765-R17
+ © Copyright IBM Corp. 2020 All Rights Reserved.
+ US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp


**Description**
---

```
This example implements a possible instrumentation of a basic Finite Element(FE) simulation, run with Code Aster, 
with IBM Bayesian Optimization Accelerator.

This example is covering the use case where, we need to find out the value of length, breadth and thickness 
of a rectangular steel plate for which the displacement will be maximum on applying force for specific 
interval of time

```


**Input Values**
---


```
  boaServiceURL = input("Enter IBM Bayesian Optimization Accelerator services URL : ")
  userId = input("Enter User ID for white listed BOA user : ")
  password = input("Enter User password to run the BOA experiment : ")
  baseDir = input("Enter Directory path that holds the input .comm, .mmed and .export files :  ")

```

While running this Interface_function , It ask for user to input 4 values . Those values are :

1. IBM Bayesian Optimization Accelerator service URL .
2. User ID for white listed BOA user trying to run the experiment
3. User password of the account from which the experiment is going to be executed
4. Directory that holds the required input files(.mmed, .comm, .export files)


**Experiment configuration**
---

BOA uses a configuration JSON file or an equivalent Python dictionary to configure the optimization. This
topic describes the parameters used for configuration.

1. name

    + The name of your optimization experiment.

2. domain


      ```
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
    ]
      ```

    + The domain is the set of parameters that you want to search through to find the optimum parameters.
      For an engineering problem this might be the list of possible designs for a component, such as the
      engine of a car. For a chemical manufacturing problem, this could be the list of possible combinations
      of ingredients.
    + To define the domain as a grid, we specify the name of each parameter, a minimum value, a
      maximum value, and a step size.

3. model

    ```
    "model":{
      "gaussian_process": {
      "kernel_func": "Matern52",
      "scale_y": True,
      "scale_x": False,
      "noise_kernel": True,
      "use_scikit": True
      }
    }

    ```

    + Defines the surrogate model to use


4. optimization_type

    + Defines the type of optimization technique : min (for minimization ) max (for maximization )

5. initialization

    ```
    "optimization_type": "min",
       "initialization": {
         "type": "random",
         "random": {
           "no_samples": 3,
           "seed": None
         }
       }
    ```

    + Specifies how to initialize the optimizer. There are two options: initialization by random samples
      (random) or by uploading observations (observations). Random initialization randomly selects
      values from the domain, whereas the observation-based initialization allows you to specify a list of
      parameter values to initialize the optimizer.
      Example of specifying random initialization:

    + no_samples
        - Specifies the number of samples to use for initialization.
    + seed
        - Specifies whether to set the NumPy random seed for the initialization.

6. sampling_function

    ```
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

    ```

    + Specifies how the optimizer will sample from the domain
    + type
       - Specifies what type of acquisition function to use.
       - The acquisition function is core to how Bayesian optimization functions,
         and different acquisition functions will result in different optimizer
         behaviors.
       - It is typically advised to use one of the following acquisition functions:
         expected_improvement, adaptive_expected_improvement, probablity_improvement,
         or adaptive_probability_improvement
       - BOA optimizer also supports, epsilon_greedy, maximum_entropy and random_sampler sampler
         types but only when design variables domain is defined as Grid(Discrete variables).
     + epsilon
        - This variable controls the degree to which the optimizer will tend to
          exploit known 'good' areas of the domain (low epsilon), or favor exploring
          less well-known areas of the domain (high epsilon).
     + scale
        - Depending on version of BOA used, the scale parameter may not be required.
        - If required, this should always be set to False.
     + bounds
        - Contains the upper and lower bound for each parameter in the list.
     + explain
        - Defines the explainability features computed for BOA. If the explain field
          isn't used, BOA will run without explainability. Its parameters are :
        - feature_importance . Whether to compute the feature importance.
        - feature_interaction . A list of feature interactions to use, one or both of
          PDP and H_statistic can populate the list.
        - features_idx

**BOA Services**
---


1. Login API

    ```
      boaas = BOaaSClient(host=boaServiceURL)
      user = {"_id": userId , "password": password }
      user_login = boaas.login(user)
      user_token = user_login["logged_in"]["token"]

    ```
    
    + Set BOA instance
    + create UserId and password dictionary using data shared by User at run time
    + Use the BOA's login API
    + Fetch user token

2. Construct BOA experiment

    ```
    exp_user_object = { "_id": user["_id"], "token": user_token}
    experiment_res = boaas.create_experiment(exp_user_object, openFOAM_experiment)
    experiment_id = experiment_res["experiment"]["_id"]

    ```
    
    + Define experiment user object
    + Use the BOA's create_experiment in order to create an experiment .
        - API takes in the experiment user object created above and Experiment Configuration created above .
    + Fetch the experiment_id from the experiment created above .

3. Run BOA experiment

    ```
    boaas.run(experiment_id=experiment_id, user_token=user_token, func=objective_func, no_epochs=3, explain=True)
    best_observation = boaas.best_observation(experiment_id, user_token)
    print("best observation:")
    print(best_observation)
    boaas.stop_experiment(experiment_id=experiment_id, user_token=user_token)

    ```
    
    + Use the BOA's run API to execute the experiment .
       - it takes the Experiment_id , user token , objective_function , number of epochs
    + execute the best_observation API to get the best output .
       - for the number of epoch it returns the best value depending upon the optimization_type
    + prints the final output value .
    + Run the stop_experiment API to change the experiment status and stop the activity .


**objective_function**
---
An objective function is the output that you want to maximize or minimize. It is
what we will measure designs against to decide which option is best. The objective function can be
thought of as the goal of your generative design process.

```
def objective_func(x):
    """
        This objective function calculates the 
        displacement of a rectangular steel plate after applying a constant 
        force for 1.2 milliseconds for various values of length, breadth and 
        thickness. These values of design variables will be 
        generated as input on every iteration of optimization of IBM Bayesian 
        Optimization Accelerator. 

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

    # Printing the design variables value used during the simulation on the console
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
    f = post_process(baseDir)

    # Printing the displacement value on the console
    print("Displacement at is: {} m".format(f))

    return f

```


BOA uses this function to perform 4 different process to prepare the data , populate with respective values ,
run simulations and prepare the output variable and return the optimized value.

+ Takes in 3 arguments (Length, Breadth and Thickness)
+ these 3 arguments in the form of vector is shared by BOA during every epoch run
+ It returns a value that is taken as the output.
+ This function internally executes 4 processes
+ preprocess  :     Prepare the data for every epoch by replacing the design variables value in input .comm file for each epoch
+ simulation  :     run the Code Aster simulation process 
+ postprocess :     fetches the output from the output .resu file and store it in a variable
