import csv
import json
import argparse
import time
import warnings

__author__  = 'Timothy S. Jones <jonests@bu.edu>, Densmore Lab, BU'
__license__ = 'GPL3'

def add_gates(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_REGULATOR = 'regulator'
    S_CSV_GROUP_NAME = 'group_name'
    S_CSV_GATE_NAME = 'gate_name'
    S_CSV_GATE_TYPE = 'gate_type'
    S_CSV_SYSTEM = 'system'
    S_CSV_COLOR_HEXCODE = 'color_hexcode'

    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_GATES = 'gates'
    S_UCF_REGULATOR = 'regulator'
    S_UCF_GROUP_NAME = 'group_name'
    S_UCF_GATE_NAME = 'gate_name'
    S_UCF_GATE_TYPE = 'gate_type'
    S_UCF_SYSTEM = 'system'
    S_UCF_COLOR_HEXCODE = 'color_hexcode'

    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {}

    expected = set([S_CSV_REGULATOR,
                    S_CSV_GROUP_NAME,
                    S_CSV_GATE_NAME,
                    S_CSV_GATE_TYPE,
                    S_CSV_SYSTEM,
                    S_CSV_COLOR_HEXCODE])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_REGULATOR:
                header_keys_map[S_CSV_REGULATOR] = i
                expected.remove(S_CSV_REGULATOR)
            elif key == S_CSV_GROUP_NAME:
                header_keys_map[S_CSV_GROUP_NAME] = i
                expected.remove(S_CSV_GROUP_NAME)
            elif key == S_CSV_GATE_NAME:
                header_keys_map[S_CSV_GATE_NAME] = i
                expected.remove(S_CSV_GATE_NAME)
            elif key == S_CSV_GATE_TYPE:
                header_keys_map[S_CSV_GATE_TYPE] = i
                expected.remove(S_CSV_GATE_TYPE)
            elif key == S_CSV_SYSTEM:
                header_keys_map[S_CSV_SYSTEM] = i
                expected.remove(S_CSV_SYSTEM)
            elif key == S_CSV_COLOR_HEXCODE:
                header_keys_map[S_CSV_COLOR_HEXCODE] = i
                expected.remove(S_CSV_COLOR_HEXCODE)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))
        
    gates = []

    for row in reader:
        regulator = row[header_keys_map[S_CSV_REGULATOR]]
        group_name = row[header_keys_map[S_CSV_GROUP_NAME]]
        gate_name = row[header_keys_map[S_CSV_GATE_NAME]]
        gate_type = row[header_keys_map[S_CSV_GATE_TYPE]]
        system = row[header_keys_map[S_CSV_SYSTEM]]
        color_hexcode = row[header_keys_map[S_CSV_COLOR_HEXCODE]]

        collection = {S_UCF_COLLECTION: S_UCF_GATES,
                      S_UCF_REGULATOR: regulator,
                      S_UCF_GROUP_NAME: group_name,
                      S_UCF_GATE_NAME: gate_name,
                      S_UCF_GATE_TYPE: gate_type,
                      S_UCF_SYSTEM: system,
                      S_UCF_COLOR_HEXCODE: color_hexcode}

        gates.append(collection)

    ucf += gates
    return ucf

