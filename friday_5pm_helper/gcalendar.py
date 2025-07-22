from __future__ import print_function
import httplib2
import sys

from apiclient import discovery
from datetime import datetime
from dateutil.parser import isoparse

from friday_5pm_helper import (
    EXPECTED_DATETIME_FORMATS,
    TimeEntryData,
    worklog_time_spent
)
from friday_5pm_helper.credentials import get_credentials

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gsuite_utilities_gcalendar.json
LOCAL_CREDENTIAL_FILE = 'gsuite_utilities_gcalendar.json'
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret_gcalendar.json'
APPLICATION_NAME = 'G Suite Utilities'


class GCalendarClient():
    def __init__(self):
        """
        Creates a Google Calendar API service object
        :return: a Google Calendar API service object
        """
        credentials = get_credentials(
            LOCAL_CREDENTIAL_FILE,
            CLIENT_SECRET_FILE,
            SCOPES,
            APPLICATION_NAME
        )
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def gcalendar_events(self, start_date, end_date):
        """
        Outputs a list of the next 'max_results' events on the user's calendar.
        :param service: a Google Calendar API service object
        :return: a list
        """
        min_time = start_date.isoformat() + 'Z' # 'Z' indicates UTC time
        max_time = end_date.isoformat() + 'Z'
        eventsResult = self.service.events().list(
            calendarId='6b3f23202ff7b6b0312a9002ed6d79fe7bf3519c0bb70bbb34a67bdcf6f0c975@group.calendar.google.com',
            timeMin=min_time,
            timeMax=max_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return eventsResult.get('items', [])


def calc_interval(start_time, end_time):
    print(start_time, end_time)
    """
    :param start_time: start time in datetime
    :param end_time: end time in datetime
    :return: string hh:mm
    """
    try:
        start_dt = isoparse(start_time)
        end_dt = isoparse(end_time)
        t_delta_secs = (end_dt - start_dt).seconds
        return (worklog_time_spent(t_delta_secs), start_dt, end_dt)
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return None


def retrieve_gcalendar_event_data(start_date, end_date, tasks_info):
    """
    Retrieve calendar events' data in TimeEntryData format
    :return: list of TimeEntryData
    """
    time_entry_data_list = []

    # see https://developers.google.com/google-apps/calendar/v3/reference/events/list
    for event in GCalendarClient().gcalendar_events(start_date, end_date):
        start_time_str = event['start'].get('dateTime', event['start'].get('date'))
        end_time_str = event['end'].get('dateTime', event['end'].get('date'))

        (interval, start, end) = calc_interval(start_time_str, end_time_str)

        time_entry_data_list.append(TimeEntryData(
            year=start.year,
            month=start.month,
            day=start.day,
            interval=interval,
            comment=event['summary'],
            taskid=tasks_info['InternalMeeting'],
            start_time=start,
            end_time=end
        ))

    return time_entry_data_list


if __name__ == '__main__':
    from friday_5pm_helper import start_and_end_of_week_of_a_day

    today = datetime.utcnow()
    (start_date, end_date) = start_and_end_of_week_of_a_day(today)

    ret = retrieve_gcalendar_event_data(start_date, end_date, tasks_info={'InternalMeeting':'123'})
    for i in ret:
        print(i)

    sys.exit(0)
