from itertools import chain
from typing import List

import pytest_testrail_api_client.configure as configure
from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.modules.plan import Run
from pytest_testrail_api_client.modules.result import Result
from pytest_testrail_api_client.service import to_json


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

    def copy_run_to_plan(self, run_id: int, plan_id: int, delete_untested: bool = True,
                         delete_original_run: bool = False, milestone_id: int = None) -> Run:
        run = self._session.runs.get_run(run_id)
        run_tests = self._session.tests.get_tests(run_id)
        cases_ids = tuple(test.case_id for test in run_tests)
        run_to_add = {'include_all': False, 'config_ids': run.config_ids, 'case_ids': cases_ids}
        if milestone_id is not None and isinstance(milestone_id, int):
            run_to_add.update({'milestone_id': milestone_id})
        new_entry = self._session.plans.add_plan_entry(plan_id, suite_id=run.suite_id, name=run.name,
                                                       description=run.description, config_ids=run.config_ids,
                                                       runs=[run_to_add])
        new_run_id = new_entry.runs[-1].id

        self.copy_results_from_run(run_id, new_run_id, run_tests)
        if delete_untested is True:
            self.delete_untested_tests_from_run(new_run_id)
        if delete_original_run is True:
            self._session.runs.delete_run(run_id)

        return new_entry.runs[-1]

    def copy_results_from_run(self, old_run_id: int, new_run_id: int, old_tests: List[Result] = None):
        statuses = tuple(status.id for status in self._session.statuses.get_statuses())
        results = sorted(self._session.results.get_results_for_run(old_run_id, status_id=statuses),
                         key=lambda result: result.created_on, reverse=False)
        if old_tests is None:
            old_tests = self._session.tests.get_tests(old_run_id)

        new_tests = self._session.tests.get_tests(new_run_id)
        for old_test in old_tests:
            old_results = tuple(filter(lambda x: x.test_id == old_test.id, results))
            if len(old_results) > 0:
                new_test_id = next((x.id for x in new_tests if x.title == old_test.title), None)
                if new_test_id is not None:
                    for res in old_results:
                        res.test_id = new_test_id

        self._session.results.add_results(new_run_id, to_json(results))
