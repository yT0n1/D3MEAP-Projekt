
reset;

option solver gurobi;
option display_1col 0; 


param this_node;
# we reduce the number of queries which is critical to reduce complexity, however, we also need to give new names/numbers here
param Num_Queries_on_Node default 0; 
param Num_Fragments default 0;
set Fragment_Size default {};						

set node_queries default {};
set required_fragments default {};

set Query_Frequency default {};
set Query_Cost default {};
set Workload default {};
param Total_Worload default 0;
param Num_Nodes default 0;
param Number_of_Children default 0;




var Location_Node {fragment in required_fragments, nodes in 1..Number_of_Children} binary;
var Runnable_Node {query in node_queries, nodes in 1..Number_of_Children}  binary; 
var Workshare_Node {query in node_queries, nodes in 1..Number_of_Children} >= 0; 

minimize LP2: sum{F in required_fragments, N in 1..Number_of_Children} (Location_Node[F, N] * Fragment_Size[F]);

#jede uebrig gebliebene query mindestens auf einem system ausfuerbar
subject to NB1_1 {Q in node_queries}: sum{N in 1..Number_of_Children} Runnable_Node[Q,N] >= 1;

subject to NB2_1 {Q in node_queries}: sum{N in 1..Number_of_Children} Workshare_Node[Q,N] = 1;


subject to NB3_1 {N in 1..Number_of_Children, Q in node_queries}: 
	Runnable_Node[Q,N] * sum{f in required_fragments} Queries[f, Q] <= sum{f in required_fragments} Location_Node[f, N] * Queries[f, Q];

subject to NB4_1 {N in 1..Number_of_Children, Q in node_queries}:
	Workshare_Node[Q, N] <= Runnable_Node[Q, N];
	
subject to NB5_1 {N in 1..Number_of_Children}: sum{q in node_queries} ((Workshare_Node[q, N] * Workload[q] * Workshare[q,this_node]) / (Total_Worload/Num_Nodes)) = 1/Number_of_Children; 


problem Second_Cut: LP2, Location_Node, Runnable_Node, Workshare_Node, NB1_1, NB2_1, NB3_1, NB4_1, NB5_1;

param work2 {n in 1..Number_of_Children};  

for {i in 1..Num_Nodes}{
	let this_node := i;
	display this_node;
	for {Q in 1..Num_Queries} let Num_Queries_on_Node :=  Num_Queries_on_Node + Runnable[Q, this_node];
	display Num_Queries_on_Node;
	for {q in 1..Num_Queries} let node_queries := if Runnable[q, this_node] then node_queries union {q} else node_queries;
	display node_queries;
	for{f in 1..Num_Fragments, q in node_queries} let required_fragments := if Queries[f,q] = 1 then required_fragments union {f} else required_fragments;
	display required_fragments;
	solve Second_Cut;

	display LP2; 
	display Location_Node;
	display Runnable_Node;
	display Workshare_Node; 
	
	for { n in 1..Number_of_Children} {
		let work2[n] := sum{q in node_queries} Workshare_Node[q, n]* Workshare[q, this_node] * Workload[q] / (Total_Worload/Num_Nodes);
	}
	display work2; 
	
}