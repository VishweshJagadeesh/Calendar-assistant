from langchain.agents import Tool
from datetime import datetime

import os
import datetime 
import httplib2
import socket
from google.auth.exceptions import TransportError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain.agents import Tool

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar"
]


def main():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    return service

    # Call the Calendar API
    
  except HttpError as error:
    print(f"An error occurred: {error}")
  except httplib2.ServerNotFoundError as e:
    print("Server not found. Please check your internet connection:", e)
  except socket.gaierror as e:
    print("Network error: Unable to resolve host. Check your connection.", e)
  except TransportError as e:
    print("Transport error: Possible network issue.", e)
  except Exception as e:
    print("An unexpected error occurred:", e)

def get_current_time(_: str = "") -> str:
    return str(datetime.datetime.now())

def get_time_tools():
    return Tool(
            name="Current Time",
            func=get_current_time,
            description="Returns the current system time. Use this to get the current date and time in iso format. This is used to get the start and end time of the event. The time zone is 'Asia/Kolkata' unless specified."
        )
    
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: dict = Field(
        ...,
        description='''
        Given a user prompt extract information in this form
        {'summary': title,
  'location': location,
  'description': description,
  'start': {
    'dateTime': start_datetime,
    'timeZone': timezone,
  },
  'end': {
    'dateTime': end_datetime,
    'timeZone': timezone,
  },
  'attendees': [
    {'email': 'example1@example.com'},
    {'email': 'example2@example.com'},
  ],
  'reminders': {
    'useDefault': True,
  },}
    so that it can be used to add an event to the user's google calendar. Make sure the summary,start_datetime,end_datetime are providede and ask for them if not, make sure the date time is in iso format use the get_time_tools() to get today's date and time and the time zone is 'Asia/Kolkata' unless specified''')

from langchain_groq import ChatGroq
key="Groq_API_Key"
llm=ChatGroq(groq_api_key=key,model_name="llama-3.3-70b-versatile")
tools=[get_time_tools()]
llm=llm.bind_tools(tools)
structured_llm_router = llm.with_structured_output(RouteQuery)
system = """You are an expert at Adding events to a calendar and figuring out the current date in iso format.
The Calendar can be editted to add update and remove existing records can can be read to."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
question_router = route_prompt | structured_llm_router


def add_event(_: str = "") -> str:
    source = question_router.invoke(
        {'question': _}
    )
    service=main()
    event=service.events().insert(calendarId='primary', body=source.datasource).execute()
    return ('Event created: %s' % (event.get('htmlLink')))

def add_event_tool():
    return Tool(
            name="add Event",
            func=add_event,
            description="Adds an event to the calendar. Provide the title, start_datetime, end_datetime make sure the start time and end time are strings in iso form, to get todays date use the Current time tool. location,description, recurrance, atendees are optional. and call the add_event function with these values."
        )

def first10events(_: str = "") -> dict:
  service=main()
  try:
    now = datetime.datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
    
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      return ("No upcoming events found.")
      

    # Prints the start and name of the next 10 events
    l,c={},1
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      end=event["end"].get("dateTime", event["end"].get("date"))
      l[c]=(
          event["summary"],start,end)
      c+=1
    
    return l
  except:
    return "An error occurred while fetching events."

def get_event_tool():
    return Tool(
            name="get Events",
            func=first10events,
            description="Returns the the next 10 events in the calendar. Events are arranged as ('event name','start time','end time') in a dictonary with a number as a key. Use this to answer questions about the upcomming events in the calendar."
        )
