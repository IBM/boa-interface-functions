
This example implements a possible instrumentation of a 
basic Finite Element(FE) simulation, run with Code Aster, with BOA.

This is a sample test case pre-existed with Code Aster installation which can
be referred at below link
https://www.code-aster.org/V2/doc/v14/en/man_v/v2/v2.03.115.pdf

This example is covering the use case where, we need to find out the value 
of length, breadth and thickness of a rectangular steel plate for which 
the displacement will be maximum on applying force for specific 
interval of time. Force is a function of time as defined below-

F(t)=Q0 E K e cos(Kl)sin(wt)
Q0 ( =10^16 m ) - amplitude of the loading
E  Young modulus defined above (in N / m 2 )
e  the thickness defined above (in m )
l  the dimension of the plate defined above (in m )
K ( = pi/ 8l ) the number of wave of the analytical solution (in m −1 )
w  frequency (time 2*pi ), related to the number of wave


This example works against any hosted BOA services.

**Setup**
All the required input files like .comm, .mmed and .export files should be
present in the "data" folder.

"Code_aster_interface" directory contains 2 python files - code_aster_example.py-
this file acts as an interface function while the code_aster_utils.py has the
utility functions to support pre-processing and post-processing.

Code Aster environment should be running.

This examples come with the default export file. We can also generate our own
.export file using "astk"( Code Aster UI) utility or modify this existing file as per our needs.

**Usage**

To run the code_aster_example.py , you need to run with 
python interpreter
Then it asks for 4 values which user needs to enter one by one

```

  python openfoam-boa-simple.py
  Enter IBM Bayesian Optimization Accelerator services URL : http://BOA_Server_IP_Address:80 or https://BOA_Server_IP_Address:443
  Enter User ID for white listed BOA user : abc@abc.com
  Enter User password to run the BOA experiment : xyz
  Enter Directory path that holds the input .comm, .mmed and .export files :  ../data
```

