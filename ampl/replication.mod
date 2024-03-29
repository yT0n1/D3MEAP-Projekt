reset;

option solver gurobi;
option display_1col 0; #do not collaps matrixes on display
		
param Num_Fragments := 9;									
param Fragment_Size {i in 1..Num_Fragments} := Uniform(0,100);						
param Num_Queries := 9;
param Queries {f in 1..Num_Fragments, q in 1..Num_Queries} := round(Uniform(0,1));
display Queries;
param Query_Frequency {i in 1..Num_Queries} := Uniform(0,100);
param Query_Cost {i in 1..Num_Queries} := Uniform(0,100);
param Workload {i in 1..Num_Queries} := Query_Cost[i] *  Query_Frequency[i];
display Workload;
param Total_Worload := sum {Q in 1..Num_Queries} Workload[Q];
param Num_Nodes := 5;
param Num_Servers := Num_Nodes * 4;
param Servers_per_Node = Num_Servers / Num_Nodes;

var Location {fragment in 1..Num_Fragments, nodes in 1..Num_Nodes} binary;
var Runnable {query in 1..Num_Queries, nodes in 1..Num_Nodes}  binary; 
var Workshare {query in 1..Num_Queries, nodes in 1..Num_Nodes} >= 0; 
var epsilon;

minimize LP: (sum{F in 1..Num_Fragments, N in 1..Num_Nodes} (Location[F, N] * Fragment_Size[F])) + 1000 * epsilon;

#query mindestens auf einem system ausfuerbar
subject to NB1 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Runnable[Q,N] >= 1;

subject to NB2 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Workshare[Q,N] = 1;

#Each query has is runnable iff all their fragments are on a node // todo: do we need <= or would = also work?
subject to NB3 {N in 1..Num_Nodes, Q in 1..Num_Queries}: 
	Runnable[Q,N] * sum{f in 1..Num_Fragments} Queries[f, Q] <= sum{f in 1..Num_Fragments} Location[f, N] * Queries[f, Q];

subject to NB4 {N in 1..Num_Nodes, Q in 1..Num_Queries}:
	Workshare[Q, N] <= Runnable[Q, N];
	
subject to NB5 {N in 1..Num_Nodes}: sum{q in 1..Num_Queries} (Workshare[q, N] * Workload[q]) / Total_Worload = 1/Num_Nodes + epsilon; 

param work {n in 1..Num_Nodes};  


problem First_Cut: LP, Location, Runnable, Workshare, NB1, NB2, NB3, NB4, NB5;
solve First_Cut;

for { n in 1..Num_Nodes} {
	let work[n] := sum{q in 1..Num_Queries} Workshare[q, n] * Workload[q] / Total_Worload;
}
display work;
display LP; 
display Location;
display Runnable;
display Workshare; 

#end;
#### secondary splits

param this_node default 0;
# we reduce the number of queries which is critical to reduce complexity, however, we also need to give new names/numbers here
param Num_Queries_on_Node default 0; 

set node_queries default {};
set required_fragments default {};



var Location_Node {fragment in required_fragments, nodes in 1..Servers_per_Node} binary;
var Runnable_Node {query in node_queries, nodes in 1..Servers_per_Node}  binary; 
var Workshare_Node {query in node_queries, nodes in 1..Servers_per_Node} >= 0; 
var epsilon2;

minimize LP2: (sum{F in required_fragments, N in 1..Servers_per_Node} (Location_Node[F, N] * Fragment_Size[F])) + 1000 * epsilon2;

#jede uebrig gebliebene query mindestens auf einem system ausfuerbar
subject to NB1_1 {Q in node_queries}: sum{N in 1..Servers_per_Node} Runnable_Node[Q,N] >= 1;

subject to NB2_1 {Q in node_queries}: sum{N in 1..Servers_per_Node} Workshare_Node[Q,N] = 1;


subject to NB3_1 {N in 1..Servers_per_Node, Q in node_queries}: 
	Runnable_Node[Q,N] * sum{f in required_fragments} Queries[f, Q] <= sum{f in required_fragments} Location_Node[f, N] * Queries[f, Q];

subject to NB4_1 {N in 1..Servers_per_Node, Q in node_queries}:
	Workshare_Node[Q, N] <= Runnable_Node[Q, N];
	
subject to NB5_1 {N in 1..Servers_per_Node}: sum{q in node_queries} ((Workshare_Node[q, N] * Workload[q] * Workshare[q,this_node]) / (Total_Worload/Num_Nodes)) = 1/Servers_per_Node + epsilon2; 


problem Second_Cut: LP2, Location_Node, Runnable_Node, Workshare_Node, NB1_1, NB2_1, NB3_1, NB4_1, NB5_1;

param work2 {n in 1..Servers_per_Node};  


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
	
	for { n in 1..Servers_per_Node} {
		let work2[n] := sum{q in node_queries} Workshare_Node[q, n]* Workshare[q, this_node] * Workload[q] / (Total_Worload/Num_Nodes);
	}
	display work2; 
	
}

	
