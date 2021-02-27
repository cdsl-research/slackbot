import datetime
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.events'
CAL_ID = os.environ.get("GOOGLE_CALENDAR_ID", None)
assert CAL_ID is not None, "Fail to get GOOGLE_CALENDAR_ID"


def dt_to_rfc3339(_dt: datetime) -> str:
    return _dt.strftime('%Y-%m-%dT%H:%M:%S+09:00')


def add(
    title: str,
    begin_date: datetime,
    end_date: datetime,
    # user_email: str
) -> str:
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    https://developers.google.com/calendar/quickstart/python
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    event = {
        'summary': title,
        'description': "Slack Botから追加．",
        # 'attendees': [
        #     {
        #         "email": user_email
        #     }
        # ],
        'start': {
            'dateTime': dt_to_rfc3339(begin_date),
            'timeZone': 'Asia/Tokyo',  # 1985-04-12T23:20:50.52Z
        },
        'end': {
            'dateTime': dt_to_rfc3339(end_date),
            'timeZone': 'Asia/Tokyo',  # 1985-04-12T23:20:50.52Z
        },
    }
    assert len(CAL_ID) > 20, "Invalid CAL_ID"
    result = service.events().insert(calendarId=CAL_ID, body=event).execute()
    return result.get('htmlLink')


if __name__ == "__main__":
    a = add(
        title="Test schdule",
        begin_date=datetime.datetime.now(),
        end_date=datetime.datetime.now() + datetime.timedelta(days=1),
        # user_email="user@example.com"
    )
    print(a)
