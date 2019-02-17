from glob import glob
import json
import argparse
import os

__author__  = 'Timothy S. Jones <jonests@bu.edu>, Densmore Lab, BU'
__license__ = 'GPL3'


parser = argparse.ArgumentParser(description='Build a JSON file containing all the parameters of all the stages of an application.')
parser.add_argument('-d','--directory',required=True,help='the Cello2 directory')
parser.add_argument('-a','--application',required=True,help='application')
parser.add_argument('-o','--outfile',help='output file')
args = parser.parse_args()

app_config_file = os.path.join(args.directory,"cello2","cello2-" + args.application,"src","non-packaged-resources","Configuration.json")

with open(app_config_file,"r") as config_json:
    config = json.load(config_json)

stages = [x["name"].lower() for x in config["stages"]]

params = {}

for stage in stages:
    params[stage] = {}
    path = os.path.join(args.directory,"cello2","cello2-" + stage,"src","non-packaged-resources","algorithms")
    algorithms = glob(os.path.join(path,"*"))
    for algorithm in algorithms:
        base = os.path.basename(algorithm)
        alg_param_file = os.path.join(algorithm,base + ".json")
        with open(alg_param_file,"r") as param_json:
            param = json.load(param_json)
            params[stage][base] = param

print(json.dumps(params,indent=2))
