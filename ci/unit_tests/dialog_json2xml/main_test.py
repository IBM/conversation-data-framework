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

import os

from lxml import etree


import dialog_json2xml

from ...test_utils import BaseTestCaseCapture


# From # http://doc.pytest.org/en/latest/example/parametrize.html#parametrizing-test-methods-through-per-class-configuration
def pytest_generate_tests(metafunc):
    # called once per each test function
    funcname = metafunc.function.__name__
    if funcname in metafunc.cls.params:
        funcarglist = metafunc.cls.params[metafunc.function.__name__]
        argnames = sorted(funcarglist[0])
        metafunc.parametrize(
            argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
        )


class TestMain(BaseTestCaseCapture):

    dataBasePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'main_data')
    testOutputPath = os.path.join(dataBasePath, 'outputs')

    # a map specifying multiple argument sets for a test method
    params = {
        "test_validToXmlTransformation": [{'category': 'Actions'},
                                          {'category': 'Bool'},
                                          {'category': 'NodeTypes'},
                                          {'category': 'Slots'}]
    }

    @classmethod
    def setup_class(cls):
        ''' Setup any state specific to the execution of the given class (which usually contains tests). '''
        # create output folder
        BaseTestCaseCapture.createFolder(TestMain.testOutputPath)

    def callfunc(self, *args, **kwargs):
        dialog_json2xml.main(*args, **kwargs)

    def _assertXmlEqual(self, xml1path, xml2path):
        """Tests if two xml files are equal."""
        with open(xml1path, 'r') as xml1File:
            xml1 = etree.XML(xml1File.read(), etree.XMLParser(remove_blank_text=True))
            for parent in xml1.xpath('//*[./*]'):  # Search for parent elements
                parent[:] = sorted(parent, key=lambda x: x.tag)
        # with open(xml2path, 'r') as xml2File:
        #     print(f'{xml2File.read()}')
        with open(xml2path, 'r') as xml2File:
            xml2 = etree.XML(xml2File.read(), etree.XMLParser(remove_blank_text=True))
            for parent in xml2.xpath('//*[./*]'):  # Search for parent elements
                parent[:] = sorted(parent, key=lambda x: x.tag)

        assert etree.tostring(xml1, encoding=str, pretty_print=True) == \
               etree.tostring(xml2, encoding=str, pretty_print=True)

    def test_validToXmlTransformation(self, category):
        """Tests if the script successfully completes with valid input file"""
        inputFileName = 'input' + category + 'Valid.json'
        expectedFileName = 'expected' + category + 'Valid.xml'
        inputJsonPath = os.path.abspath(os.path.join(self.dataBasePath, inputFileName))
        expectedXmlPath = os.path.abspath(os.path.join(self.dataBasePath, expectedFileName))

        outputXmlDirPath = os.path.join(self.testOutputPath, 'outputActionsValidResult')
        outputXmlPath = os.path.join(outputXmlDirPath, 'dialog.xml')

        BaseTestCaseCapture.createFolder(outputXmlDirPath)

        self.t_noException([[inputJsonPath, '-d', outputXmlDirPath]])
        self._assertXmlEqual(expectedXmlPath, outputXmlPath)
