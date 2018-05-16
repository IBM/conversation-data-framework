# watson-assistant-workbench
WAW is a toolkit for maintaining Watson Assistant data in github repository.
It aims at 
- structured data-driven approach, with easy diffs visible in GitHub
- easy collaboration among large teams
- improved dialog tree representation resulting in greater readability and easier updates compared to the original WA JSON format
- easy-to-use XML format and tools that make authoring of Watson Conversation workspaces easier using standard text editors
- ability to easily include and combine pieces of dialog together
- full compatibility with the WA JSON workspace format
- easy Continuous Integration - each commit to GitHub runs tests and updates conversation workspace if all succeed
- automatic dialog code generation (go back, abort, etc. - actions needed in each dialog step)
- support for internationalization
- and more :)

It countains a bundle of tools for generating WA workspace from the structure data (and viceversa), testing and uploading (working with the WCS API).

Currently supported conversation version is 2017-02-03 except:
- Fuzzy matching, Folders, Digression and Pattern defined entities are not supported.
- A name of a dialog node still has to be unique as it is used as node ID.
- Missing "slot_in_focus" property.
- Slots and are not supported in json to xml conversion scripts.

Scripts use python 2.7

Please install following python modules: configparser, openpyxl, cryptography, unidecode, requests

For brief summary how to run scripts please see scripts.md.

Description of dialog T2C and xml WAW format is placed in doc folder as well as description of entity and intent csv format.
