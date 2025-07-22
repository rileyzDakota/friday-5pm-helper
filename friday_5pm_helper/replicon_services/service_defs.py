from __future__ import print_function
from collections import namedtuple


RequestData = namedtuple('RequestData', 'service_url data')


def get_user_2(login_name):
    return RequestData(
        service_url= 'UserService1.svc/GetUser2',
        data={"user": {"loginName": login_name}}
    )


def get_timesheet_for_date_2(user_uri, y, m, d):
    return RequestData(
        service_url='TimesheetService1.svc/GetTimesheetForDate2',
        data={
            "userUri": user_uri,
            "date": {
                "year": y,
                "month": m,
                "day": d
            }
        }
    )

def get_time_entries_for_user_and_date_range(
        login_name, start_y, start_m, start_d, end_y, end_m, end_d
):
    return RequestData(
        service_url='TimeEntryService3.svc/GetTimeEntriesForUserAndDateRange',
        data={
            "user": {
                "loginName": login_name,
            },
            "dateRange": {
                "startDate": {
                    "year": start_y,
                    "month": start_m,
                    "day": start_d
                },
                "endDate": {
                    "year": end_y,
                    "month": end_m,
                    "day": end_d
                }
            }
        }
    )

def put_time_entry(user_uri, y, m, d, comment, unique_unit_of_work_id, correlation_id, start_time, end_time):
    # Assuming start_time and end_time are strings in "HH:MM" format
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))

    return RequestData(
        service_url='TimeEntryRevisionGroupService1.svc/PutTimeEntryRevisionGroup',
        data={
            "timeEntryRevisionGroup": {
                "target": {
                    "parameterCorrelationId": correlation_id,
                    "uri": None
                },
                "user": {
                    "uri": user_uri,
                },
                "entryDate": {
                    "year": y,
                    "month": m,
                    "day": d
                },
                "timeAllocationTypeUris": [
                    "urn:replicon:time-allocation-type:attendance",
                    "urn:replicon:time-allocation-type:project"
                ],
                "interval": {
                    "hours": None,
                    "timePair": {
                        "startTime": {
                            "hour": start_hour,
                            "minute": start_minute,
                            "second": 0
                        },
                        "endTime": {
                            "hour": end_hour,
                            "minute": end_minute,
                            "second": 0
                        }
                    }
                },
                "customMetadata": [
                    {
                        "keyUri": "urn:replicon:time-entry-metadata-key:comments",
                        "value": {
                            "text": comment
                        }
                    }
                ],
                "extensionFieldValues": []
            },
            "unitOfWorkId": unique_unit_of_work_id
        }
    )

def get_timesheet_summary(timesheet_uri):
    return RequestData(
        service_url='TimesheetService1.svc/GetTimesheetSummary',
        data={
            "timesheetUri": timesheet_uri
        }
    )

def get_standard_timesheet_2(timesheet_uri):
    return RequestData(
        service_url='TimesheetService1.svc/GetStandardTimesheet2',
        data={
            "timesheetUri": timesheet_uri
        }
    )
