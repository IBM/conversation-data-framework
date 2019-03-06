
import os, unittest, sys, codecs, json

import workspace_addjson

class TestMain(unittest.TestCase):

    ''' Tests if particular file is found by getFilesAtPath function '''
    def test_main(self):

        cmd = 'cp ./tests/test_data/workspace.json ./tests/test_data/workspace_forAddJsonTest.json'
        os.system(cmd)

        workspaceFile = 'workspace_forAddJsonTest.json'
        directory = './tests/test_data/'
        jsonAddPath = './tests/test_data/jsonToAdd.json'
        targetNode = 'parent'
        referenceResult = './tests/test_data/workspace_result.json'

        workspace_addjson.main(['-w', workspaceFile, '-d', directory , '-j', jsonAddPath, '-t', targetNode, '-v'])

        # compare the new result with the reference result
        with codecs.open(os.path.join(directory, workspaceFile), 'r', encoding='utf8') as inputpath:
            newWorkspace = json.load(inputpath)

        with codecs.open(os.path.join(referenceResult), 'r', encoding='utf8') as inputpath:
            referenceWorkspace = json.load(inputpath)

        referenceWorkspaceString = json.dumps(referenceWorkspace)
        newWorkspaceString = json.dumps(newWorkspace)

        assert referenceWorkspaceString == newWorkspaceString
