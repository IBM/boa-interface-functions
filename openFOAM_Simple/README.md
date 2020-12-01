
This example implements a possible instrumentation of a 
basic CFD simulation, run with OpenFOAM, with BOA.


The simulation models the flow around a cylinder, where
the control variables are the flow's inlet velocity,
initial pressure, turbulent kinetic energy, dissipation
rate, and wall velocity. The objective is to minimize the 
turbulent kinetic energy at a point in the cylinder's wake 
(coordinates x=2, y=0=z).

This example works against any hosted BOA services.

The OpenFOAM simulation relies on ESI-OpenFOAM. Compiling 
OpenFOAM requires mpicc. An easy way to install OpenFOAM
on POWER is to reely on the WMLCE-1.7.0 conda environment
for MPI and other dependencies as described below.

Instructions for OpenFOAM setup:

1) Setup WMLCE environment with the following steps:
     conda create --name wmlce_env python=3.6
     conda activate wmlce_env
     conda install powerai

2) Download OpenFOAM-v2006.tgz from 
   https://www.openfoam.com/download/install-source.php

3) tar -xvf OpenFOAM-v2006.tgz

4) source $PWD/OpenFOAM-v2006/etc/bashrc (The wmlce_env
   conda environment need to be active for this command)

5) cd $PWD/OpenFOAM-v2006

6) ./Allwmake -j


The wmlce_env environment is used only for OpenFOAM setup. The
python code openfoam-boa-simple.py is executed within the 
boa conda environment.
To run this openfoam-boa-simple.py file , BOA sdk package
should be installed on the machine where openfoam simulator 
is running. Python3 is pre-req for BOA SDK.

**Usage**

To run the openfoam-boa-simple.py , you need to run with 
python interpreter
Then it asks for 4 values which user needs to enter one by one

```

  python openfoam-boa-simple.py
  Enter IBM Bayesian Optimization Accelerator services URL : http://BOA_Server_IP_Address:80 or https://BOA_Server_IP_Address:443
  Enter User ID for white listed BOA user : abc@abc.com
  Enter User password to run the BOA experiment : xyz
  Enter Directory that holds the Template folder :  ../cylinder

```

