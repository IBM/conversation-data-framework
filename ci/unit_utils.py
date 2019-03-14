"""
Copyright 2019 IBM Corporation
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

import json, os, pytest, sys, unittest, traceback, shutil

#class BaseTestCaseCapture(unittest.TestCase):
class BaseTestCaseCapture(object):

    dialogSchemaPath = '../data_spec/dialog_schema.xml'
    captured = None

    def tTooFewArgs(self, *args, **kwargs):
        ''' Runs predefined function (callfunc) with given arguments and tests if it fails and error message contains \'too few arguments\' '''
        self.tfTooFewArgs(self.callfunc, *args, **kwargs)

    def tfTooFewArgs(self, function, *args, **kwargs):
        ''' Runs function with given arguments and tests if it fails and error message contains \'too few arguments\' '''
        self.tfExitCodeAndErrMessage(function, 2, 'too few arguments', *args, **kwargs)

    def tUnrecognizedArgs(self, *args, **kwargs):
        ''' Runs predefined function (callfunc) with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
        self.tfUnrecognizedArgs(self.callfunc, *args, **kwargs)

    def tfUnrecognizedArgs(self, function, *args, **kwargs):
        ''' Runs function with given arguments and tests if it fails and error message contains \'unrecognized arguments\' '''
        self.tfExitCodeAndErrMessage(function, 2, 'unrecognized arguments', *args, **kwargs)

    def tExitCode(self, exitCode, *args, **kwargs):
        ''' Runs predefined function (callfunc) with given arguments and tests exit code '''
        self.tfExitCode(self.callfunc, exitCode, *args, **kwargs)

    def tfExitCode(self, function, exitCode, *args, **kwargs):
        ''' Runs function with given arguments and tests exit code '''
        self.tfExitCodeAndErrMessage(function, exitCode, '', *args, **kwargs)

    def tExitCodeAndErrMessage(self, exitCode, errMessage, *args, **kwargs):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exit code and error message '''
        self.tfExitCodeAndErrMessage(self.callfunc, exitCode, errMessage, *args, **kwargs)

    def tfExitCodeAndErrMessage(self, function, exitCode, errMessage, *args, **kwargs):
        ''' (Generic) Runs function with given arguments and tests exit code and error message '''
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            function(*args, **kwargs)
        self.captured = self.capfd.readouterr()
        assert pytest_wrapped_e.value.code == exitCode
        assert errMessage in self.captured.err

    def tRaiseError(self, errorType, errMessage, *args, **kwargs):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and tests exception '''
        self.tfRaiseError(self.callfunc, errorType, errMessage, *args, **kwargs)

    def tfRaiseError(self, function, errorType, errMessage, *args, **kwargs):
        ''' (Generic) Runs function with given arguments and tests exception '''
        with pytest.raises(errorType, match=errMessage) as pytest_wrapped_e:
            function(*args, **kwargs)
        self.captured = self.capfd.readouterr()

    def t(self, *args, **kwargs):
        ''' (Generic) Runs predefined function (callfunc) with given arguments and checks that no exception was raised '''
        self.tf(self.callfunc, *args, **kwargs)

    def tf(self, function, *args, **kwargs):
        ''' (Generic) Runs function with given arguments and checks that no exception was raised '''
        try:
            function(*args, **kwargs)
            self.captured = self.capfd.readouterr()
        except Exception as e:
            pytest.fail(traceback.print_exception(*sys.exc_info()))

    def callfunc(self, *args, **kwargs):
        ''' (Need to be overidden) Function to be called and tested '''
        raise NotImplementedError()

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    @staticmethod
    def createFolder(folderPath, deleteExisting=True):
        ''' Creates folder with parent folders given by path if the folder does not exist '''
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        elif deleteExisting:
            shutil.rmtree(folderPath)
            os.makedirs(folderPath)

    @staticmethod
    def createFolders(folderPaths, deleteExisting=True):
        ''' Calls createFolder method for each folder path (given by array) '''
        for folderPath in folderPaths:
            BaseTestCaseCapture.createFolder(folderPath, deleteExisting)

    @staticmethod
    def checkEnvironmentVariable(environmentVariable):
        BaseTestCaseCapture.checkEnvironmentVariables([environmentVariable])

    @staticmethod
    def checkEnvironmentVariables(environmentVariables):
        missingEnvironmentVariables = list(set(environmentVariables) - set(os.environ))
        if missingEnvironmentVariables:
            if len(missingEnvironmentVariables) == 1:
                pytest.fail('Missing ENVIRONMENT VARIABLE: ' + missingEnvironmentVariables[0])
            else:
                missingEnvironmentVariables.sort()
                pytest.fail('Missing ENVIRONMENT VARIABLES: ' + str(missingEnvironmentVariables))

