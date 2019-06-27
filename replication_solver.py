from typing import List

from amplpy import AMPL, Environment, DataFrame


def main():
    ampl = AMPL(Environment('./../amplide.macosx64/amplide.macosx64'))
    #ampl = AMPL(Environment('../ampl/'))
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
    #ampl.getParameter('Queries').setValues([[1,1,1,0],[0,1,1,0],[0,1,0,1], [1,1,1,1], [1,1,1,1]])
    ampl.getParameter('Query_Frequency').setValues([6,1,0.5,2,10])
    ampl.getParameter('Query_Cost').setValues([10, 20, 20, 5, 20])
    ampl.getParameter('Num_Nodes').setValues([2])
    ampl.getParameter('Number_of_Children').setValues([2])

    df = DataFrame(('fragment', 'query'), ('needs'))
    df.setColumn('fragment', [1,1,1,1,1,2,2,2,2,2,3,3,3,3,3,4,4,4,4,4])
    df.setColumn('query', [1,2,3,4,5] * 4)
    df.setColumn('needs', [1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,1])
    print(df)
    ampl.getParameter('Queries').setValues(df)
    print(ampl.getOutput('display Queries;'))

    ampl.solve()
    print(ampl.getOutput('display LP2;'))
    print(ampl.getOutput('display Queries;'))
    print(ampl.getOutput('display Fragment_Size;'))
    print(ampl.getOutput('display Query_Frequency;'))
    print(ampl.getOutput('display Query_Cost;'))
    print(ampl.getOutput('display Runnable_Node;'))
    print(ampl.getOutput('display Workshare_Node;'))
    print(ampl.getOutput('display node_queries;'))
    print(ampl.getOutput('display required_fragments;'))
    runnable = ampl.getVariable('Runnable_Node')


    print('hi')




if __name__ == '__main__':
    main()