def add_logic_constraints(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_TYPE = 'type'
    S_CSV_MAX_INSTANCES = 'max_instances'
    
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_LOGIC_CONTRAINTS = 'logic_constraints'
    S_UCF_TYPE = 'type'
    S_UCF_MAX_INSTANCES = 'max_instances'
    S_UCF_AVAILABLE_GATES = 'available_gates'
    
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {}

    expected = set([S_CSV_TYPE,
                    S_CSV_MAX_INSTANCES])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_TYPE:
                header_keys_map[S_CSV_TYPE] = i
                expected.remove(S_CSV_TYPE)
            elif key == S_CSV_MAX_INSTANCES:
                header_keys_map[S_CSV_MAX_INSTANCES] = i
                expected.remove(S_CSV_MAX_INSTANCES)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    collection = {S_UCF_COLLECTION: S_UCF_LOGIC_CONTRAINTS,
                  S_UCF_AVAILABLE_GATES: []}

    for row in reader:
        if len(row) > 0:
            constraint_type = row[header_keys_map[S_CSV_TYPE]]
            if len(constraint_type) == 0:
                raise RuntimeError("'%s' not specified." % S_CSV_TYPE)

            max_instances = row[header_keys_map[S_CSV_MAX_INSTANCES]]
            if len(max_instances) == 0:
                raise RuntimeError("'%s' not specified." % S_CSV_MAX_INSTANCES)

            constraint = {S_UCF_TYPE: constraint_type,
                          S_UCF_MAX_INSTANCES: max_instances}

            collection[S_UCF_AVAILABLE_GATES].append(constraint)
                    
    ucf.append(collection)
    return ucf

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
                                warnings.warn("Variable %s already added to this gate. Skipping." % variable,RuntimeWarning)

                        if len(cassette) > 0:
                            continue
                    else:
                         collection['expression_cassettes'] = cassettes   

                    cassette['maps_to_variable'] = variable
                    parts = []
                    if spec[S_CSV_PART] == 0:
                        warnings.warn("No parts specified for %s, variable %s." % (name,variable),RuntimeWarning)
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
                    warnings.warn("Part '%s' already specified, skipping." % part_name,RuntimeWarning)
                    continue

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
    with open('std-motif.json', 'r') as jsonfile:
        motif = json.load(jsonfile)

    ucf += motif
    return ucf

def add_toxicity(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_GATE_NAME = "gate_name"
    S_CSV_VARIABLE_NAME = "variable"
    S_CSV_INPUT = "input"
    S_CSV_GROWTH = "growth"
        
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = "collection"
    S_UCF_TOXICITY = "gate_toxicity"
    S_UCF_GATE_NAME = "gate_name"
    S_UCF_VARIABLE_NAME = "maps_to_variable"
    S_UCF_INPUT = "input"
    S_UCF_GROWTH = "growth"
    
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {}

    expected = set([S_CSV_GATE_NAME,
                    S_CSV_VARIABLE_NAME,
                    S_CSV_INPUT,
                    S_CSV_GROWTH])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_GATE_NAME:
                header_keys_map[S_UCF_GATE_NAME] = i
                expected.remove(S_CSV_GATE_NAME)
            elif key == S_CSV_VARIABLE_NAME:
                header_keys_map[S_UCF_VARIABLE_NAME] = i
                expected.remove(S_CSV_VARIABLE_NAME)
            elif key == S_CSV_INPUT:
                header_keys_map[S_UCF_INPUT] = i
                expected.remove(S_CSV_INPUT)
            elif key == S_CSV_GROWTH:
                header_keys_map[S_UCF_GROWTH] = i
                expected.remove(S_CSV_GROWTH)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    toxicity = []

    for row in reader:
        if len(row) > 0:
            collection = {}

            gate_name = row[header_keys_map[S_UCF_GATE_NAME]]
            variable = row[header_keys_map[S_UCF_VARIABLE_NAME]]
            if len(gate_name) == 0:
                raise RuntimeError("Gate name not specified.")
            elif len(variable) == 0:
                raise RuntimeError("Variable name not specified.")
            else:
                for c in toxicity:
                    if c[S_UCF_GATE_NAME] == gate_name and c[S_UCF_VARIABLE_NAME] == variable:
                        collection = c

                if len(collection) == 0:
                    collection[S_UCF_COLLECTION] = S_UCF_TOXICITY
                    collection[S_UCF_GATE_NAME] = gate_name
                    collection[S_UCF_VARIABLE_NAME] = variable
                    collection[S_UCF_INPUT] = []
                    collection[S_UCF_GROWTH] = []
                    toxicity.append(collection)

            input_value = row[header_keys_map[S_CSV_INPUT]]
            if len(input_value) == 0:
                raise RuntimeError("Input value not specified for '%s'." % input_value)
            collection[S_UCF_INPUT].append(float(input_value))

            growth_value = row[header_keys_map[S_CSV_GROWTH]]
            if len(growth_value) == 0:
                raise RuntimeError("Growth value not specified for '%s'." % gate_name)
            collection[S_UCF_GROWTH].append(float(growth_value))

    ucf += toxicity
    return ucf

def add_cytometry(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_GATE_NAME = 'gate_name'
    S_CSV_VARIABLE = 'variable'
    S_CSV_INPUT = 'input'
    S_CSV_OUTPUT_BIN = 'bin'
    S_CSV_OUTPUT_COUNT = 'count'
    
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_CYTOMETRY = 'gate_cytometry'
    S_UCF_GATE_NAME = 'gate_name'
    S_UCF_VARIABLE = 'maps_to_variable'
    S_UCF_INPUT = 'input'
    S_UCF_OUTPUT_BIN = 'output_bins'
    S_UCF_OUTPUT_COUNT = 'output_counts'
    S_UCF_CYTOMETRY_DATA = 'cytometry_data'
    
    reader = csv.reader(open(filename, 'r'), delimiter=',')
    header = next(reader)
    
    header_keys_map = {}

    expected = set([S_CSV_GATE_NAME,
                    S_CSV_VARIABLE,
                    S_CSV_INPUT,
                    S_CSV_OUTPUT_BIN,
                    S_CSV_OUTPUT_COUNT])
    for i,key in enumerate(header):
        if key in expected:
            if key == S_CSV_GATE_NAME:
                header_keys_map[S_CSV_GATE_NAME] = i
                expected.remove(S_CSV_GATE_NAME)
            elif key == S_CSV_VARIABLE:
                header_keys_map[S_CSV_VARIABLE] = i
                expected.remove(S_CSV_VARIABLE)
            elif key == S_CSV_INPUT:
                header_keys_map[S_CSV_INPUT] = i
                expected.remove(S_CSV_INPUT)
            elif key == S_CSV_OUTPUT_BIN:
                header_keys_map[S_CSV_OUTPUT_BIN] = i
                expected.remove(S_CSV_OUTPUT_BIN)
            elif key == S_CSV_OUTPUT_COUNT:
                header_keys_map[S_CSV_OUTPUT_COUNT] = i
                expected.remove(S_CSV_OUTPUT_COUNT)
        else:
            raise RuntimeError("Unexpected header key in %s at position %d." % (filename,i))

    cytometry = []

    for row in reader:
        if len(row) > 0:
            collection = {}

            gate_name = row[header_keys_map[S_CSV_GATE_NAME]]
            if len(gate_name) == 0:
                raise RuntimeError("Gate name not specified.")
            else:
                for c in cytometry:
                    if c[S_UCF_GATE_NAME] == gate_name:
                        collection = c

                if len(collection) == 0:
                    collection[S_UCF_COLLECTION] = S_UCF_CYTOMETRY
                    collection[S_UCF_GATE_NAME] = gate_name
                    collection[S_UCF_CYTOMETRY_DATA] = []
                    cytometry.append(collection)

                variable = row[header_keys_map[S_CSV_VARIABLE]]
                if len(variable) == 0:
                    raise RuntimeError("'%s' name not specified." % S_CSV_VARIABLE )

                cytometry_input = row[header_keys_map[S_CSV_INPUT]]
                if len(cytometry_input) == 0:
                    raise RuntimeError("'%s' name not specified." % S_CSV_INPUT)

                output_bin = row[header_keys_map[S_CSV_OUTPUT_BIN]]
                if len(output_bin) == 0:
                    raise RuntimeError("'%s' name not specified." % S_CSV_OUTPUT_BIN)

                output_count = row[header_keys_map[S_CSV_OUTPUT_COUNT]]
                if len(output_count) == 0:
                    raise RuntimeError("'%s' name not specified." % S_CSV_OUTPUT_COUNT)

                data = {}
                for obj in collection[S_UCF_CYTOMETRY_DATA]:
                    if obj[S_UCF_VARIABLE] == variable and obj[S_UCF_INPUT] == float(cytometry_input):
                        data = obj
                        break

                if len(data) == 0:
                    collection[S_UCF_CYTOMETRY_DATA].append(data)
                    data[S_UCF_VARIABLE] = variable
                    data[S_UCF_INPUT] = float(cytometry_input)
                    data[S_UCF_OUTPUT_BIN] = []
                    data[S_UCF_OUTPUT_COUNT] = []
                    
                data[S_UCF_OUTPUT_BIN].append(float(output_bin))
                data[S_UCF_OUTPUT_COUNT].append(float(output_count))
                    
    ucf += cytometry
    return ucf

def add_header(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_DESCRIPTION = 'description'
    S_CSV_VERSION = 'version'
    S_CSV_DATE = 'date'
    S_CSV_AUTHOR = 'author'
    S_CSV_ORGANISM = 'organism'
    S_CSV_GENOME = 'genome'
    S_CSV_MEDIA = 'media'
    S_CSV_TEMPERATURE = 'temperature'
    S_CSV_GROWTH = 'growth'

    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_HEADER = 'header'
    S_UCF_DESCRIPTION = 'description'
    S_UCF_VERSION = 'version'
    S_UCF_DATE = 'date'
    S_UCF_AUTHOR = 'author'
    S_UCF_ORGANISM = 'organism'
    S_UCF_GENOME = 'genome'
    S_UCF_MEDIA = 'media'
    S_UCF_TEMPERATURE = 'temperature'
    S_UCF_GROWTH = 'growth'

    reader = csv.reader(open(filename, 'r'), delimiter=',')

    collection = {S_UCF_COLLECTION: S_UCF_HEADER,
                  S_UCF_AUTHOR: [],
                  S_UCF_DATE: time.strftime("%a %b %d %H:%M:%S %Z %Y", time.localtime())}

    for row in reader:
        key = row[0]
        value = row[1]
        if key == S_CSV_DESCRIPTION:
            collection[S_UCF_DESCRIPTION] = value
        elif key == S_CSV_VERSION:
            collection[S_UCF_VERSION] = value
        elif key == S_CSV_DATE:
            collection[S_UCF_DATE] = value
        elif key == S_CSV_AUTHOR:
            collection[S_UCF_AUTHOR].append(value)
        elif key == S_CSV_ORGANISM:
            collection[S_UCF_ORGANISM] = value
        elif key == S_CSV_GENOME:
            collection[S_UCF_GENOME] = value
        elif key == S_CSV_MEDIA:
            collection[S_UCF_MEDIA] = value
        elif key == S_CSV_TEMPERATURE:
            collection[S_UCF_TEMPERATURE] = value
        elif key == S_CSV_GROWTH:
            collection[S_UCF_GROWTH] = value
        else:
            warnings.warn("Unrecognized key '%s'" % key,RuntimeWarning)

    ucf.append(collection)
    return ucf
    
def add_measurement_standard(filename,ucf):
    ###############
    # header keys #
    ###############
    S_CSV_UNITS = 'signal_carrier_units'
    S_CSV_NORMALIZATION = 'normalization_instructions'
    S_CSV_DESCRIPTION = 'plasmid_description'

    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_MEASUREMENT_STD = 'measurement_std'
    S_UCF_UNITS = 'signal_carrier_units'
    S_UCF_NORMALIZATION = 'normalization_instructions'
    S_UCF_DESCRIPTION = 'plasmid_description'
    S_UCF_SEQUENCE = 'plasmid_sequence'

    reader = csv.reader(open(filename, 'r'), delimiter=',')

    collection = {}

    for c in ucf:
        if c[S_UCF_COLLECTION] == S_UCF_MEASUREMENT_STD:
            collection = c
            break

    if len(collection) == 0:
        collection = {S_UCF_COLLECTION: S_UCF_MEASUREMENT_STD}
        ucf.append(collection)

    for row in reader:
        key = row[0]
        value = row[1]
        if key == S_CSV_UNITS:
            collection[S_UCF_UNITS] = value
        elif key == S_CSV_NORMALIZATION:
            collection[S_UCF_NORMALIZATION] = value
        elif key == S_CSV_DESCRIPTION:
            collection[S_UCF_DESCRIPTION] = value
        else:
            warnings.warn("Unrecognized key '%s'" % key,RuntimeWarning)

    return ucf

def add_measurement_plasmid(filename,ucf):
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_MEASUREMENT_STD = 'measurement_std'
    S_UCF_SEQUENCE = 'plasmid_sequence'

    collection = {}

    for c in ucf:
        if c[S_UCF_COLLECTION] == S_UCF_MEASUREMENT_STD:
            collection = c
            break

    if len(collection) == 0:
        collection = {S_UCF_COLLECTION: S_UCF_MEASUREMENT_STD}
        ucf.append(collection)

    plasmid_sequence = []
    with open(filename, 'r') as plasmidfile:
        plasmid_sequence = plasmidfile.read().splitlines()

    collection[S_UCF_SEQUENCE] = plasmid_sequence

    return ucf

def add_part_placement_rules(filename,ucf):
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_PLACEMENT_RULES = 'eugene_rules'
    S_UCF_PART_PLACEMENT_RULES = 'eugene_part_rules'
    S_UCF_GATE_PLACEMENT_RULES = 'eugene_gate_rules'

    collection = {}

    for c in ucf:
        if c[S_UCF_COLLECTION] == S_UCF_PLACEMENT_RULES:
            collection = c
            break

    if len(collection) == 0:
        collection = {S_UCF_COLLECTION: S_UCF_PLACEMENT_RULES}
        ucf.append(collection)

    rules = []
    with open(filename, 'r') as rulesfile:
        rules = rulesfile.read().splitlines()

    collection[S_UCF_PART_PLACEMENT_RULES] = rules

    return ucf

def add_gate_placement_rules(filename,ucf):
    ############
    # ucf keys #
    ############
    S_UCF_COLLECTION = 'collection'
    S_UCF_PLACEMENT_RULES = 'eugene_rules'
    S_UCF_PART_PLACEMENT_RULES = 'eugene_part_rules'
    S_UCF_GATE_PLACEMENT_RULES = 'eugene_gate_rules'

    collection = {}

    for c in ucf:
        if c[S_UCF_COLLECTION] == S_UCF_PLACEMENT_RULES:
            collection = c
            break

    if len(collection) == 0:
        collection = {S_UCF_COLLECTION: S_UCF_PLACEMENT_RULES}
        ucf.append(collection)

    rules = []
    with open(filename, 'r') as rulesfile:
        rules = rulesfile.read().splitlines()

    collection[S_UCF_GATE_PLACEMENT_RULES] = rules

    return ucf

def main():
    parser = argparse.ArgumentParser(description="Build a UCF.")
    parser.add_argument("--header", "-e", required=True, help="Header input CSV.", metavar="FILE")

    parser.add_argument("--measurement-std", "-s", dest="measurement_std", help="Measurement standard CSV.", metavar="FILE")
    parser.add_argument("--measurement-plasmid", "-i", dest="measurement_plasmid", help="Measurement standard plasmid.", metavar="FILE")

    parser.add_argument("--logic-constraints", "-l", dest="logic_constraints", help="Measurement standard input file.", metavar="FILE")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--motif-library", "-m", dest="motif_library", help="Motif library input file.", metavar="FILE")
    group.add_argument("--std-motif-library", dest="std_motif_library", help="Use the standard motif library.", action='store_true')
    
    parser.add_argument("--gates", "-g", required=True, help="Gates CSV.", metavar="FILE")
    parser.add_argument("--response-functions", "-f", dest="response_functions", required=True, help="Response functions CSV.", metavar="FILE")
    parser.add_argument("--gate-parts", "-a", dest="gate_parts", required=True, help="Gate parts CSV.", metavar="FILE")
    parser.add_argument("--parts", "-p", dest="parts", required=True, help="Parts CSV.", metavar="FILE")
    parser.add_argument("--toxicity", "-t", help="Toxicity input file.", metavar="FILE")
    parser.add_argument("--cytometry", "-c", help="Cytometry input file.", metavar="FILE")
    parser.add_argument("--part-placement-rules", "-x", dest="part_placement_rules", help="Part placement rules input file.", metavar="FILE")
    parser.add_argument("--gate-placement-rules", "-y", dest="gate_placement_rules", help="Gate placement rules input file.", metavar="FILE")
    args = parser.parse_args()
    
    ucf = []
    if args.header:
        ucf = add_header(args.header,ucf)
    if args.measurement_std:
        ucf = add_measurement_standard(args.measurement_std,ucf)
    if args.measurement_plasmid:
        ucf = add_measurement_plasmid(args.measurement_plasmid,ucf)
    if args.logic_constraints:
        ucf = add_logic_constraints(args.logic_constraints,ucf)
    if args.motif_library:
        ucf = add_motif_library(args.motif_library,ucf)
    if args.std_motif_library:
        ucf = add_standard_motif_library(ucf)
    ucf = add_gates(args.gates,ucf)
    ucf = add_response_functions(args.response_functions,ucf)
    ucf = add_gate_parts(args.gate_parts,ucf)
    ucf = add_parts(args.parts,ucf)
    if args.toxicity:
        ucf = add_toxicity(args.toxicity,ucf)
    if args.cytometry:
        ucf = add_cytometry(args.cytometry,ucf)
    if args.part_placement_rules:
        ucf = add_part_placement_rules(args.part_placement_rules,ucf)
    if args.gate_placement_rules:
        ucf = add_gate_placement_rules(args.gate_placement_rules,ucf)

    print(json.dumps(ucf,indent=2))

if __name__ == "__main__":
    main()
