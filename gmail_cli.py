import argparse
import httplib2
import sys
import os

import oauth2client
from oauth2client import tools
from oauth2client import client
from apiclient import discovery

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import base64

from apiclient import errors
from apiclient.discovery import build


CLIENT_SECRET_FILE = 'client_id.json'
SCOPES = 'https://mail.google.com/'
APPLICATION_NAME = 'GMail CLI'


def getCredentials(flags):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail_cli.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    
    if not credentials or credentials.invalid:
        
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials


def createMessage(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64 encoded email object.
    """
    message = MIMEText(message_text)
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject
    return {'raw': base64.b64encode(message.as_string())}


def createMessageWithAttachment(sender, to, subject, message_text, filepath):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file_dir: The directory containing the file to be attached.
    filename: The name of the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    # path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(filepath)
    filename = os.path.basename(filepath)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    
    main_type, sub_type = content_type.split('/', 1)
    
    if main_type == 'text':
        fp = open(filepath, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    
    elif main_type == 'image':
        fp = open(filepath, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    
    elif main_type == 'audio':
        fp = open(filepath, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    
    else:
        fp = open(filepath, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def process(flags):
    
    credentials = getCredentials(flags)
    http = credentials.authorize(httplib2.Http())
    service = build('gmail', 'v1', http=http)
    
    print flags.action

    if flags.action == 'save':
        
        if flags.attachments.lower() == 'none':
            message_body = createMessage('gunjal.varad@gmail.com', flags.recipient, flags.subject, flags.message_text)
            
            try:
                msg = {'message': message_body}
                m = service.users().drafts().create(userId='me', body=msg).execute()
                print 'Message Id: %s' % m['id']
                return m
            
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
            
        else:
            message_body = createMessageWithAttachment('gunjal.varad@gmail.com', flags.recipient, flags.subject, flags.message_text, 
                                        flags.attachments)
            
            try:
                msg = {'message': message_body}
                m = service.users().drafts().create(userId='me', body=msg).execute()
                print 'Message Id: %s' % m['id']
                return m
            
            except errors.HttpError, error:
                print 'An error occurred: %s' % error


    elif flags.action == 'send':

        if flags.attachments.lower() == 'none':
            message_body = createMessage('gunjal.varad@gmail.com', flags.recipient, flags.subject, flags.message_text)

            try:
                m = service.users().messages().send(userId='me', body=message_body).execute()
                print 'Message Id: %s' % m['id']
                return m
            
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
        
        else:
            message_body = createMessageWithAttachment('gunjal.varad@gmail.com', flags.recipient, flags.subject, flags.message_text,
                                        flags.attachments)

            try:
                m = service.users().messages().send(userId='me', body=message_body).execute()
                print 'Message Id: %s' % m['id']
                return m
            
            except errors.HttpError, error:
                print 'An error occurred: %s' % error


    else:
        print 'Please input a valid action'
            


def main(argv):
    
    # Weird handling of argparse by GMail API. Can't parse CL arguments separately. Just define them. 
    # Parsing is done within parent tools.argparser 

    parser = argparse.ArgumentParser(parents=[tools.argparser], add_help=False)
    group = parser.add_argument_group('standard')

    parser.add_argument("-to", "--recipient", required=True, help="Recipients")
    parser.add_argument("-sub", "--subject", help="Subject")
    parser.add_argument("-msg", "--message_text", help="Text Body")
    parser.add_argument("-act", "--action", help="Action")
    parser.add_argument("-attach", "--attachments", help="Files to be attached")

    flags = parser.parse_args(argv[1:])
    process(flags)

if __name__ == '__main__':
    main(sys.argv)
    
