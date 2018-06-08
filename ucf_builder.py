import csv
import json
import argparse

__author__  = 'Timothy S. Jones <jonests@bu.edu>, Densmore Lab, BU'
__license__ = 'GPL3'

def add_gate_parts(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_GATE_NAME = "gate_name"
    S_CSV_PROMOTER = "promoter"
    S_CSV_VARIABLE = "variable"
    S_CSV_PART = "part"

    S_CASSETTES = "cassettes"

    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys = {S_CASSETTES:[]}

    expected = set([S_CSV_GATE_NAME,S_CSV_PROMOTER,S_CSV_VARIABLE])
    variable = ""
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_GATE_NAME:
                header_keys[S_CSV_GATE_NAME] = i
                expected.remove(S_CSV_GATE_NAME)
            elif key == S_CSV_PROMOTER:
                header_keys[S_CSV_PROMOTER] = i
                expected.remove(S_CSV_PROMOTER)
            elif key == S_CSV_VARIABLE:
                cassette = {S_CSV_VARIABLE:i,S_CSV_PART:[]}
                header_keys[S_CASSETTES].append(cassette)
                expected.add(S_CSV_PART)
            elif key == S_CSV_PART:
                cassette = header_keys[S_CASSETTES][-1]
                cassette[S_CSV_PART].append(i)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    # if S_CSV_GATE_NAME not in header_keys:
    #     raise RuntimeError("'%s' required in header." % (S_CSV_GATE_NAME))
    # if S_CSV_PROMOTER not in header_keys:
    #     raise RuntimeError("'%s' required in header." % (S_CSV_PROMOTER))
    # if S_CASSETTES not in header_keys:
    #     raise RuntimeError("At least one '%s' required in header." % (S_CSV_VARIABLE))

    gate_parts = []

    for row in reader:
        if len(row) > 0:
            collection = {}

            #############################
            # find or create collection #
            #############################
            name = row[header_keys[S_CSV_GATE_NAME]]
            if len(name) == 0:
                raise RuntimeError("Gate name not specified.")
            else:
                for c in gate_parts:
                    if c['gate_name'] == name:
                        collection = c

                if len(collection) == 0:
                    collection['collection'] = 'gate_parts'
                    collection['gate_name'] = name
                    gate_parts.append(collection)
                else:
                    raise RuntimeError("Cassettes already specified for '%s'." % name)

            ##################
            # cassette parts #
            ##################
            cassette_specs = header_keys[S_CASSETTES]
            for spec in cassette_specs:
                variable = row[spec[S_CSV_VARIABLE]]
            
                if len(variable) == 0:
                    continue
                else:
                    cassettes = []
                    cassette = {}
                    if 'expression_cassettes' in collection:
                        cassettes = collection['expression_cassettes']
                        for c in cassettes:
                            if 'maps_to_variable' in c and c['maps_to_variable'] == variable:
                                cassette = c
                                raise RuntimeWarning("Variable %s already added to this gate. Skipping." % variable)

                        if len(cassette) > 0:
                            continue
                    else:
                         collection['expression_cassettes'] = cassettes   

                    cassette['maps_to_variable'] = variable
                    parts = []
                    if spec[S_CSV_PART] == 0:
                        raise RuntimeWarning("No parts specified for %s, variable %s." % (name,variable))
                    else:
                        for i in spec[S_CSV_PART]:
                            if len(row[i]) > 0:
                                parts.append(row[i])
                        cassette['cassette_parts'] = parts
                    cassettes.append(cassette)

            ############
            # promoter #
            ############
            collection['promoter'] = row[header_keys[S_CSV_PROMOTER]]

    ucf += gate_parts
    return ucf

def add_response_functions(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_GATE_NAME = "gate_name"
    S_CSV_EQUATION = "equation"
    S_CSV_VARIABLE_NAME = "variable_name"
    S_CSV_OFF_THRESHOLD = "off_threshold"
    S_CSV_ON_THRESHOLD = "on_threshold"
    S_CSV_PARAMETER_NAME = "parameter_name"
    S_CSV_PARAMETER_VALUE = "value"
    
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = "collection"
    S_UCF_RESPONSE_FUNCTIONS = "response_functions"
    S_UCF_GATE_NAME = "gate_name"
    S_UCF_EQUATION = "equation"
    S_UCF_VARIABLES = "variables"
    S_UCF_PARAMETERS = "parameters"
    S_UCF_VARIABLE_NAME = "name"
    S_UCF_OFF_THRESHOLD = "off_threshold"
    S_UCF_ON_THRESHOLD = "on_threshold"
    S_UCF_PARAMETER_NAME = "name"
    S_UCF_PARAMETER_VALUE = "value"
    
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {S_UCF_VARIABLES:[],S_UCF_PARAMETERS:[]}

    expected = set([S_CSV_GATE_NAME,
                    S_CSV_EQUATION,
                    S_CSV_VARIABLE_NAME,
                    S_CSV_PARAMETER_NAME])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_GATE_NAME:
                header_keys_map[S_UCF_GATE_NAME] = i
                expected.remove(S_CSV_GATE_NAME)
                for s in [S_CSV_PARAMETER_VALUE,S_CSV_OFF_THRESHOLD,S_CSV_ON_THRESHOLD]:
                    if s in expected:
                        expected.remove(s)
            elif key == S_CSV_EQUATION:
                header_keys_map[S_UCF_EQUATION] = i
                expected.remove(S_CSV_EQUATION)
                for s in [S_CSV_PARAMETER_VALUE,S_CSV_OFF_THRESHOLD,S_CSV_ON_THRESHOLD]:
                    if s in expected:
                        expected.remove(s)
            elif key == S_CSV_VARIABLE_NAME:
                header_keys_map[S_UCF_VARIABLES].append({S_UCF_VARIABLE_NAME:i})
                expected.add(S_CSV_OFF_THRESHOLD)
                expected.add(S_CSV_ON_THRESHOLD)
                if S_CSV_PARAMETER_VALUE in expected:
                    expected.remove(S_CSV_PARAMETER_VALUE)
            elif key == S_CSV_OFF_THRESHOLD:
                variable = header_keys_map[S_UCF_VARIABLES][-1]
                variable[S_UCF_OFF_THRESHOLD] = i
                expected.remove(S_CSV_OFF_THRESHOLD)
            elif key == S_CSV_ON_THRESHOLD:
                variable = header_keys_map[S_UCF_VARIABLES][-1]
                variable[S_UCF_ON_THRESHOLD] = i
                expected.remove(S_CSV_ON_THRESHOLD)
            elif key == S_CSV_PARAMETER_NAME:
                header_keys_map[S_UCF_PARAMETERS].append({S_UCF_PARAMETER_NAME:i})
                expected.add(S_CSV_PARAMETER_VALUE)
            elif key == S_CSV_PARAMETER_VALUE:
                parameter = header_keys_map[S_UCF_PARAMETERS][-1]
                parameter[S_UCF_PARAMETER_VALUE] = i
                expected.remove(S_CSV_PARAMETER_VALUE)
                
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    response_functions = []

    for row in reader:
        if len(row) > 0:
            collection = {}

            #############################
            # find or create collection #
            #############################
            name = row[header_keys_map[S_UCF_GATE_NAME]]
            if len(name) == 0:
                raise RuntimeError("Gate name not specified.")
            else:
                for c in response_functions:
                    if c[S_UCF_GATE_NAME] == name:
                        raise RuntimeError("Response function already specified for '%s'." % name)

                collection[S_UCF_COLLECTION] = S_UCF_RESPONSE_FUNCTIONS
                collection[S_UCF_GATE_NAME] = name
                response_functions.append(collection)

            ############
            # equation #
            ############
            collection[S_UCF_EQUATION] = row[header_keys_map[S_UCF_EQUATION]]

            #############
            # variables #
            #############
            variable_specs = header_keys_map[S_UCF_VARIABLES]
            variables = []
            for spec in variable_specs:
                variable = row[spec[S_UCF_VARIABLE_NAME]]
                
                if len(variable) == 0:
                    continue

                off_threshold = row[spec[S_UCF_OFF_THRESHOLD]]
                on_threshold = row[spec[S_UCF_ON_THRESHOLD]]
                if len(off_threshold) == 0:
                    raise RuntimeError("No %s specified for variable '%s'." % (S_CSV_OFF_THRESHOLD,variable))
                if len(on_threshold) == 0:
                    raise RuntimeError("No %s specified for variable '%s'." % (S_CSV_ON_THRESHOLD,variable))
                variables.append({S_UCF_VARIABLE_NAME:variable,
                                  S_UCF_OFF_THRESHOLD:float(off_threshold),
                                  S_UCF_ON_THRESHOLD:float(on_threshold)})

            collection[S_UCF_VARIABLES] = variables

            ##############
            # parameters #
            ##############
            parameter_specs = header_keys_map[S_UCF_PARAMETERS]
            parameters = []
            for spec in parameter_specs:
                parameter = row[spec[S_UCF_PARAMETER_NAME]]
                
                if len(parameter) == 0:
                    continue

                value = row[spec[S_UCF_PARAMETER_VALUE]]
                if len(value) == 0:
                    raise RuntimeError("No %s specified for parameter '%s'." % (S_CSV_PARAMETER_VALUE,parameter))
                parameters.append({S_UCF_PARAMETER_NAME:parameter,
                                  S_UCF_PARAMETER_VALUE:float(value)})

            collection[S_UCF_PARAMETERS] = parameters
            
    ucf += response_functions
    return ucf

def add_parts(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_PART_NAME = "name"
    S_CSV_PART_TYPE = "type"
    S_CSV_PART_DNASEQUENCE = "dnasequence"
        
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = "collection"
    S_UCF_PARTS = "parts"
    S_UCF_PART_NAME = "name"
    S_UCF_PART_TYPE = "type"
    S_UCF_PART_DNASEQUENCE = "dnasequence"
    
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {}

    expected = set([S_CSV_PART_NAME,
                    S_CSV_PART_TYPE,
                    S_CSV_PART_DNASEQUENCE])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_PART_NAME:
                header_keys_map[S_UCF_PART_NAME] = i
                expected.remove(S_CSV_PART_NAME)
            elif key == S_CSV_PART_TYPE:
                header_keys_map[S_UCF_PART_TYPE] = i
                expected.remove(S_CSV_PART_TYPE)
            elif key == S_CSV_PART_DNASEQUENCE:
                header_keys_map[S_UCF_PART_DNASEQUENCE] = i
                expected.remove(S_CSV_PART_DNASEQUENCE)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    parts = []

    for row in reader:
        if len(row) > 0:
            collection = {}

            part_name = row[header_keys_map[S_CSV_PART_NAME]]
            if len(part_name) == 0:
                raise RuntimeError("Part name not specified.")
            else:
                for c in parts:
                    if c[S_UCF_PART_NAME] == part_name:
                        collection = c

                if len(collection) == 0:
                    collection[S_UCF_COLLECTION] = S_UCF_PARTS
                    collection[S_UCF_PART_NAME] = part_name
                    parts.append(collection)
                else:
                    raise RuntimeError("Part '%s' already specified." % part_name)

            part_type = row[header_keys_map[S_CSV_PART_TYPE]]
            if len(part_type) == 0:
                raise RuntimeError("Part type not specified for '%s'." % part_name)
            collection[S_UCF_PART_TYPE] = part_type

            part_dnasequence = row[header_keys_map[S_CSV_PART_DNASEQUENCE]]
            if len(part_dnasequence) == 0:
                raise RuntimeError("Part dna sequence not specified for '%s'." % part_name)
            collection[S_UCF_PART_DNASEQUENCE] = part_dnasequence

    ucf += parts
    return ucf

def add_motif_library(filename,ucf):
    raise NotImplementedError("Motif library not implemented.")

def add_standard_motif_library(ucf):
    raise NotImplementedError("Motif library not implemented.")    

def add_toxicity(filename,ucf):
    raise NotImplementedError("Toxicity not implemented.")    

def add_cytometry(filename,ucf):
    raise NotImplementedError("Cytometry not implemented.")    

def add_header(filename,ucf):
    raise NotImplementedError("Header not implemented.")    

def add_measurement_standard(filename,ucf):
    raise NotImplementedError("Measurement standard not implemented.")    

def add_logic_constraints(filename,ucf):
    raise NotImplementedError("Logic constraints not implemented.")    

def add_placement_rules(filename,ucf):
    raise NotImplementedError("Placement rules not implemented.")    

def main():
    parser = argparse.ArgumentParser(description="Build a UCF.")
    parser.add_argument("--gate-parts", "-g", dest="gate_parts", required=True, help="Gate parts CSV.", metavar="FILE")
    parser.add_argument("--response-functions", "-f", dest="response_functions", required=True, help="Response functions CSV.", metavar="FILE")
    parser.add_argument("--parts", "-p", dest="parts", required=True, help="Parts CSV.", metavar="FILE")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--motif-library", "-m", dest="motif_library", help="Motif library input file.", metavar="FILE")
    group.add_argument("--std-motif-library", dest="std_motif_library", help="Use the standard motif library.", action='store_true')
    
    parser.add_argument("--toxicity", "-t", help="Toxicity input file.", metavar="FILE")
    parser.add_argument("--cytometry", "-c", help="Cytometry input file.", metavar="FILE")
    parser.add_argument("--header", "-e", help="Header input file.", metavar="FILE")
    parser.add_argument("--measurement-std", "-s", dest="measurement_std", help="Measurement standard input file.", metavar="FILE")
    parser.add_argument("--logic-constraints", "-l", dest="logic_constraints", help="Measurement standard input file.", metavar="FILE")
    parser.add_argument("--placement-rules", "-r", dest="placement_rules", help="Placement rules input file.", metavar="FILE")
    args = parser.parse_args()
    
    ucf = []
    if args.motif_library:
        ucf = add_motif_library(args.motif_library,ucf)
    if args.std_motif_library:
        ucf = add_standard_motif_library(ucf)
    ucf = add_gate_parts(args.gate_parts,ucf)
    ucf = add_response_functions(args.response_functions,ucf)
    ucf = add_parts(args.parts,ucf)
    if args.toxicity:
        ucf = add_toxicity(args.toxicity,ucf)
    if args.cytometry:
        ucf = add_cytometry(args.cytometry,ucf)
    if args.placement_rules:
        ucf = add_placement_rules(args.placement_rules,ucf)
    if args.measurement_std:
        ucf = add_measurement_standard(args.measurement_std,ucf)


    print(json.dumps(ucf,indent=4))

if __name__ == "__main__":
    main()