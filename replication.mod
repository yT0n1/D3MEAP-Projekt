reset;

option solver cplex;
		
param Num_Fragments := 10;									
param Fragment_Size {i in 1..Num_Fragments} := Uniform(0,100);						
param Num_Queries := 9; #nope menge an columns
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

	param this_node := 1;
	# we reduce the number of queries which is critical to reduce complexity, however, we also need to give new names/numbers here
	param Num_Queries_on_Node default 0; 
	for {Q in 1..Num_Queries} let Num_Queries_on_Node :=  Num_Queries_on_Node + Runnable[Q, this_node];
	display Num_Queries_on_Node;
	
	param Mapping {n in 1..Num_Queries};
	for {q in 2..Num_Queries_on_Node} {
		
		for {q_old in 1..Num_Queries}{
			let Mapping[1]  := if Runnable[q_old, this_node] then q_old;
			let Mapping[q]  := if Runnable[q_old, this_node]  and q_old < Mapping[q-1] then q_old;
		}
	}
		
	display Mapping;
	
	var Location_Node {fragment in 1..Num_Fragments, nodes in 1..Servers_per_Node} binary;
	var Runnable_Node {query in 1..Num_Queries_on_Node, nodes in 1..Servers_per_Node}  binary; 
	var Workshare_Node {query in 1..Num_Queries_on_Node, nodes in 1..Servers_per_Node} >= 0; 
	
	minimize LP2: sum{F in 1..Num_Fragments, N in 1..Servers_per_Node} (Location_Node[F, N] * Fragment_Size[F]);
	
	#jede uebrig gebliebene query mindestens auf einem system ausfuerbar
	subject to NB1_1 {Q in 1..Num_Queries_on_Node}: sum{N in 1..Servers_per_Node} Runnable_Node[Q,N] >= 1;
	
	#Todo: workshare needs to be reconfigurated?
	subject to NB2_1 {Q in 1..Num_Queries_on_Node}: sum{N in 1..Servers_per_Node} Workshare_Node[Q,N] = 1;
	
	
	subject to NB4_1 {N in 1..Servers_per_Node, Q in 1..Num_Queries_on_Node}: 
		Runnable_Node[Q,N] * sum{f in 1..Num_Fragments} Queries[f, Mapping[Q]] <= sum{f in 1..Num_Fragments} Location_Node[f, N] * Queries[f, Mapping[Q]];
	
	subject to NB5_1 {N in 1..Servers_per_Node, Q in 1..Num_Queries_on_Node}:
		Workshare_Node[Q, N] <= Runnable_Node[Q, N];
		
	subject to NB6_1 {N in 1..Servers_per_Node}: sum{q in 1..Num_Queries_on_Node} (Workshare_Node[q, N] * Workload[Mapping[q]] * Workshare[Mapping[q],this_node]) / (Total_Worload/Num_Nodes) = 1/Servers_per_Node; 
	objective LP2;
	solve;
