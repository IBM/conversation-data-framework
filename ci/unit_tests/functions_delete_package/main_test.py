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

import json, os, pytest, requests, shutil, unittest, uuid, zipfile

import functions_delete_package
from ...test_utils import BaseTestCaseCapture
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning

class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    packageBase = "Package-for-WAW-CI-"

    def setup_class(cls):
        BaseTestCaseCapture.checkEnvironmentVariables(['CLOUD_FUNCTIONS_USERNAME', 'CLOUD_FUNCTIONS_PASSWORD',
                                                       'CLOUD_FUNCTIONS_NAMESPACE'])
        cls.username = os.environ['CLOUD_FUNCTIONS_USERNAME']
        cls.password = os.environ['CLOUD_FUNCTIONS_PASSWORD']
        cls.apikey = cls.username + ':' + cls.password
        cls.cloudFunctionsUrl = os.environ.get('CLOUD_FUNCTIONS_URL',
                                               'https://us-south.functions.cloud.ibm.com/api/v1/namespaces')
        cls.namespace = os.environ['CLOUD_FUNCTIONS_NAMESPACE']
        cls.urlNamespace = quote(cls.namespace)
        cls.actionsUrl = cls.cloudFunctionsUrl + '/' + cls.urlNamespace + '/actions/'
        cls.functionFilePath = os.path.join(cls.dataBasePath, 'examplePython.py')

    def callfunc(self, *args, **kwargs):
        functions_delete_package.main(*args, **kwargs)

    def setup_method(self):
        self.package = self.packageBase + str(uuid.uuid4())

    def _uploadPackage(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        packageUrl = self.cloudFunctionsUrl + '/' + self.urlNamespace + '/packages/' + self.package + '?overwrite=true'
        response = requests.put(packageUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'},
                                data='{}')
        responseJson = response.json()
        return responseJson

    # TODO: Enable enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteEmptyPackage(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is empty."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        responseJson = self._uploadPackage()
        if 'error' in responseJson:
            pytest.fail(responseJson['error'])

        # delete package
        self.t_noException([params])
    
    # TODO: Enable enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonEmptyPackageWithoutSequence(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is not empty and doesn't have a sequence."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl,
                '--cloudfunctions_package', self.package]

        responseJson = self._uploadPackage()
        if 'error' in responseJson:
            pytest.fail(responseJson['error'])

        functionsDir = os.path.join(self.dataBasePath, 'example_functions')
        functionFiles = [os.path.join(functionsDir, f) for f in os.listdir(functionsDir)]

        # Iterate over the cloud functions and upload them
        for fileName in functionFiles:
            funcName = os.path.basename(fileName)
            functionUrl = self.actionsUrl + self.package + '/' + funcName + '?overwrite=true'

            content = open(fileName, 'r').read()
            payload = {'exec': {'kind': 'python', 'binary': False, 'code': content}}
            # Upload the cloud function
            response = requests.put(functionUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'},
                                    data=json.dumps(payload), verify=False)
            responseJson = response.json()

            if 'error' in responseJson:
                pytest.fail(responseJson['error'])

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])

        # delete package
        self.t_noException([params])
    
    # TODO: Enable enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonEmptyPackageWithSequence(self, useApikey):
        """Tests if functions_delete_package deletes uploaded package that is not empty and has a sequence."""

        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', self.package, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl]

        responseJson = self._uploadPackage()
        if 'error' in responseJson:
            pytest.fail(responseJson['error'])

        functionsDir = os.path.join(self.dataBasePath, 'example_functions')
        functionFiles = [os.path.join(functionsDir, f) for f in os.listdir(functionsDir)]

        # Iterate over the cloud functions and upload them
        for fileName in functionFiles:
            funcName = os.path.basename(fileName)
            functionUrl = self.actionsUrl + self.package + '/' + funcName + '?overwrite=true'

            content = open(fileName, 'r').read()
            payload = {'exec': {'kind': 'python', 'binary': False, 'code': content}}
            # Upload the cloud function
            response = requests.put(functionUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'},
                                    data=json.dumps(payload), verify=False)
            responseJson = response.json()
            if 'error' in responseJson:
                pytest.fail(responseJson['error'])
        
        sequenceUrl = self.actionsUrl + self.package + '/testSequence?overwrite=true'
        # fully qualified names
        functionNames = [f"/{self.namespace}/{self.package}/{os.path.basename(fileName)}" for fileName in functionFiles]
        payload = {'exec': {'kind': 'sequence', 'binary': False, 'components': functionNames}}
        # Connect the functions into a sequence
        response = requests.put(sequenceUrl, auth=(self.username, self.password), headers={'Content-Type': 'application/json'},
                                    data=json.dumps(payload), verify=False)
        responseJson = response.json()

        if 'error' in responseJson:
            pytest.fail(responseJson['error'])
        
        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])
        # delete package
        self.t_noException([params])
    
    # TODO: Enable enable apikey/username+password testing in Nightly builds
    #@pytest.mark.parametrize('useApikey', [True, False])
    @pytest.mark.parametrize('useApikey', [True])
    def test_deleteNonexistentPackage(self, useApikey):
        """Tests if functions_delete_package errors while deleting nonexistent package."""

        randomName = str(uuid.uuid4())
        params = ['-c', os.path.join(self.dataBasePath, 'exampleFunctions.cfg'),
                '--cloudfunctions_package', randomName, '--cloudfunctions_namespace', self.urlNamespace,
                '--cloudfunctions_url', self.cloudFunctionsUrl]

        if useApikey:
            params.extend(['--cloudfunctions_apikey', self.apikey])
        else:
            params.extend(['--cloudfunctions_username', self.username, '--cloudfunctions_password', self.password])
        # Fail 
        self.t_exitCode(1, [params])
        