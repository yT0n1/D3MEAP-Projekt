from amplpy import AMPL, Environment


def main():
    #ampl = AMPL(Environment('./../amplide.macosx64/amplide.macosx64'))
    ampl = AMPL(Environment('../ampl/'))
    ampl.read('replication_function.mod')
    """
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
    """

    a = ampl.getParameters()


    ampl.solve()



if __name__ == '__main__':
    main()