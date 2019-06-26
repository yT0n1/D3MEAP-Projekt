from amplpy import AMPL, Environment


def main():
    ampl = AMPL(Environment('./../amplide.macosx64/amplide.macosx64'))
    ampl.read('replication_function.mod')
    """
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
    """


    ampl.getSet('node_queries').setValues([1,2,3,4,5])
    ampl.getSet('required_fragments').setValues([1,2,3,4])
    ampl.getParameter('Fragment_Size').setValues([1,1,2,3])
    ampl.getParameter('Queries').setValues([[1,1,1,0],[0,1,1,0],[0,1,0,1], [1,1,1,1], [1,1,1,1]])
    ampl.getParameter('Query_Frequency').setValues([6,1,0.5,2])
    ampl.getParameter('Query_Cost').setValues([10, 20, 20, 5])
    ampl.getParameter('Num_Nodes').setValues(3)
    ampl.getParameter('Number_of_Children').setValues(2)



    ampl.solve()



if __name__ == '__main__':
    main()