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

import os, json, sys, argparse, requests, zipfile, base64
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from cfgCommons import Cfg
from wawCommons import setLoggerConfig, getScriptLogger, getFilesAtPath, openFile, getRequiredParameter, getOptionalParameter, getParametersCombination, convertApikeyToUsernameAndPassword
import urllib3
import logging


logger = getScriptLogger(__file__)

def isActionNotSequence(action):
    for annotation in action['annotations']:
        if annotation['key'] == 'exec' and annotation['value'] == 'sequence': return True;
    return False

def main(argv):
    logger.info('STARTING: '+ os.path.basename(__file__))
    parser = argparse.ArgumentParser(description="Deploys the cloud functions",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('-c', '--common_configFilePaths', help="configuaration file", action='append')
    parser.add_argument('--common_functions', required=False, help="directory where the cloud functions are located")
    parser.add_argument('--cloudfunctions_namespace', required=False, help="cloud functions namespace")
    parser.add_argument('--cloudfunctions_apikey', required=False, help="cloud functions apikey")
    parser.add_argument('--cloudfunctions_username', required=False, help="cloud functions user name")
    parser.add_argument('--cloudfunctions_password', required=False, help="cloud functions password")
    parser.add_argument('--cloudfunctions_package', required=False, help="cloud functions package name")
    parser.add_argument('--cloudfunctions_url', required=False, help="url of cloud functions API")
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))

    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)
        
    config = Cfg(args)

    namespace = getRequiredParameter(config, 'cloudfunctions_namespace')
    auth = getParametersCombination(config, 'cloudfunctions_apikey', ['cloudfunctions_password', 'cloudfunctions_username'])
    package = getRequiredParameter(config, 'cloudfunctions_package')
    namespaceUrl = getRequiredParameter(config, 'cloudfunctions_url')
    functionDir = getRequiredParameter(config, 'common_functions')

    if 'cloudfunctions_apikey' in auth:
        username, password = convertApikeyToUsernameAndPassword(auth['cloudfunctions_apikey'])
    else:
        username = auth['cloudfunctions_username']
        password = auth['cloudfunctions_password']

    logger.info(f"Will delete cloud functions in package '{package}'.")

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    packageUrl = namespaceUrl + '/' + namespace + '/packages/' + package# + '?overwrite=true'
    response = requests.get(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
    responseJson = response.json()

    if 'error' in responseJson:
        logger.critical("Cannot get the package information")
        logger.critical(responseJson['error'])
        sys.exit(1)
    
    actions = responseJson['actions']
    # put the sequences at the beggining
    actions.sort(key=lambda action: isActionNotSequence(action))
    
    for action in actions:
        name = action['name']
        actionUrl = namespaceUrl + '/' + namespace + '/actions/' + package +'/' + name
        logger.verbose(f"Deleting action '{name}' at {actionUrl}")
        response = requests.delete(actionUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
        responseJson = response.json()
        if 'error' in responseJson:
            logger.critical(f"Cannot delete the action '{name}'")
            logger.critical(responseJson['error'])
            sys.exit(1)
        else:
            logger.verbose("Done")
    
    logger.verbose(f"Deleting package '{package}'")
    response = requests.delete(packageUrl, auth=(username, password), headers={'Content-Type': 'application/json'})
    responseJson = response.json()

    if 'error' in responseJson:
        logger.critical(f"Cannot delete the package '{name}'")
        logger.critical(responseJson['error'])
        sys.exit(1)
    else:
        logger.verbose("Done")

if __name__ == '__main__':
    main(sys.argv[1:])
