
import os, unittest, sys, codecs, json

import workspace_addjson

class TestMain(unittest.TestCase):


    def test_addingJsonDictionary(self):
        ''' Tests for including additional json dictionary to arbitrary location in dialog nodes '''

        cmd = 'cp ./ci/unit_tests/workspace_addjson/main_data/workspace.json ./ci/unit_tests/workspace_addjson/main_data/workspace_forAddJsonTest.json'
        os.system(cmd)

        workspaceFile = 'workspace_forAddJsonTest.json'
        directory = './ci/unit_tests/workspace_addjson/main_data/'
        jsonAddPath = './ci/unit_tests/workspace_addjson/main_data/jsonToAdd.json'
        targetNode = 'parent'
        referenceResult = './ci/unit_tests/workspace_addjson/main_data/workspace_result.json'

        workspace_addjson.main(['-w', workspaceFile, '-d', directory , '-j', jsonAddPath, '-t', targetNode, '-v'])

        # compare the new result with the reference result
        with codecs.open(os.path.join(directory, workspaceFile), 'r', encoding='utf8') as inputpath:
            newWorkspace = json.load(inputpath)

        with codecs.open(os.path.join(referenceResult), 'r', encoding='utf8') as inputpath:
            referenceWorkspace = json.load(inputpath)

        referenceWorkspaceString = json.dumps(referenceWorkspace)
        newWorkspaceString = json.dumps(newWorkspace)

        assert referenceWorkspaceString == newWorkspaceString


    def test_addingJsonArray(self):
        ''' Tests for including additional json array to arbitrary location in dialog nodes '''

        cmd = 'cp ./ci/unit_tests/workspace_addjson/main_data/workspace.json ./ci/unit_tests/workspace_addjson/main_data/workspace_forAddJsonTest.json'
        os.system(cmd)

        workspaceFile = 'workspace_forAddJsonTest.json'
        directory = './ci/unit_tests/workspace_addjson/main_data/'
        jsonAddPath = './ci/unit_tests/workspace_addjson/main_data/jsonToAdd_array.json'
        targetNode = 'parent'
        referenceResult = './ci/unit_tests/workspace_addjson/main_data/workspace_result_array.json'

        workspace_addjson.main(['-w', workspaceFile, '-d', directory , '-j', jsonAddPath, '-t', targetNode, '-v'])

        # compare the new result with the reference result
        with codecs.open(os.path.join(directory, workspaceFile), 'r', encoding='utf8') as inputpath:
            newWorkspace = json.load(inputpath)

        with codecs.open(os.path.join(referenceResult), 'r', encoding='utf8') as inputpath:
            referenceWorkspace = json.load(inputpath)

        referenceWorkspaceString = json.dumps(referenceWorkspace)
        newWorkspaceString = json.dumps(newWorkspace)

        assert referenceWorkspaceString == newWorkspaceString
