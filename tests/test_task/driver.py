import sys
from interfaces.exampleinterface import exampleinterface
from taskwizard.module import supervisor

supervisor.init()

solution_process = supervisor.algorithm_create_process("solution")

solution_process.start()

iface = exampleinterface(solution_process.upward_pipe, solution_process.downward_pipe)

iface.N = 10
iface.M = 100
iface.A.alloc(1, 100)

for i in range(1, 1+100):
    iface.A[i] = i*i

S = iface.solve(3)

print("Answer:", S, file=sys.stderr)

solution_process.stop()