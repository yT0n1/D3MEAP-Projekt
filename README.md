# Data Replacement for Partial Replication

This repository implements an linear-programming based approach on how to solve the problem of data replication.
The acdemic essay on the problem can be found within our paper, this README will focus on the practical aspects.

## Requirements
The project was programmed in Python 3. The needed libaries are listed within the requirements.txt file.

Moreover, if you want to see your trees being printed, you also have to install:
https://www.graphviz.org/

Guriobi solver with an academic license.

## Code Structure

### AMPL
One can find our AMPL implementation in this directory

### Automated Testing
This package include the files which are used to evaluate our approach on desired parameters.

#### Parameters
The parameters enable you to adapte the hardness of the problem you are trying to solve and how long specific tests should run. Be a little careful with these configurations, as it is easily possible to create a configuration which takes more than 15 hours to run.

##### General Configuration for the Problems
These are general parameters valid for all testing algorithms. They essentially define the hardness of the problem.


`num_problems` 	-	Number of Problems to run against. Essentially cross-validation.	

`min_fragments`	-	Minimum number of fragments per problem

`max_fragments`	-	Maximum number of fragments per problem

`min_queries` 	-	Minimum number of queries per problem

`max_queries`  	-	Maximum number of queries per problem

`num_workloads`	-	Number of workloads per problem. A workload is a set of queries.

##### Algorithm Specific Configuration
In addition to these general parameters, most testing algorithms also have their own specific configuration. These are mostly self-explaintory and focus around whether epsilon is turned on or off or how long the test should run (min and max node counts). 

#### What tests are available?
**test_node_count**

This test will create two sets of diagrams, one with the epsilon tuning enabled and one without. The special thing about this testing method is that it runs the different strategies over an increasing node count. This means that one can evaluate the behavior of the stragies over differnt node counts. What you can see are all algorithms evaluated over their time, deviation and space averages. Moreover, a summary view is also provided. This is a great first test to run if you are new to this project.

**test_pareto**

This test will give you a Pareto front in relation to different values of epsilon in regards to the "Complete"-stategy.

**test_timeout**

This test will evaluate the quality parameters like space, runtime and deviation over different timeouts. The goal here is to see how the solutions improve when being given more time. It outputs two sets of diagrams, one with epsilon, one without.

**compare_lp_heuristic**

In this test we try to see if the heuristics are actually better then the complete split. Therefore, we let the complete split run with the time the heuristic needed and see the results. This allows a more fair comparison between both approaches.

**test_runtime_increasing_factors & test_runtime_increasing_factors_combined**

These tests evaluate how much each problem parameter effects the run-time of our approach. The difference between the two is that the first uses the cross-product of all values between a certain range while the second uses the same number for all parameters and increases them (i.e. 1-1-1, 2-2-2 etc.)

#### Files

**main.py:**
Here you should select the testing algorithms you are interested in and run the application. Moreover, there are also extensive parameters availabe for selecting the problem and tuning the testing parameters.

**plotting_functions.py**
A collection of plotting functions used for the different testing algorithms.

**problem_generation.py**
A file containing code dealing with problems. Generation and methods interacting with them.

**testing_algorithms.py**
A collection of the different testing algorithms. Go here if you want to adapt or change any of them.

#### Output Files
In the two directories **results** and **tree_images** are the respective CSV outputs of the tests and the images of the tree. Both include some example files. When you want to use these files, you will have to open a python console and execute the plotting functions by yourself. This is useful if the data was generated, but the diagram generation failed for some reason.

### Core Functionality
This package contains the core functionality, like the LP definition or different tree-heuristics.

#### Files

**observation.py:**
Contains the observation class. A class used to save the results from a run.

**solver_node.py:**
Contains the main logic of the program. This includes the LP-problem definition and the methods needed to solve it.

**tree_generation.py:**
Here we define the different splitting stragegies. These heuristics are then evaluated in the automated testing.

**utils.py:**
Various methods including many debugging related printing functions. You can enable these by commenting them in within the solver_node.py file.

### Documentation
Various files from the project. Also including the paper.