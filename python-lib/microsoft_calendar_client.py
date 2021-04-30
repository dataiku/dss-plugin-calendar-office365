import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='microsoft-calendar plugin %(levelname)s - %(message)s')


class MicrosoftCalendarClientError(ValueError):
    pass

class MicrosoftCalendarClient():
    def __init__(self, access_token):
        logger.info("MicrosoftCalendarClient init")
        self.access_token = access_token
        self.headers = {'Authorization' : 'Bearer {}'.format(self.access_token)}
        logger.info("Microsoft credentials retrieved")
        self.number_retrieved_events = 0
        self.next_page_token = None
        self.first_call = True

    def build_url(self, from_date, to_date, calendar_id):
        if not self.next_page_token:
            print("CALENDAR ID IS FOLLOWING")
            print(calendar_id)
            if isinstance(calendar_id, str):
                print("IS STR")
                self.base_url = "https://graph.microsoft.com/v1.0/me/calendars/{}/calendarView?startDateTime={}&endDateTime={}".format(calendar_id, from_date, to_date)
            else:
                print("NOT STR")
                self.base_url = "https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime={}&endDateTime={}".format(from_date, to_date)
        else:
            self.base_url = self.next_page_token

    def get_next_page_token_if_exist(self, events_result):
        try:
            self.next_page_token = events_result['@odata.nextLink']
        except:
            self.next_page_token = None

    def reset_next_page_token(self):
        self.next_page_token = None

    def get_events(self, from_date, to_date, calendar_id, can_raise=True):
        self.build_url(from_date, to_date, calendar_id)
        events_result = requests.get(self.base_url, headers=self.headers).json()
        self.get_next_page_token_if_exist(events_result)

        try:
            events = events_result['value']
        except Exception as err:
            logging.error("Microsoft Client Error : {}".format(err))
            if can_raise:
                try:
                    err = events_result['error']['code']
                except:
                    pass
                raise MicrosoftCalendarClientError("Error: {}".format(err))
            else:
                return ["api error : {}".format(err)]

        self.number_retrieved_events += len(events)
        logger.info("{} events retrieved, {} in total".format(len(events), self.number_retrieved_events))
        return events

    def has_more_events(self):
        return self.next_page_token is not None
