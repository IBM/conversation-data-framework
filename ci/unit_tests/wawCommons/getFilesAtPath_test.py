
import os

import wawCommons
 
def test_getFilesAtPath():
    directory = '../tests/test_data' 
    pathList = wawCommons.getFilesAtPath([directory])
    testFile = os.path.abspath(os.path.join(directory, "text2codeExample-en.xml"))
    assert testFile in pathList
    