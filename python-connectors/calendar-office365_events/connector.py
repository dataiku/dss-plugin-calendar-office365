# This file is the actual code for the custom Python dataset calendar-office365_events
# import the base class for the custom dataset

from dku_common import get_token_from_config, assert_no_temporal_paradox, extract_start_end_date
from microsoft_calendar_client import MicrosoftCalendarClient
from dataiku.connector import Connector
import logging

class MicrosoftCalendarEventConnector(Connector):

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)
        access_token = get_token_from_config(config)
        self.client = MicrosoftCalendarClient(access_token)
        self.from_date = self.config.get("from_date", None)
        self.to_date = self.config.get("to_date", None)
        assert_no_temporal_paradox(self.from_date, self.to_date)
        self.calendar_id = self.config.get("calendar_id", None)
        self.raw_results = self.config.get("raw_results", False)

    def get_read_schema(self):
        # In this example, we don't specify a schema here, so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                            partition_id=None, records_limit=-1):
        if not self.calendar_id:
            self.calendar_id = None

        events = []
        first_call = True
        self.client.reset_next_page_token()
        while first_call or self.client.has_more_events():
            first_call = False
            events.extend(
                self.client.get_events(from_date=self.from_date,
                                       to_date=self.to_date,
                                       calendar_id=self.calendar_id,
                                       max_results=records_limit))
        for event in events:
            yield {"api_output": event} if self.raw_results else extract_start_end_date(event)

    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                         partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise Exception("Unimplemented")


    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise Exception("Unimplemented")


    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []


    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")


    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise Exception("unimplemented")
