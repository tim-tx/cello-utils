import json
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot the cytometry histograms of a gate from a UCF.')
parser.add_argument('-u','--ucf',required=True,help='UCF file')
parser.add_argument('-g','--gate',required=True,help='gate')
parser.add_argument('-o','--outfile',help='output file basename')
args = parser.parse_args()

with open(args.ucf,'r') as ucf_file:
    ucf = json.load(ucf_file)

cytometry = {}

for x in ucf:
    if x['collection'] == 'gate_cytometry':
         if x['gate_name'] == args.gate:
             for data in x['cytometry_data']:
                 cytometry[data['input']] = {'bins'  : data['output_bins'],
                                             'counts': data['output_counts']}
         else:
             pass

fig, ax = plt.subplots(len(cytometry),1,sharex=True)

for i,key in enumerate(sorted(cytometry.keys())):
    ax[i].bar(cytometry[key]['bins'],cytometry[key]['counts'])
    ax[i].text(0.85,0.5,key,ha='left',va='center',transform=ax[i].transAxes)
    ax[i].set_xscale('log')
    ax[i].set_yticklabels([])
    if i == len(cytometry) - 1:
        axis = "y"
    else:
        axis = "both"
    ax[i].tick_params(axis=axis,
                      which='both',
                      bottom=False,
                      top=False,
                      right=False,
                      left=False,
                      labelleft=False)

plt.subplots_adjust(hspace=0)
# plt.tight_layout()

out_file = args.outfile if args.outfile else args.gate
plt.savefig(out_file + ".png",bbox_inches='tight')
