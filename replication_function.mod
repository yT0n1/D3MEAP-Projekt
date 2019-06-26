
reset;

option solver gurobi;
option display_1col 0; 


# we reduce the number of queries which is critical to reduce complexity, however, we also need to give new names/numbers here
param Num_Queries_on_Node default 0; 
set node_queries default {};
set required_fragments default {};


param Fragment_Size {required_fragments};	
param Queries { required_fragments , node_queries} binary; 					



param Query_Frequency {node_queries};
param Query_Cost {node_queries};
param Workload {q in node_queries} := Query_Cost[q] *  Query_Frequency[q];
param Total_Workload := sum {q in node_queries} Workload[q];

param Num_Nodes default 0;
param Number_of_Children default 0;




var Location_Node {fragment in required_fragments, nodes in 1..Number_of_Children} binary;
var Runnable_Node {query in node_queries, nodes in 1..Number_of_Children}  binary; 
var Workshare_Node {query in node_queries, nodes in 1..Number_of_Children} >= 0; 

minimize LP2: sum{F in required_fragments, N in 1..Number_of_Children} 
	(Location_Node[F, N] * Fragment_Size[F]);

#jede uebrig gebliebene query mindestens auf einem system ausfuerbar
subject to NB1_1 {Q in node_queries}: sum{N in 1..Number_of_Children} Runnable_Node[Q,N] >= 1;

subject to NB2_1 {Q in node_queries}: sum{N in 1..Number_of_Children} Workshare_Node[Q,N] = 1;


subject to NB3_1 {N in 1..Number_of_Children, Q in node_queries}: 
	Runnable_Node[Q,N] * sum{f in required_fragments} Queries[f, Q] <= 
	sum{f in required_fragments} Location_Node[f, N] * Queries[f, Q];

subject to NB4_1 {N in 1..Number_of_Children, Q in node_queries}:
	Workshare_Node[Q, N] <= Runnable_Node[Q, N];
	
subject to NB5_1 {N in 1..Number_of_Children}: 
	sum{q in node_queries} ((Workshare_Node[q, N] * Workload[q]) / (Total_Workload/Num_Nodes)) = 1/Number_of_Children; 


problem Second_Cut: LP2, Location_Node, Runnable_Node, Workshare_Node, NB1_1, NB2_1, NB3_1, NB4_1, NB5_1;

param work2 {n in 1..Number_of_Children};  

solve Second_Cut;

display LP2; 
display Location_Node;
display Runnable_Node;
display Workshare_Node; 

