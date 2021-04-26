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

    def get_events(self, from_date=None, to_date=None, calendar_id=None, can_raise=True):
        if isinstance(calendar_id, str):
            self.base_url = "https://graph.microsoft.com/v1.0/me/calendars/{}/events?startDateTime={}&endDateTime={}".format(calendar_id, from_date, to_date)
        else:
            self.base_url = "https://graph.microsoft.com/v1.0/me/calendar/events?startDateTime={}&endDateTime={}".format(from_date, to_date)

        events_result = requests.get(self.base_url, headers=self.headers).json()

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
        data = {}
        data['events'] = [event['subject'] for event in events]
        data['start'] = [event['start']['dateTime'] for event in events]
        data['end'] = [event['end']['dateTime'] for event in events]
        data['link'] = [event['webLink'] for event in events]

        self.number_retrieved_events += len(data['events'])
        logger.info("{} events retrieved, {} in total".format(len(data['events']), self.number_retrieved_events))
        return data
