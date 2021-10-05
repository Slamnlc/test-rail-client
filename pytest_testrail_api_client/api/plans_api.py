from typing import List

from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.plan import Plan, Run, Entries
from pytest_testrail_api_client.service import get_dict_from_locals, split_by_coma


class PlansApi(Base):
    __sub_host = '/api/v2'

    def get_plan(self, plan_id: int) -> Plan:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#getplan

        Returns an existing test plan
        :param plan_id: The ID of the test plan
        :return: Plan
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_plan/{plan_id}'), Plan)

    def get_plans(self, project_id: int = None) -> List[Plan]:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#getplans

        Returns a list of test plans for a project
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :return: List[Plan]
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_plans/{project_id}'), Plan)

    def add_plan(self, name: str, project_id: int = None, description: str = None, milestone_id: int = None,
                 entries: List[str] = None) -> Entries:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#addplan

        Creates a new test plan
        :param name: The name of the test plan (required)
        :param project_id: The ID of the project - if project ID isn't indicated - take default project id
        :param description: The description of the test plan
        :param milestone_id: The ID of the milestone to link to the test plan
        :param entries: An array of objects describing the test runs of the plan, see add_plan_entry
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        data = get_dict_from_locals(locals(), exclude=['project_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_plan/{project_id}', data=data), Plan)

    def add_plan_entry(self, plan_id: int, suite_id: int, name: int = None, description: str = None,
                       assignedto_id: int = None, include_all: bool = None, case_ids: (list, str) = None,
                       config_ids: (list, str) = None, refs: str = None, runs: List[Run] = None) -> Entries:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#addplanentry

        Adds one or more new test runs to a test plan.
        :param plan_id: The ID of the plan the test runs should be added to
        :param suite_id: The ID of the test suite for the test run(s) (required)
        :param name: The name of the test run(s)
        :param description: The description of the test run(s) (requires TestRail 5.2 or later)
        :param assignedto_id: The ID of the user the test run(s) should be assigned to
        :param include_all: True for including all test cases of the test suite and false for a custom case selection
        :param case_ids: An array of case IDs for the custom case selection
        :param config_ids: An array of configuration IDs used for the test runs of the test plan entry
        :param refs: A string of external requirement IDs, separated by commas. (requires TestRail 6.3 or later)
        :param runs: An array of test runs with configurations, please see the example below for details
        :return:
        """
        if case_ids is not None:
            if isinstance(case_ids, str):
                case_ids = case_ids.replace(' ', '').split(',')
        config_ids = split_by_coma(config_ids)
        if config_ids is not None:
            if isinstance(config_ids, str):
                config_ids = config_ids.replace(' ', '').split(',')
        data = get_dict_from_locals(locals(), exclude=['plan_id'])
        return self._valid(self._session.request('post', f'{self.__sub_host}/add_plan_entry/{plan_id}', data=data),
                           Entries)

    def close_plan(self, plan_id: int) -> Plan:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#closeplan

        Closes an existing test plan and archives its test runs & results
        :param plan_id: The ID of the test plan
        :return:
        """
        return self._valid(self._session.request('post', f'{self.__sub_host}/close_plan/{plan_id}'), Plan)

    def delete_plan(self, plan_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#deleteplan

        Deletes an existing test plan
        :param plan_id: The ID of the test plan
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_plan/{plan_id}', return_type='status_code')

    def delete_plan_entry(self, plan_id: int, entry_id: str) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#deleteplanentry

        Deletes one or more existing test runs from a plan
        :param plan_id: The ID of the test plan
        :param entry_id: The ID of the test plan entry (note: not the test run ID)
        :return: status code
        """
        return self._session.request('post', f'{self.__sub_host}/delete_plan_entry/{plan_id}/{entry_id}')

    def delete_run_from_plan_entry(self, run_id: int) -> int:
        """
        https://www.gurock.com/testrail/docs/api/reference/plans#deleteplanentry

        Deletes a test run from a test plan entry
        :param run_id: The ID of the test run
        :return:
        """
        return self._session.request('post', f'{self.__sub_host}/delete_run_from_plan_entry/{run_id}',
                                     return_type='status_code')
