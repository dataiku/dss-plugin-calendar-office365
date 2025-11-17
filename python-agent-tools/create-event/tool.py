# This file is the implementation of custom agent tool create-event
from dataiku.llm.agent_tools import BaseAgentTool
import datetime
from dku_common import get_token_from_config, assert_no_temporal_paradox, extract_start_end_date
from microsoft_calendar_client import MicrosoftCalendarClient


class CustomAgentTool(BaseAgentTool):
    def set_config(self, config, plugin_config):
        self.config = config
        access_token = get_token_from_config(config)
        self.client = MicrosoftCalendarClient(access_token)

    def get_descriptor(self, tool):
        time_now = "All time expression should be evaluated against the current date and time, which is {}.".format(time_now_RFC3339())
        return {
            "description": "This tool is a wrapper around Office 365 Calendar Events API, useful when you need to create an event stored on a Office 365 Calendar. The input to this tool is a dictionary containing the time period for the events, e.g. '{'timeMin':'2011-06-03T10:00:00Z', 'timeMax':'2011-06-03T10:30:00Z'}'",
            "inputSchema": {
                "$id": "https://example.com/agents/tools/hash/input",
                "title": "Input for the hashing tool",
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "The subject of the event"
                    },
                    "description": {
                        "type": "string",
                        "description": "The description of the event"
                    },
                    "location": {
                        "type": "string",
                        "description": "The location of the event"
                    },
                    "attendees": {
                        "type": "array",
                        "description": "Comma separated string of the attendees email addresses"
                    },
                    "start": {
                        "type": "string",
                        "description": "Upper bound (exclusive) for the event's start time. Must be an RFC3339 timestamp with mandatory time zone offset, for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. {}".format(time_now)
                    },
                    "end": {
                        "type": "string",
                        "description": "Lower bound (exclusive) for the event's end time. Must be an RFC3339 timestamp with mandatory time zone offset, for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. {}".format(time_now)
                    },
                },
                "required": ["payload"]
            }
        }

    def invoke(self, input, trace):
        args = input["input"]
        subject = args["subject"]
        description = args["description"]
        start = args["start"]
        end = args["end"]
        attendees_emails = args["attendees_emails"]
        location = args["location"]

        '''
        POST https://graph.microsoft.com/v1.0/me/calendars/AAMkAGViNDU7zAAAAAGtlAAA=/events
        Content-type: application/json

        {
        "subject": "Let's go for lunch",
        "body": {
            "contentType": "HTML",
            "content": "Does mid month work for you?"
        },
        "start": {
            "dateTime": "2019-03-15T12:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "end": {
            "dateTime": "2019-03-15T14:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "location":{
            "displayName":"Harry's Bar"
        },
        "attendees": [
            {
            "emailAddress": {
                "address":"adelev@contoso.com",
                "name": "Adele Vance"
            },
            "type": "required"
            }
        ],
        "transactionId":"7E163156-7762-4BEB-A1C6-729EA81755A7"
        }
        '''
        attendees_emails = attendees_emails.split(",")
        response = self.client.create_event(start, end, subject, description, location, attendees_emails)
        json_response = response.json()
        web_link = json_response.get("webLink")
        if web_link:
            return {
                "output": "Event created with the following link: {}".format(web_link)
            }
        else:
            return {
                "output": "There was an issue while creating the event."
            }


def time_now_RFC3339():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.isoformat("T").split(".")[0] + "Z"
