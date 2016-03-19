from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import os

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

CLIENT_SECRET_FILE = 'client_id.json'


def getCredentials(json_file_name, scopes, application_name):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   json_file_name)

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    
    if not credentials or credentials.invalid:
        
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scopes)
        flow.user_agent = application_name
        
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials