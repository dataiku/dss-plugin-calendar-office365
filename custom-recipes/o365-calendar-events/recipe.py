# -*- coding: utf-8 -*-
import dataiku
import pandas as pd
import logging
import requests
from microsoft_calendar_client import MicrosoftCalendarClient

from dataiku.customrecipe import get_input_names_for_role, get_recipe_config, get_output_names_for_role
from dku_common import get_token_from_config, get_iso_format


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='microsoft-calendar plugin %(levelname)s - %(message)s')


logger.info("Microsoft Calendar Plugin events recipe")

config = get_recipe_config()
access_token = get_token_from_config(config)

calendar_id_column = config.get("calendar_id_column", None)
start_time = config.get("from_date_column", None)
end_time = config.get("to_date_column", None)
max_results = config.get("max_results")


logger.info("Retrieving Microsoft Calendar events using columns id '{}', from '{}' to '{}'".format(calendar_id_column, start_time, end_time))
client = MicrosoftCalendarClient(access_token)
logger.info("Microsoft Calendar client authenticated")

input_dataset_name = get_input_names_for_role('input_dataset_name')
input_dataset = dataiku.Dataset(input_dataset_name[0])
input_df = input_dataset.get_dataframe()
logger.info("{} line(s) to process".format(len(input_df)))

events = []
for index, input_parameters_row in input_df.iterrows():
    calendar_id = input_parameters_row.get(calendar_id_column, None)
    from_date = get_iso_format(input_parameters_row.get(start_time)) if start_time else None
    to_date = get_iso_format(input_parameters_row.get(end_time)) if end_time else None

    first_call = True
    client.reset_next_page_token()
    while first_call or client.has_more_events():
        first_call = False
        events.extend(
            client.get_events(from_date=from_date, to_date=to_date, calendar_id=calendar_id, max_results=max_results)
                )

calendar_events_df = pd.DataFrame(events)

if calendar_events_df.size > 0:
    output_names_stats = get_output_names_for_role('api_output')
    api_output = dataiku.Dataset(output_names_stats[0])
    api_output.write_with_schema(calendar_events_df)
