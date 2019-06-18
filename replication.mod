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
param Num_Nodes := 4;

var Location {fragment in 1..Num_Fragments, nodes in 1..Num_Nodes} binary;
var Runnable {query in 1..Num_Queries, nodes in 1..Num_Nodes}  binary; 
var Workshare {query in 1..Num_Queries, nodes in 1..Num_Nodes} >= 0; 

minimize LP: sum{F in 1..Num_Fragments, N in 1..Num_Nodes} (Location[F, N] * Fragment_Size[F]);

#query mindestens auf einem system ausfuerbar
subject to NB1 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Runnable[Q,N] >= 1;

subject to NB2 {Q in 1..Num_Queries}: sum{N in 1..Num_Nodes} Workshare[Q,N] = 1;

#subject to NB3 {N in 1..Num_Nodes}: (sum{Q in 1..Num_Queries} Workshare[Q,N]) / Num_Queries = 1 / Num_Nodes;

subject to NB4 {N in 1..Num_Nodes, Q in 1..Num_Queries}: 
	Runnable[Q,N] * sum{f in 1..Num_Fragments} Queries[f, Q] <= sum{f in 1..Num_Fragments} Location[f, N] * Queries[f, Q];

subject to NB5 {N in 1..Num_Nodes, Q in 1..Num_Queries}:
	Workshare[Q, N] <= Runnable[Q, N];
	
subject to NB6 {N in 1..Num_Nodes}: sum{q in 1..Num_Queries} (Workshare[q, N] * Workload[q]) / Total_Worload = 1/Num_Nodes; 

solve;

param work {n in 1..Num_Nodes};  

solve;

for { n in 1..Num_Nodes} {
	let work[n] := sum{q in 1..Num_Queries} Workshare[q, n] * Workload[q] / Total_Worload;
}


display work;
display LP; 
display Location;
display Runnable;
display Workshare; 
