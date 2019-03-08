
import os, unittest, sys, codecs, json

import workspace_addjson

class TestIncludeJson(unittest.TestCase):

    def test_addingJsonDictionary(self):
        ''' Tests for including additional json dictionary to arbitrary location in dialog nodes '''

        nodeJSON = {
            "a" : "b"
        }
        keyJSON = "c"
        keySearch = "a"
        includeJSON = {
            "x" : "y"
        }

        resultJSON = nodeJSON

        workspace_addjson.includeJson(nodeJSON, keyJSON, keySearch, includeJSON)

        assert resultJSON == nodeJSON

    # TODO write more tests
    # keyJSON = None
    # keyJSON = "value"
