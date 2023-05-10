from __future__ import print_function

import os.path
import mysql.connector

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me',labelIds='INBOX',maxResults=100).execute()
        messages = result.get('messages')
        db = mysql.connector.connect(host="localhost",user="root",password="",database="emailDB",auth_plugin='mysql_native_password',charset='utf8mb4',collation='utf8mb4_unicode_ci')
        cur = db.cursor()
        cnt=1
        l=[]
        for msg in messages:
            result = service.users().messages().get(userId='me',id=msg.get('id')).execute()
            labels=result['labelIds']
            headers=result['payload']['headers'] 
            data={'s_no':cnt,'message_id':msg.get('id')}
            for key in headers:
                if(key['name']=='Subject' or key['name']=='From' or key['name']=="To" or key['name']=="Date"):
                    if(len(key['value'])>60):key['value']=key['value'][:60]+"..."
                    data[key['name']] = key['value']
            data['labels']=(',').join(labels) 
            l.append(data)      
            cnt+=1

        querry = "INSERT INTO mails VALUES(%s,%s,%s,%s,%s,%s,%s)"
        for i in l:
            val=(i['s_no'],i['message_id'],i['From'],i['To'],i['Subject'],i['Date'],i['labels'])
            cur.execute(querry,val)
        db.commit()
        print("Emails Fetched")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()