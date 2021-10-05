from itertools import chain
from typing import List

import pytest_testrail_api_client.configure as configure
from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Suite


class ServiceApi(Base):
    def convert_configs_to_ids(self, configs: (str, list)):
        all_configs = tuple(chain.from_iterable((x.configs for x in self._session.configs.get_configs())))
        if isinstance(configs, str):
            configs = configure.trim(configs).split(', ')
        config_ids = []
        for config in configs:
            config_id = [conf_id.id for conf_id in all_configs if conf_id.name.lower() == config.lower()]
            if len(config_id) > 0:
                config_ids.append(config_id[0])
        return config_ids

    def get_suite_by_name(self, suite_name: str, suite_list: List[Suite] = None) -> Suite:
        suite_list = self._session.suites.get_suites() if suite_list is None else suite_list
        result = tuple(suite for suite in suite_list if suite.name.lower() == suite_name.lower())
        return result[0] if len(result) > 0 else []

    def delete_untested_tests_from_run(self, run_id: int):
        case_ids = list(result.case_id for result in self._session.tests.get_tests(run_id, status_id='1, 5'))
        self._session.plans.update_run_in_plan_entry(run_id=run_id, include_all=False, case_ids=case_ids)
