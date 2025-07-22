from dku_plugin_test_utils import dss_scenario

TEST_PROJECT_KEY = "PLUGINTESTCALENDAROFFICE365"


def test_run_calendar_office365_dataset_events(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="DATASET_EVENTS")

def test_run_calendar_office365_recipe_events(user_dss_clients):
    dss_scenario.run(user_dss_clients, project_key=TEST_PROJECT_KEY, scenario_id="RECIPE_EVENTS")