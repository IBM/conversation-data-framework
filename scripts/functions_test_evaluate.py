'''
Copyright 2018 IBM Corporation
Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import json, sys, os, argparse, requests, configparser
from wawCommons import setLoggerConfig, getScriptLogger, getRequiredParameter, getOptionalParameter, getParametersCombination, convertApikeyToUsernameAndPassword, replaceValue
from cfgCommons import Cfg
import logging
from deepdiff import DeepDiff

logger = getScriptLogger(__file__)

def main(argv):
    parser = argparse.ArgumentParser(description='Evaluates all test output against Cloud Functions specified in given file and save evaluation output to output file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # positional arguments
    parser.add_argument('inputFileName', help='File with json array containing test output.')
    parser.add_argument('outputFileName', help='File where to store evaluation output.')
    # optional arguments
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
    parser.add_argument('--log', type=str.upper, default=None, choices=list(logging._levelToName.values()))
    args = parser.parse_args(argv)

    if __name__ == '__main__':
        setLoggerConfig(args.log, args.verbose)

    config = Cfg(args)

    logger.info('STARTING: '+ os.path.basename(__file__))

    try:
        inputFile = open(args.inputFileName, 'r')
    except IOError:
        logger.critical('Cannot open test output file %s', args.inputFileName)
        sys.exit(1)

    try:
        outputFile = open(args.outputFileName, 'w')
    except IOError:
        logger.critical('Cannot open evaluation output file %s', args.outputFileName)
        sys.exit(1)

    try:
        inputJson = json.load(inputFile)
    except ValueError as e:
        logger.critical('Cannot decode json from test output file %s, error: %s', args.inputFileName, str(e))
        sys.exit(1)

    if not isinstance(inputJson, list):
        logger.critical('Test output json is not array!')
        sys.exit(1)

    # run evaluation
    testCounter = 0
    for test in inputJson:
        if not isinstance(test, dict):
            logger.error('Input test array element %d is not dictionary. Each test has to be dictionary, please see doc!', testCounter)
            continue
        logger.info('Test number: %d, name: %s', testCounter, (test['name'] if 'name' in test else '-'))

        # load test expected output payload json
        testOutputExpectedJson = test['outputExpected']
        testOutputExpectedPath = None
        try:
            if testOutputExpectedJson.startswith('@'):
                testOutputExpectedPath = os.path.join(os.path.dirname(args.inputFileName), testOutputExpectedJson[1:])
                logger.debug('Loading expected output payload from file: %s', testOutputExpectedPath)
                try:
                    outputExpectedFile = open(testOutputExpectedPath, 'r')
                except IOError:
                    logger.error('Cannot open expected output payload from file: %s', testOutputExpectedPath)
                    continue
                try:
                    testOutputExpectedJson = json.load(outputExpectedFile)
                except ValueError as e:
                    logger.error('Cannot decode json from expected output payload from file %s, error: %s', testOutputExpectedPath, str(e))
                    continue
        except:
            pass

        if not testOutputExpectedPath:
            logger.debug('Expected output payload provided inside the test')

        # load test returned output payload json
        testOutputReturnedJson = test['outputReturned']
        testOutputReturnedPath = None
        try:
            if testOutputReturnedJson.startswith('@'):
                testOutputReturnedPath = os.path.join(os.path.dirname(args.inputFileName), testOutputReturnedJson[1:])
                logger.debug('Loading returned output payload from file: %s', testOutputReturnedPath)
                try:
                    outputReturnedFile = open(testOutputReturnedPath, 'r')
                except IOError:
                    logger.error('Cannot open returned output payload from file: %s', testOutputReturnedPath)
                    continue
                try:
                    testOutputReturnedJson = json.load(outputReturnedFile)
                except ValueError as e:
                    logger.error('Cannot decode json from returned output payload from file %s, error: %s', testOutputReturnedPath, str(e))
                    continue
        except:
            pass

        # evaluate test
        if 'type' not in test or test['type'] == 'EXACT_MATCH':
            testResultString = DeepDiff(testOutputExpectedJson, testOutputReturnedJson, ignore_order=True).json
            testResultJson = json.loads(testResultString)
            if testResultJson == {}:
                test['result'] = 0
            else:
                test['result'] = 1
                test['diff'] = testResultJson
        else:
            logger.error('Unknown test type: %s', test['type'])

        testCounter += 1

    outputFile.write(json.dumps(inputJson, indent=4, ensure_ascii=False) + '\n')
    logger.info('FINISHING: '+ os.path.basename(__file__))

if __name__ == '__main__':
    main(sys.argv[1:])

