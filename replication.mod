reset;

option solver cplex;
option display_1col 0;
		
param Num_Fragments := 10;									
param Fragment_Size {i in 1..Num_Fragments} := Uniform(0,100);						
param Num_Queries := 9;
param Queries {f in 1..Num_Fragments, q in 1..Num_Queries} := round(Uniform(0,1));
display Queries;
param Query_Frequency {i in 1..Num_Queries} := Uniform(0,100);
param Query_Cost {i in 1..Num_Queries} := Uniform(0,100);
param Workload {i in 1..Num_Queries} := Query_Cost[i] *  Query_Frequency[i];
param Total_Worload := sum {Q in 1..Num_Queries} Workload[Q];
param Num_Nodes := 3;
param Num_Servers := Num_Nodes * 3;
param Servers_per_Node = Num_Servers / Num_Nodes;

var Location {fragment in 1..Num_Fragments, nodes in 1..Num_Nodes} binary;
var Runnable {query in 1..Num_Queries, nodes in 1..Num_Nodes}  binary; 
var Workshare {query in 1..Num_Queries, nodes in 1..Num_Nodes} >= 0; 

minimize LP: sum{F in 1..Num_Fragments, N in 1..Num_Nodes} (Location[F, N] * Fragment_Size[F]);

#query mindestens auf einem system ausfuerbar
subject to NB1 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Runnable[Q,N] >= 1;

subject to NB2 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Workshare[Q,N] = 1;

#subject to NB3 {N in 1..Num_Nodes}: (sum{Q in 1..Num_Queries} Workshare[Q,N]) / Num_Queries = 1 / Num_Nodes;

#Each query has is runnable iff all their fragments are on a node // todo: do we need <= or would = also work?
subject to NB4 {N in 1..Num_Nodes, Q in 1..Num_Queries}: 
	Runnable[Q,N] * sum{f in 1..Num_Fragments} Queries[f, Q] <= sum{f in 1..Num_Fragments} Location[f, N] * Queries[f, Q];

subject to NB5 {N in 1..Num_Nodes, Q in 1..Num_Queries}:
	Workshare[Q, N] <= Runnable[Q, N];
	
subject to NB6 {N in 1..Num_Nodes}: sum{q in 1..Num_Queries} (Workshare[q, N] * Workload[q]) / Total_Worload = 1/Num_Nodes; 

solve;

param work {n in 1..Num_Nodes};  

for { n in 1..Num_Nodes} {
	let work[n] := sum{q in 1..Num_Queries} Workshare[q, n] * Workload[q] / Total_Worload;
}


display work;
display LP; 
display Location;
display Runnable;
display Workshare; 


#### second split

param nodes_workshare {query in 1..Num_Queries, nodes in 1..Num_Nodes};  

for {q in 1..Num_Queries, n in 1..Num_Nodes} {
	let nodes_workshare[q, n] := Workshare[q,n]
}

param this_node := 1;
# we reduce the number of queries which is critical to reduce complexity, however, we also need to give new names/numbers here
param Num_Queries_on_Node default 0; 
for {Q in 1..Num_Queries} let Num_Queries_on_Node :=  Num_Queries_on_Node + Runnable[Q, this_node];
display Num_Queries_on_Node;
set node_queries default {};
for {q in 1..Num_Queries} let node_queries := if Runnable[q, this_node] then node_queries union {q} else node_queries;
display node_queries;


var Location_Node {fragment in 1..Num_Fragments, nodes in 1..Servers_per_Node} binary;
var Runnable_Node {query in node_queries, nodes in 1..Servers_per_Node}  binary; 
var Workshare_Node {query in node_queries, nodes in 1..Servers_per_Node} >= 0; 

minimize LP2: sum{F in 1..Num_Fragments, N in 1..Servers_per_Node} (Location_Node[F, N] * Fragment_Size[F]);

#jede uebrig gebliebene query mindestens auf einem system ausfuerbar
subject to NB1_1 {Q in node_queries}: sum{N in 1..Servers_per_Node} Runnable_Node[Q,N] >= 1;

#Todo: workshare needs to be reconfigurated?
subject to NB2_1 {Q in node_queries}: sum{N in 1..Servers_per_Node} Workshare_Node[Q,N] = 1;


subject to NB4_1 {N in 1..Servers_per_Node, Q in node_queries}: 
	Runnable_Node[Q,N] * sum{f in 1..Num_Fragments} Queries[f, Q] <= sum{f in 1..Num_Fragments} Location_Node[f, N] * Queries[f, Q];

subject to NB5_1 {N in 1..Servers_per_Node, Q in node_queries}:
	Workshare_Node[Q, N] <= Runnable_Node[Q, N];
	
subject to NB6_1 {N in 1..Servers_per_Node}: sum{q in node_queries} ((Workshare_Node[q, N] * Workload[q] * nodes_workshare[q,this_node]) / (Total_Worload/Num_Nodes)) = 1/Servers_per_Node; 
objective LP2;
solve;
display LP2; 
display Location_Node;
display Runnable_Node;
display Workshare_Node; 
display nodes_workshare;
param work2 {n in 1..Num_Nodes};  

for { n in 1..Servers_per_Node} {
	let work2[n] := sum{q in node_queries} Workshare_Node[q, n]* nodes_workshare[q, this_node] * Workload[q] / (Total_Worload/Num_Nodes);
}


display work2;
	
