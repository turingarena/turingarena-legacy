import sys
from interfaces.exampleinterface import exampleinterface
from taskwizard.module import supervisor

if supervisor.has_supervisor():
    supervisor.init()

    solution_process = supervisor.algorithm_create_process("solution")
    solution_process.start()

    iface = exampleinterface(solution_process.upward_pipe, solution_process.downward_pipe)
else:
    iface = exampleinterface(sys.stdin, sys.stdout)

iface._callbacks["test"] = lambda a, b: a+b

iface.N = 10
iface.M = 100
iface.A.alloc(1, iface.N)

for i in range(1, 1+iface.N):
    iface.A[i] = i*i

S = iface.solve(3)

print("Answer:", S, file=sys.stderr)

if supervisor.has_supervisor():
    solution_process.stop()
