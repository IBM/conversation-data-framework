"""
Copyright 2018 IBM Corporation
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json, sys, os.path, argparse, random, string, re
from wawCommons import printf, eprintf


try:
    basestring            # Python 2
except NameError:
    basestring = (str, )  # Python 3


    # function to find a desired variable in complex json and add other part of json
def includeJson(nodeJSON, keyJSON, keySearch, includeJSON):
    if keyJSON == keySearch:
        nodeJSON[keyJSON] = includeJSON
    # None
    if nodeJSON[keyJSON] is None:
        pass
    # list
    elif isinstance(nodeJSON[keyJSON], list):
        for i in range(len(nodeJSON[keyJSON])):
            includeJson(nodeJSON[keyJSON], i, keySearch, includeJSON)
    # dict
    elif isinstance(nodeJSON[keyJSON], dict):
        for subKeyJSON in nodeJSON[keyJSON]:
            includeJson(nodeJSON[keyJSON], subKeyJSON, keySearch, includeJSON)


if __name__ == '__main__':
    printf('\nSTARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='This script takes a workspace JSON as one parameter and another JSON (i.e., piece of context data structure) and put the second one into desired place in first one', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('workspaceFileName', help='file with original workspace JSON')
    parser.add_argument('jsonInclude', help='file with JSON you want to include')
    parser.add_argument('targetElement', help='the element, where you want to add your JSON, i.e., "data_structure" : null; where you want to replace null, you would put "data_strucute" as this parameter')
    # optional arguments
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    #init the parameters
    VERBOSE = args.verbose

    inputpath = args.workspaceFileName
    jsonincludepath = args.jsonInclude
    targetElement = args.targetElement

    if not os.path.isfile(inputpath):
        eprintf("ERROR: Input workspace json '%s' does not exist.", inputpath)
        exit(1)

    if not os.path.isfile(jsonincludepath):
        eprintf("ERROR: to include JSON file '%s' does not exist.", jsonincludepath)
        exit(1)
    #open the workspace file and json to add
    with open(inputpath) as f:
        workspaceInput = json.load(f)

    with open(jsonincludepath) as g:
        jsonInclude = json.load(g)
    #find the target variable and add the json
    includeJson(workspaceInput, "dialog_nodes", targetElement, jsonInclude)
    #writing the file
    with open(inputpath, 'w') as outfile:
        print('Writing workspaces with added JSON.')
        json.dump(workspaceInput, outfile, indent=4)

    print('\nFINISHING: ' + os.path.basename(__file__) + '\n')
