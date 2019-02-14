"""
Copyright 2018 IBM Corporation
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
from __future__ import print_function

import os, json, sys, argparse, requests, configparser
from wawCommons import printf, eprintf
from cfgCommons import Cfg
import datetime

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3

def checkErrorsInResponse(responseJson):
    # check errors
    if 'error' in responseJson:
        eprintf('ERROR: %s (code %s)\n', responseJson['error'], responseJson['code'])
        if 'errors' in responseJson:
            for errorJson in responseJson['errors']:
                eprintf('\t path: \'%s\' - %s\n', errorJson['path'], errorJson['message'])
#        if VERBOSE: eprintf("INFO: WORKSPACE: %s\n", json.dumps(workspace, indent=4))
        return 1
    else:
        return 0

if __name__ == '__main__':
    print('STARTING: ' + os.path.basename(__file__) + '\n')
    parser = argparse.ArgumentParser(description='Deploys  workspace in json format to Watson Conversation Service.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-of', '--common_outputs_directory', required=False, help='directory where the otputs are stored')
    parser.add_argument('-ow', '--common_outputs_workspace', required=False, help='name of the json file with workspace')
    parser.add_argument('-c', '--common_configFilePaths', help='configuaration file', action='append')
    parser.add_argument('-oc', '--common_output_config', help='output configuration file')
    parser.add_argument('-cu','--conversation-url', required=False, help='url of the conversation service API')
    parser.add_argument('-cv','--conversation_version', required=False, help='version of the conversation service API')
    parser.add_argument('-cn','--conversation_username', required=False, help='username of the conversation service instance')
    parser.add_argument('-cp','--conversation_password', required=False, help='password of the conversation service instance')
    parser.add_argument('-cid','--conversation_workspace_id', required=False, help='workspace_id of the application. If a workspace id is provided, previous workspace content is overwritten, otherwise a new workspace is created ')
    parser.add_argument('-wn','--conversation_workspace_name', required=False, help='name of the workspace')
    parser.add_argument('-v','--common_verbose', required=False, help='verbosity', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    config = Cfg(args)
    VERBOSE = hasattr(config, 'common_verbose')

    # workspace info
    if not hasattr(config, 'common_outputs_directory') or not getattr(config, 'common_outputs_directory'):
        print('ERROR: common_outputs_directory parameter not defined.')
        exit(1)
    if not hasattr(config, 'common_outputs_workspace') or not getattr(config, 'common_outputs_workspace'):
        print('ERROR: common_outputs_workspace parameter not defined.')
        exit(1)
    try:
        workspaceFilePath = os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_workspace'))
        with open(workspaceFilePath, 'r') as workspaceFile:
            workspace = json.load(workspaceFile)
    except IOError:
        eprintf('ERROR: Cannot load workspace file %s\n', workspaceFilePath)
        sys.exit(1)
    # workspace name
    if hasattr(config, 'conversation_workspace_name'):
        workspace['name'] = getattr(config, 'conversation_workspace_name')
    else:
        print('WARNING: conversation_workspace_name parameter not defined')
    # workspace language
    if hasattr(config, 'conversation_language'):
        workspace['language'] = getattr(config, 'conversation_language')
    else:
        print('WARNING: conversation_language parameter not defined')

    # credentials (required)
    if not hasattr(config, 'conversation_username') or not getattr(config, 'conversation_username'):
        print('ERROR: conversation_username parameter not defined.')
        exit(1)
    username = getattr(config, 'conversation_username')
    if not hasattr(config, 'conversation_password') or not getattr(config, 'conversation_password'):
        print('ERROR: conversation_password parameter not defined.')
        exit(1)
    password = getattr(config, 'conversation_password')
    # url (required)
    if not hasattr(config, 'conversation_url') or not getattr(config, 'conversation_url'):
        print('ERROR: con_url parameter not defined.')
        exit(1)
    workspacesUrl = getattr(config, 'conversation_url')
    # version (required)
    if not hasattr(config, 'conversation_version') or not getattr(config, 'conversation_version'):
        print('ERROR: conversation_version parameter not defined.')
        exit(1)
    version = getattr(config, 'conversation_version')
    # workspace id
    if not hasattr(config, 'conversation_workspace_id') or not getattr(config, 'conversation_workspace_id'):
        print('INFO: conversation_workspace_id parameter not defined.')
        workspaceId = ""
    else:
        print('INFO: conversation_workspace_id defined.')
        workspaceId = getattr(config, 'conversation_workspace_id')

    # workspace name unique
    if hasattr(config, 'conversation_workspace_name_unique') and getattr(config, 'conversation_workspace_name_unique') in ["true", "True"]:
        if hasattr(config, 'conversation_workspace_name') and getattr(config, 'conversation_workspace_name'):
            print('INFO: conversation_workspace_name set to unique')
            workspaceName = getattr(config, 'conversation_workspace_name')

            # get all workspaces with this name
            requestUrl = workspacesUrl + '?version=' + version
            printf("request url: %s\n", requestUrl)
            response = requests.get(requestUrl, auth=(username, password))
            responseJson = response.json()
            if VERBOSE: printf("\nINFO: response: %s\n", responseJson)
            if checkErrorsInResponse(responseJson) == 0:
                if VERBOSE: printf('INFO: Workspaces successfully retrieved.\n')
            else:
                eprintf('ERROR: Cannot retrieve workspaces.\n')
                sys.exit(1)

            sameNameWorkspace = None
            for workspace in responseJson['workspaces']:
                print("workspace name: " + workspace['name'] + "\n")
                if workspace['name'] == workspaceName:
                    print("same\n")
                    if sameNameWorkspace is None:
                        sameNameWorkspace = workspace
                    else:
                        # if there is more than one workspace with the same name -> error
                        eprintf('ERROR: There are more than one workspace with this name, do not know which to update.')
                        exit(1)
            if sameNameWorkspace is None:
                # workspace with the same name not found
                eprintf('ERROR: There is no workspace with this name.')
                exit(1)

            # just one workspace with this name -> get its id
            workspaceId = sameNameWorkspace['workspace_id']

        else: # workspace name unique and not defined or empty
            eprintf('ERROR: conversation_workspace_name set to unique and not defined.')
            exit(1)

    else: # workspace name not unique
        print("INFO: Workspace name doesn't have to be unique")

    if workspaceId:
        print('INFO: Updating existing workspace.')
    else:
        print('INFO: Creating new workspace.')

    requestUrl = workspacesUrl + '/' + workspaceId + '?version=' + version

    # create/update workspace
    response = requests.post(requestUrl, auth=(username, password), headers={'Content-Type': 'application/json'}, data=json.dumps(workspace, indent=4))
    responseJson = response.json()

    if VERBOSE: printf("\nINFO: response: %s\n", responseJson)
    if checkErrorsInResponse(responseJson) == 0:
        printf('INFO: Workspace successfully uploaded.\n')
    else:
        printf('ERROR: Cannot upload workspace.\n')
        sys.exit(1)

    if not hasattr(config, 'conversation_workspace_id') or not getattr(config, 'conversation_workspace_id'):
        setattr(config, 'conversation_workspace_id', responseJson['workspace_id'])
        printf('WCS WORKSPACE_ID: %s\n', responseJson['workspace_id'])
    if hasattr(config, 'common_output_config'):
        config.saveConfiguration(getattr(config, 'common_output_config'))

    if hasattr(config, 'context_client_name'):
        # Assembling uri of the client
        clientv2URL='https://clientv2-latest.mybluemix.net/#defaultMinMode=true'
        clientv2URL+='&prefered_workspace_id=' + getattr(config, 'conversation_workspace_id')
        clientv2URL+='&prefered_workspace_name=' + getattr(config, 'conversation_workspace_name')
        clientv2URL+='&shared_examples_service=&url=http://zito.mybluemix.net'
        clientv2URL+='&username=' + getattr(config, 'conversation_username')
        clientv2URL+='&custom_ui.title=' + getattr(config, 'conversation_workspace_name')
        clientv2URL+='&password=' + getattr(config, 'conversation_password')
        clientv2URL+='&custom_ui.machine_img='
        clientv2URL+='&custom_ui.user_img='
        clientv2URL+='&context.user_name=' + getattr(config, 'context_client_name')
        clientv2URL+='&context.link_build_date=' + unicode(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
        clientv2URL+='&prefered_tts=none'
        clientv2URL+='&bluemix_tts.username=xx'
        clientv2URL+='&bluemix_tts.password=xx'
        clientv2URL+='&compact_mode=true'
        clientv2URL+='&compact_switch_enabled=true'
        clientv2URL+='developer_switch_enabled=false'
        printf('clientv2URL=%s\n', clientv2URL)

    # create file with automatic redirect
    if hasattr(config, 'common_outputs_client') and getattr(config, 'common_outputs_client'):
        clientFilePath = os.path.join(getattr(config, 'common_outputs_directory'), getattr(config, 'common_outputs_client'))
        try:
            with open(clientFilePath, "w") as clientFile:
                clientFile.write('<meta http-equiv="refresh" content=\"0; url=' + clientv2URL + '\" />')
                clientFile.write('<p><a href=\"' + clientv2URL + '\">Redirect</a></p>')
            clientFile.close()
        except IOError:
            eprintf('ERROR: Cannot write to %s\n', clientFilePath)
            sys.exit(1)

    print('\nFINISHING: '+ os.path.basename(__file__) + '\n')
