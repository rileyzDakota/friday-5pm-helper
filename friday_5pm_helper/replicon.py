from __future__ import print_function
import sys

from datetime import datetime, timedelta

from friday_5pm_helper import (
    read_json,
    start_and_end_of_week_of_a_day,
    unique_unit_of_work_id
)
import friday_5pm_helper.gcalendar as g
import friday_5pm_helper.jira_checker as j
from friday_5pm_helper.replicon_services import service_defs
from friday_5pm_helper.replicon_services.client import RepliconClient

# Default replicon configs file (json)
REPLICON_CONFIGS_JSON = 'client_replicon_configs.json'

# Default client credentials file
REPLICON_JSON = 'client_secret_replicon.json'

# Need to change the account from SSO to Replicon account
# See https://www.replicon.com/help/what-account-should-we-use-for-integrations
# Arguments defined in the client credential file
ARG_COMPANY_KEY="company_key"
ARG_UNAME="login_name"
ARG_UPASS="login_pass"


def retrieve_user_data(start_date, end_date, tasks_info):
    """
    Retrieves user data from different sources.
    :return: a list of TimeEntryData
    """
    # Retrieve calendar events
    print('Retrieving Google Calendar events ...')
    time_entry_data_list = g.retrieve_gcalendar_event_data(start_date, end_date, tasks_info['calendar'])
    print('{} event found'.format(len(time_entry_data_list)))

    # print('Retrieving JIRA issues being updated since the start of the week ...')
    # time_entry_data_list_2 = j.retrieve_jira_issues_updated_since_start_of_week(start_date, end_date, tasks_info['jira'])
    # print('{} issues found'.format(len(time_entry_data_list_2)))

    return time_entry_data_list


def create_replicon_time_entries(replicon_client, time_entry_data_list):
    """
    :param replicon_client: a RepliconClient object
    :param time_entry_data_list: list of TimeEntryData to be pushed
    :return: result
    """
    print('Creating replicon time entries ...')
    user_uri = retrieve_user_uri(replicon_client) # Retrieve user_uri once
    if not user_uri:
        print('Failed to retrieve user URI. Aborting time entry creation.')
        return

    try:
        for i in time_entry_data_list:
            start_time = i.start_time.strftime('%H:%M')
            end_time = i.end_time.strftime('%H:%M')
            correlation_id = unique_unit_of_work_id() # Generate correlation_id for each entry

            request_data = service_defs.put_time_entry(
                user_uri=user_uri, # Pass user_uri
                y=i.year,
                m=i.month,
                d=i.day,
                comment=i.comment,
                unique_unit_of_work_id=unique_unit_of_work_id(),
                correlation_id=correlation_id, # Pass correlation_id
                start_time=start_time,
                end_time=end_time
            )

            ret = replicon_client.process_request(request_data)
            if ret is None:
                break

    except Exception as e:
        print('Error {}'.format(e))


def retrieve_user_uri(replicon_client):
    """
    Retrieve time enties
    :param replicon_client: a RepliconClient object
    :return: user uri
    """
    print('Retrieving user uri for login name {} ...'.format(replicon_client.login_name))
    request_data = service_defs.get_user_2(replicon_client.login_name)
    user_uri = replicon_client.process_request(request_data)['uri']
    print(user_uri)
    return user_uri


def retrieve_timesheet_uri(replicon_client, user_uri, y, m, d):
    """
    Retrieve timesheet uri
    :param replicon_client: a RepliconClient object
    :param user_uri: user uri
    :param y: year
    :param m: month
    :param d: day
    :return: timesheet uri
    """
    print('Retrieving timesheet uri for {}-{}-{} ...'.format(y, m, d))
    request_data = service_defs.get_timesheet_for_date_2(user_uri, y, m, d)
    ret = replicon_client.process_request(request_data)
    timesheet_uri = ret['timesheet']['uri']
    print(timesheet_uri)
    return timesheet_uri


def retrieve_time_entry_list(replicon_client, login_name, start_date, end_date):
    request_data = service_defs.get_time_entries_for_user_and_date_range(
        replicon_client.login_name,
        start_date.year, start_date.month, start_date.day,
        end_date.year, end_date.month, end_date.day
    )
    time_entry_list = replicon_client.process_request(request_data)
    print_time_entry_list(time_entry_list)
    return time_entry_list


def print_time_entry_list(time_entry_list):
    for i in time_entry_list:
        if i['interval'] is None:
            continue
        print('---------------------------------------------')
        print(i['entryDate'])
        print(i['interval'])
        for m in i['customMetadata']:
            if m['keyUri'] == "urn:replicon:time-entry-metadata-key:task":
                print('Task: {}'.format(m['value']))
            elif m['keyUri'] == "urn:replicon:time-entry-metadata-key:comments":
                print('Comment: {}'.format(m['value']))
        print(i['uri'])


def main():

    # Get today's date
    date = datetime.now()
    # Move back 7 days to get a date from last week (uncomment this to do last week's time entries)
    date = date - timedelta(days=7)

    # Retrieve the start date (Monday) and end date (Sunday) of this week
    #(start_date, end_date) = start_and_end_of_week_of_a_day(date)

    # Set specific dates
    start_date = datetime(2025, 7, 7)
    end_date = datetime(2025, 7, 13)

    print('Started checking {} to {} ...'.format(start_date, end_date))

    replicon_configs = read_json(REPLICON_CONFIGS_JSON)

    # Retrieve user data
    time_entry_data_list = retrieve_user_data(start_date, end_date, replicon_configs['tasks'])

    # Prepare connection to replicon
    user_profile = read_json(REPLICON_JSON)
    replicon_client = RepliconClient(
        company_key=user_profile[ARG_COMPANY_KEY],
        login_name=user_profile[ARG_UNAME],
        login_pass=user_profile[ARG_UPASS]
    )

    # Create and push new time entries
    create_replicon_time_entries(replicon_client, time_entry_data_list)

    # Retrieve time entries from Replicon
    #retrieve_time_entry_list(replicon_client, replicon_client.login_name, start_date, end_date)

    print("Done")

    return 0

if __name__ == '__main__':
    sys.exit(main())