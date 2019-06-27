from amplpy import *

ampl = AMPL(Environment('../ampl/'))
ampl.read('./replication.mod')
ampl.getParameter('test')
ampl.solve()

print(ampl.getObjective('LP').value())