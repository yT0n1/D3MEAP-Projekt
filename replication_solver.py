from amplpy import AMPL, Environment


def main():
    ampl = AMPL(Environment('./../amplide.macosx64/amplide.macosx64'))
    ampl.read('replication_function.mod')
    this_node = ampl.getParameter('this_node')
    this_node.setValues(0)

    ampl.solve()



if __name__ == '__main__':
    main()