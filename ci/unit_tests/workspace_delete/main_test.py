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

import json, os, pytest, requests, shutil, unittest, argparse

import workspace_delete, workspace_deploy, wawCommons
from cfgCommons import Cfg
from wawCommons import getWorkspaces, getRequiredParameter
from ...test_utils import BaseTestCaseCapture


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    outputPath = os.path.join(dataBasePath, 'outputs')
    jsonWorkspaceFilename = 'skill-Customer-Care-Sample-Skill.json'
    jsonWorkspacePath = os.path.abspath(os.path.join(dataBasePath, jsonWorkspaceFilename))
    workspacesUrl = 'https://gateway.watsonplatform.net/conversation/api/v1/workspaces'
    version = '2017-02-03'

    def setup_class(cls):
        BaseTestCaseCapture.createFolder(cls.outputPath)
        BaseTestCaseCapture.checkEnvironmentVariables(['WA_USERNAME', 'WA_PASSWORD'])
        cls.username = os.environ['WA_USERNAME']
        cls.password = os.environ['WA_PASSWORD']

        cls.deployParamsBase = ['-of', cls.dataBasePath, '-ow', cls.jsonWorkspaceFilename,\
         '-cn', cls.username, '-cp', cls.password, '-cu', cls.workspacesUrl, '-cv', cls.version, '-v']

        cls.deleteParamsBase = [\
         '-cn', cls.username, '-cp', cls.password, '-cu', cls.workspacesUrl, '-cv', cls.version, '-v']

    def callfunc(self, *args, **kwargs):
        workspace_delete.main(*args, **kwargs)

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteById(self, envVarNameUsername, envVarNamePassword):
        """Tests if workspace can be deleted by its id."""

        # use outputPath instead of dataBasePath when workspace_deploy script will be able to take workspace
        # and config file from different directories (workspace should be taken from
        # dataBasePath and config should be saved to outputs directory)
        createOutputConfigFilename = 'createWorkspaceOutput.cfg'
        createOutputConfigPath = os.path.abspath(os.path.join(self.dataBasePath, createOutputConfigFilename))
        deleteOutputConfigFilename = 'deleteWorkspaceOutput.cfg'
        deleteOutputConfigPath = os.path.abspath(os.path.join(self.dataBasePath, deleteOutputConfigFilename))

        # deploy test workspace
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['-oc', createOutputConfigPath])
        workspace_deploy.main(deployParams)

        # try to delete workspace by its id (id is obtained from output config of deploy script)
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['-c', createOutputConfigPath, '-oc', deleteOutputConfigPath])
        self.t_noException([deleteParams])

        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
        parser.add_argument('-oc', '--common_output_config', help='output configuration file')
        parser.add_argument('-cu','--conversation_url', required=False, help='url of the conversation service API')
        parser.add_argument('-cv','--conversation_version', required=False, help='version of the conversation service API')
        parser.add_argument('-cn','--conversation_username', required=False, help='username of the conversation service instance')
        parser.add_argument('-cp','--conversation_password', required=False, help='password of the conversation service instance')
        parser.add_argument('-cid','--conversation_workspace_id', required=False, help='workspace_id of the application.')
        parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of the workspace')
        parser.add_argument('-wnm','--conversation_workspace_match_by_name', required=False, help='true if the workspace name should be matched by name (or pattern if defined)')
        parser.add_argument('-wnp','--conversation_workspace_name_pattern', required=False, help='regex pattern specifying a name of workspaces to be deleted')
        parser.add_argument('-v','--verbose', required=False, help='verbosity', action='store_true')
        args = parser.parse_args(deleteParams)
        deleteInputConfig = Cfg(args)

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace with id specified in config file
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['workspace_id'] == getRequiredParameter(deleteInputConfig, 'conversation_workspace_id'):
                workspacesFound += 1

        assert workspacesFound == 0

        # check if workspace_id is not present in the output config
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
        args = parser.parse_args(['-c', deleteOutputConfigPath])
        deleteOutputConfig = Cfg(args)

        assert hasattr(deleteOutputConfig, 'conversation_workspace_id') == False

    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteByName(self, envVarNameUsername, envVarNamePassword):
        """Tests if workspace can be deleted by its id."""

        workspaceName = 'deleteByName_workspace'

        # deploy test workspace
        deployParams = list(self.deployParamsBase)
        deployParams.extend(['-wn', workspaceName])
        workspace_deploy.main(deployParams)

        # try to delete workspace by its id (id is obtained from output config of deploy script)
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['-wn', workspaceName, '-wnm', 'true'])
        self.t_noException([deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace with specified name in config file
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['name'] == workspaceName:
                workspacesFound += 1

        assert workspacesFound == 0

    @pytest.mark.parametrize('envVarNameUsername, envVarNamePassword', [('WA_USERNAME', 'WA_PASSWORD')])
    def test_deleteMoreWithRegex(self, envVarNameUsername, envVarNamePassword):
        """Tests if workspace can be deleted by its id."""

        workspaceName1 = 'regexp_workspace_1'
        workspaceName2 = 'regexp_workspace_2'
        workspaceNameNM = 'non-matching_workspace'

        # deploy test workspaces
        deployParams1 = list(self.deployParamsBase)
        deployParams1.extend(['-wn', workspaceName1])
        workspace_deploy.main(deployParams1)
        deployParams2 = list(self.deployParamsBase)
        deployParams2.extend(['-wn', workspaceName2])
        workspace_deploy.main(deployParams2)
        deployParamsNM = list(self.deployParamsBase)
        deployParamsNM.extend(['-wn', workspaceNameNM])
        workspace_deploy.main(deployParamsNM)

        # try to delete workspace by its id (id is obtained from output config of deploy script)
        deleteParams = list(self.deleteParamsBase)
        deleteParams.extend(['-wnm', 'true', '-wnp', 'regexp_*'])
        self.t_noException([deleteParams])

        workspaces = getWorkspaces(self.workspacesUrl, self.version, self.username, self.password)

        # there should be no workspace with name matching specified regex
        workspacesFound = 0
        for workspace in workspaces:
            if workspace['name'] == workspaceName1 or workspace['name'] == workspaceName2:
                workspacesFound += 1

        assert workspacesFound == 0

        # there should be still workspace with non-matching name
        NMworkspacesFound = 0
        for workspace in workspaces:
            if workspace['name'] == workspaceNameNM:
                NMworkspacesFound += 1

        assert NMworkspacesFound == 1
