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

import sys

import deprecation

import workspace_test_evaluate
from _version import __version__


@deprecation.deprecated(deprecated_in='2.2', removed_in='2.6', current_version=__version__, details='Use the workspace_test_evaluate.py script / main function instead.')
def main(argv):
    workspace_test_evaluate.main(argv)

if __name__ == '__main__':
    main(sys.argv[1:])
