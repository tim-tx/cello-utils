import json
import numpy as np
import matplotlib.pyplot as plt
import pycello2.ucf

import argparse

parser = argparse.ArgumentParser(
    description='Plot some latch combinations in a triangle.'
)
parser.add_argument(
    '-u', '--ucf', type=str,
    required=True, help='The UCF file.'
)
parser.add_argument(
    '-g', '--gates', type=str,
    required=False, help='The comma-separated list of gates.'
)
parser.add_argument(
    '-o', '--output', type=str,
    required=False, help='The output file name.'
)

args = parser.parse_args()

with open(args.ucf, 'r') as ucf_file:
    ucf_json = json.load(ucf_file)

ucf = pycello2.ucf.UCF(ucf_json)

gates = []
if args.gates:
    gate_names = [gate.lstrip() for gate in args.gates.split(',')]
    for gate in ucf.gates:
        if gate.name in gate_names:
            gates.append(gate)
else:
    for gate in ucf.gates:
        if isinstance(gate, pycello2.ucf.InputSensor):
            continue
        if isinstance(gate, pycello2.ucf.OutputReporter):
            continue
        gates.append(gate)

s = len(gates) - 1

fig, axes = plt.subplots(s, s, sharex=True, sharey=True)

x = np.logspace(-3, 2)


def func(row):
    ymin = row['ymin']
    ymax = row['ymax']
    K = row['K']
    n = row['n']
    y = ymin+(ymax-ymin)/(1.0+(x/K)**n)
    return y


color1 = 'blue'
color2 = 'red'

for i in range(s):
    for j in range(i+1):
        ax = axes[i, j]

        idx1 = j
        idx2 = i+1

        if gates[idx1].group == gates[idx2].group:
            ax = axes[i, j]
            ax.axis('off')
            continue

        func1 = func(gates[idx1].parameters)
        func2 = func(gates[idx2].parameters)
        ax.loglog(func1, x, label=gates[idx1].name, color=color1)
        ax.loglog(x, func2, label=gates[idx2].name, color=color2)
        ax.set_aspect('equal')

        if (i == s-1):
            ax.set_xlabel(gates[idx1].name, color=color1)
        else:
            ax.xaxis.set_ticks_position('none')

        if (j == 0):
            ax.set_ylabel(gates[idx2].name, color=color2)
        else:
            ax.yaxis.set_ticks_position('none')
    for j in range(i+1, s):
        ax = axes[i, j]
        ax.axis('off')

fig.set_size_inches(s, s)
plt.tight_layout(pad=0.1)

out_file = 'latch-triangle' if not args.output else args.output

plt.savefig(out_file + '.png', bbox_to_inches='tight')
