import json
import argparse
import matplotlib.pyplot as plt
import sympy
import sympy.parsing.sympy_parser as sympy_parser
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
import sympy.utilities.lambdify as lambdify
import numpy

parser = argparse.ArgumentParser(description='Plot the cytometry histograms of a gate from a UCF.')
parser.add_argument('-u','--ucf',required=True,help='UCF file')
parser.add_argument('-1','--gate-1',required=True,dest='gate_1',help='first gate')
parser.add_argument('-2','--gate-2',required=True,dest='gate_2',help='second gate')
parser.add_argument('-o','--outfile',help='output file basename')
args = parser.parse_args()

with open(args.ucf,'r') as ucf_file:
    ucf = json.load(ucf_file)

class Gate:
    """Gate class."""

    def __init__(self,name,params,equation):
        self._name = name
        expr = sympy_parser.parse_expr(equation,transformations=sympy_parser.standard_transformations + (sympy_parser.convert_xor,),evaluate=False)
        expr = expr.subs(params)
        self._f = lambdify(expr.free_symbols,expr)

    @property
    def name(self):
        return self._name

    @property
    def f(self):
        return self._f

def get_params(params):
    p = {}
    for param in params:
        name = param['name']
        value = param['value']
        p[name] = value
    return p

for x in ucf:
    if x['collection'] == 'response_functions':
        params = get_params(x['parameters'])
        equation = x['equation']
        if x['gate_name'] == args.gate_1:
            gate_1 = Gate(args.gate_1,params,equation)
        elif x['gate_name'] == args.gate_2:
            gate_2 = Gate(args.gate_2,params,equation)

fig, ax = plt.subplots()
ax.set_xscale('log')
ax.set_yscale('log')

# ax.axis('equal')

x = numpy.logspace(-4,4)
y1 = gate_1.f(x)
y2 = gate_2.f(x)

plt.plot(x,y1,label=gate_1.name)
plt.plot(y2,x,label=gate_2.name)
ax.set_aspect('equal','box')
plt.legend()

plt.tight_layout()

out_file = args.outfile if args.outfile else gate_1.name + '_' + gate_2.name
plt.savefig(out_file + ".png",bbox_inches='tight')
