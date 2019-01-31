import json
import sys
import os.path
from deepdiff import DeepDiff

if len(sys.argv) != 3:
    print('Provide two arguments, input and output dialogs jsons, for comparison.')
    exit(1)

inputpath = sys.argv[1]
outputpath = sys.argv[2]

if not os.path.isfile(inputpath):
    print('Input dialog json does not exist.')
    exit(1)

if not os.path.isfile(outputpath):
    print('Output dialog json does not exist.')
    exit(1)

with open(inputpath) as f:
    dialog_input_unsorted = json.load(f)

with open(outputpath) as g:
    dialog_output_unsorted = json.load(g)

assertEqual(DeepDiff(dialog_input_unsorted, dialog_output_unsorted, ignore_order=True), {})
