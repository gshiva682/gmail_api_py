import mysql.connector
import json
import re
from datetime import datetime, timedelta
import calendar
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']

def cred_obj():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def predicate_equals(r, mail):
   field_index = {"message_id":1,"From":2, "To":3, "Subject":4, "Date":5}
   if mail[field_index[r['field']]].lower()==r['value'].lower():
       return 1
   return 0

def predicate_contains(r, mail):
    field_index = {"message_id":1,"From":2, "To":3, "Subject":4, "Date":5}   
    x = re.findall(r['value'].lower(), mail[field_index[r['field']]].lower())
    if x:
        return 1
    return 0

def predicate_less_than(r, mail):
    field_index = {"message_id":1,"From":2, "To":3, "Subject":4, "Date":5}
    months = dict((month, index) for index, month in enumerate(calendar.month_abbr) if month)
    
    d = mail[5].split()
    try:
        mail_date = datetime(int(d[3]), months[d[2]], int(d[1]))
    except:
        mail_date = datetime(int(d[2]), months[d[1]], int(d[0]))
    today_date = datetime.now()
    diff = today_date - mail_date
    if diff < timedelta(days=int(r['value'])):
        return 1
    return 0

def process_actions(actions,removeLabelIds,addLabelIds):
    for i in actions:
        if(i['action']=='mark'):
            removeLabelIds.append("UNREAD" if i["value"]=="read" else "READ")
    print(removeLabelIds,addLabelIds)
    return 0

service = build('gmail', 'v1', credentials=cred_obj())
db = mysql.connector.connect(host="localhost",user="root",password="",database="emailDB",auth_plugin='mysql_native_password',charset='utf8mb4',collation='utf8mb4_unicode_ci')
cur = db.cursor()

with open("rules.json","r") as f:
    rules = json.load(f)

json_obj={"removeLabelIds": ["UNREAD"],"addLabelIds": []}
cur.execute("SELECT * FROM mails")
result = cur.fetchall()
removeLabelIds=[]
addLabelIds=[] 
action=rules['actions'] 
process_actions(action,removeLabelIds,addLabelIds)
for mail in result:
    #print(mail)
    l=[]
    for r in rules['rules']:
        if r['predicate']=="equals":
            l.append(predicate_equals(r, mail))
        if r['predicate']=="contains":
            l.append(predicate_contains(r, mail))
        if r['predicate']=="less_than":
            l.append(predicate_less_than(r, mail))
    if l.count(1)==len(l) and rules['predicate']=='all':
        service.users().messages().modify(userId='me',id="18801d91cd0f45af",body=json_obj).execute()
    elif l.count(1)>=1 and rules['predicate']=='any':
        print(mail[1],mail)
