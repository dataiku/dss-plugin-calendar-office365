import logging
import requests
from urllib.parse import quote

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
            if isinstance(calendar_id, str):
                self.base_url = "https://graph.microsoft.com/v1.0/me/calendars/{}/calendarView?startDateTime={}&endDateTime={}".format(calendar_id, quote(from_date), quote(to_date))
            else:
                self.base_url = "https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime={}&endDateTime={}".format(quote(from_date), quote(to_date))
            #self.base_url = "https://graph.microsoft.com/v1.0/me/calendar/2"
        else:
            self.base_url = self.next_page_token

    def get_next_page_token_if_exist(self, events_result):
        self.next_page_token = events_result.get('@odata.nextLink')

    def reset_next_page_token(self):
        self.next_page_token = None

    def get_events(self, from_date, to_date, calendar_id, can_raise=True, max_results=-1):
        self.build_url(from_date, to_date, calendar_id)
        response = requests.get(self.base_url, headers=self.headers)
        events_result = response.json()
        self.get_next_page_token_if_exist(events_result)

        events = events_result.get('value')
        if response.status_code >= 400:
            return [events_result]
        self.number_retrieved_events += len(events)
        logger.info("{} events retrieved, {} in total".format(len(events), self.number_retrieved_events))
        return events

    def has_more_events(self):
        return self.next_page_token is not None
