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

stages = [x["name"] for x in config["stages"]]

root = {}
params = []
application = {"name":config["name"],"stages":params}
applications = [application,]
root['applications'] = applications

for stage in stages:
    stage_params = {}
    stage_params["name"] = stage
    stage_params["algorithms"] = []
    params.append(stage_params)
    
    path = os.path.join(args.directory,"cello2","cello2-" + stage.lower(),"src","non-packaged-resources","algorithms")
    algorithms = glob(os.path.join(path,"*"))
    for algorithm in algorithms:
        base = os.path.basename(algorithm)
        alg_param_file = os.path.join(algorithm,base + ".json")
        with open(alg_param_file,"r") as param_json:
            algorithm_params = json.load(param_json)
            stage_params["algorithms"].append(algorithm_params)
        

print(json.dumps(root,indent=2))
