import matplotlib as mpl

from automated_testing.testing_algorithms import test_with_nodes, epsilon_pareto_front, timeout_tests, \
    timeout_vs_heuristic_tests, runtime_increasing_factors, runtime_increasing_factors_combined
from automated_testing.plotting_functions import plot_data_pareto, plot_data, plot_data_timeout, plot_heu_vs_opt
from automated_testing.problem_generation import generate_problems

mpl.rcParams['figure.dpi'] = 400


# What do you want to test?
test_node_count = False
test_pareto = False
test_timeout = True
compare_lp_heuristic = False
test_runtime_increasing_factors = False
test_runtime_increasing_factors_combined = False

# General Configuration for the Problems
num_problems = 2
min_fragments = 20
max_fragments = 50
min_queries = 11
max_queries = 12
num_workloads = 3

# Configuration Node Count
NODES_min_nodes = 2
NODES_max_nodes = 8
NODES_timeout = 10
NODES_epsilon_factor = 400000

# Configuration Pareto Frontier
PARETO_selected_node_count = 12
PARETO_timeout = 15
PARETO_epsilon_factor_array = [10, 100, 1000, 3000, 5000, 7500, 10000, 500000, 1000000]

# Configuration Timeout Behaviour
TIMEOUT_selected_node_count = 7
TIMEOUT_maximum_timeout = 30
TIMEOUT_should_squeeze = False
TIMEOUT_epsilon_factor = 3000000

problems = generate_problems(num_problems, min_fragments, max_fragments, min_queries,max_queries, num_workloads)

if test_node_count:
    total_results, df = test_with_nodes(problems,
                                        NODES_min_nodes,
                                        NODES_max_nodes,
                                        NODES_timeout,
                                        False,
                                        NODES_epsilon_factor)
    plot_data(df, NODES_min_nodes, NODES_max_nodes, problems, False)
    df.to_csv("test_node_out_No_Epsilon.csv")
    total_results, df = test_with_nodes(problems,
                                        NODES_min_nodes,
                                        NODES_max_nodes,
                                        NODES_timeout,
                                        True,
                                        NODES_epsilon_factor)
    plot_data(df, NODES_min_nodes, NODES_max_nodes, problems, True)
    df.to_csv("test_node_out_Epsilon.csv")

if test_pareto:
    pareto_results, df = epsilon_pareto_front(problems,
                                              PARETO_selected_node_count,
                                              PARETO_timeout,
                                              PARETO_epsilon_factor_array)
    plot_data_pareto(df)
    df.to_csv("data_pareto_out.csv")

if test_timeout:
    timeout_results, df = timeout_tests(problems,
                                        TIMEOUT_selected_node_count,
                                        TIMEOUT_maximum_timeout,
                                        TIMEOUT_should_squeeze,
                                        TIMEOUT_epsilon_factor)
    plot_data_timeout(df)
    df.to_csv("test_timeout_out.csv")

if compare_lp_heuristic:
    compare_res, df = timeout_vs_heuristic_tests(problems,
                                                 NODES_min_nodes,
                                                 NODES_max_nodes,
                                                 False)
    df.to_csv("test_heu_out_nosqueez.csv")
    plot_heu_vs_opt(df, NODES_min_nodes, NODES_max_nodes, problems, False)

    compare_res, df = timeout_vs_heuristic_tests(problems,
                                                 NODES_min_nodes,
                                                 NODES_max_nodes,
                                                 True, NODES_epsilon_factor)
    df.to_csv("test_heu_out_squeez.csv")
    plot_heu_vs_opt(df, NODES_min_nodes, NODES_max_nodes, problems, True)

if test_runtime_increasing_factors:
    df = runtime_increasing_factors()
    df.to_csv("test_runtime_increasing_factors.csv")

if test_runtime_increasing_factors_combined:
    df = runtime_increasing_factors_combined()
    df.to_csv("runtime_increasing_factors_combined.csv")
