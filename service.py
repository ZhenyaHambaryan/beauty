from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pathlib

SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = None
BASE_DIR = str(pathlib.Path(__file__).parent.resolve())

if os.path.exists(BASE_DIR+'/token.json'):
      creds = Credentials.from_authorized_user_file(BASE_DIR+'/token.json', SCOPES)

if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
            try:
                  creds.refresh(Request())
            except:
                  os.unlink(BASE_DIR+'token.json')
      else:
            flow = InstalledAppFlow.from_client_secrets_file(BASE_DIR+'/google_client_secret.json', SCOPES)
            creds = flow.run_local_server(port=3000)
      with open(BASE_DIR+'/token.json', 'w') as token:
            token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)

def get_all_calendars():
      return service.calendarList().list().execute()

def create_new_calendar(name):
      calendar = {'summary': name}
      created_calendar = service.calendars().insert(body=calendar).execute()
      return created_calendar['id']

def create_event(body,calendar_id):
      event = service.events().insert(calendarId=calendar_id, body=body).execute()
      return event

def get_events(calendarId,min_date,max_date):
      events = service.events().list(calendarId=calendarId,
                              timeMin = min_date,
                              timeMax = max_date,
                              ).execute()
      return events

def get_all_events(calendarId):
      events = service.events().list(calendarId=calendarId).execute()
      return events

def delete_event(calendar_id,event_id):
      service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
      return True

def get_event_by_id(calendar_id,event_id):
      return service.events().get(calendarId=calendar_id, eventId=event_id).execute()

def get_event(calendar_id, event_id):
      return service.events().get(calendarId=calendar_id, eventId=event_id).execute()

def update_event(calendar_id,event_id,body):
      updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=body).execute()
      return updated_event
