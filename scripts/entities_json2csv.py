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

import json, sys, argparse, os
import unidecode
from wawCommons import printf, eprintf, toEntityName

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompose Bluemix conversation service entities in .json format to entity files in .csv format', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('entities', help='file with entities in .json format')
    parser.add_argument('entitiesDir', help='directory with entities files')
    # optional arguments
    parser.add_argument('-ne', '--common_entities_nameCheck', action='append', nargs=2, help="regex and replacement for entity name check, e.g. '-' '_' for to replace hyphens for underscores or '$special' '\L' for lowercase")
    parser.add_argument('-s', '--soft', required=False, help='soft name policy - change intents and entities names without error.', action='store_true', default="")
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    VERBOSE = args.verbose
    if args.soft: NAME_POLICY = 'soft'
    else: NAME_POLICY = 'hard'

    with open(args.entities, 'r') as entitiesFile:
        entitiesJSON = json.load(entitiesFile)

    systemEntities = []
    # process all entities
    for entityJSON in entitiesJSON:
        # process system entity
        if entityJSON["entity"].strip().lower() .startswith("sys-"):
            # issue #82: make entity name check parameter-dependent
            #systemEntities.append(toEntityName(NAME_POLICY, entityJSON["entity"]))
            systemEntities.append(entityJSON["entity"])
        # process normal entity
        else:
            values = []
            # process all entity values
            for valueJSON in entityJSON["values"]:
                value = []
                value.append(unidecode.unidecode(valueJSON["value"].strip()))
                # add all synonyms
                if 'synonyms' in valueJSON:
                    for synonym in valueJSON['synonyms']:
                        value.append(synonym.strip())
                values.append(value)
            # new entity file
            entityFileName = os.path.join(args.entitiesDir, toEntityName(NAME_POLICY, args.common_entities_nameCheck, entityJSON["entity"])) + ".csv"
            with open(entityFileName, "w") as entityFile:
                for value in values:
                    entityFile.write(';'.join(value) + "\n")

    # write file with system entities
    with open(os.path.join(args.entitiesDir, "system_entities.csv"), 'w') as systemEntitiesFile:
        systemEntitiesFile.write("# a special list for the system entities - only one value at each line\n")
        for systemEntity in systemEntities:
            systemEntitiesFile.write(systemEntity + "\n")

    if VERBOSE: printf("Entities from file '%s' were successfully extracted\n", args.entities)
