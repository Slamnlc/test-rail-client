from typing import List

from pytest_testrail_api_client.modules.case_field import CaseField
from pytest_testrail_api_client.modules.category import Base
from pytest_testrail_api_client.modules.classes import Status, CaseType, Template, ResultField, Priority, TestObj
from pytest_testrail_api_client.service import validate_id


class StatusesApi(Base):
    __sub_host = '/api/v2'

    def get_statuses(self):
        """
        https://www.gurock.com/testrail/docs/api/reference/statuses

        Returns a list of available test statuses
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_statuses'), Status)


class TestsApi(Base):
    __sub_host = '/api/v2'

    def get_test(self, test_id: int) -> TestObj:
        """
        https://www.gurock.com/testrail/docs/api/reference/tests#gettest

         Returns an existing test
        :param test_id:
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_test/{test_id}'), TestObj)

    def get_tests(self, run_id: int, status_id: (str, list) = None) -> List[TestObj]:
        """
        https://www.gurock.com/testrail/docs/api/reference/tests#gettests

        Returns a list of tests for a test run
        :param run_id: The ID of the test run
        :param status_id: A comma-separated list of status IDs to filter by
        :return:
        """
        status_id = validate_id(status_id)
        params = dict() if status_id is None else {'status_id': status_id}
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_tests/{run_id}', params=params),
                           TestObj)


class CaseTypesApi(Base):
    __sub_host = '/api/v2'

    def get_case_types(self) -> List[CaseType]:
        """
        https://www.gurock.com/testrail/docs/api/reference/case-types#getcasetypes

        Returns a list of available case types.
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_case_types'), CaseType)

    def _service_case_types(self):
        return {case_type.name.lower(): case_type.id for case_type in self.get_case_types()}


class TemplatesApi(Base):
    __sub_host = '/api/v2'

    def get_templates(self, project_id: int = None) -> List[Template]:
        """
        https://www.gurock.com/testrail/docs/api/reference/templates

        Returns a list of available templates (requires TestRail 5.2 or later).
        :param project_id: The ID of the project. If not indicated - takes default project_id
        :return:
        """
        if project_id is None:
            project_id = self._session.project_id
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_templates/{project_id}'), Template)


class CaseFieldsApi(Base):
    __sub_host = '/api/v2'

    def get_case_fields(self) -> List[CaseField]:
        """
        https://www.gurock.com/testrail/docs/api/reference/case-fields#getcasefields

        Returns a list of available test case custom fields.
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_case_fields'), CaseField)

    def _service_case_fields(self) -> dict:
        serv = dict()
        for field in self.get_case_fields():
            for config in field.configs:
                if hasattr(config.options, 'items'):
                    for key, value in config.options.items.items():
                        if key.lower() == 'to be automated':
                            serv.update({'to_automate': {'id': value, 'name': field.system_name}})
                        else:
                            serv.update({key.replace(' ', '_').lower(): {'id': value, 'name': field.system_name}})
        return serv


class ResultsFieldsApi(Base):
    __sub_host = '/api/v2'

    def get_result_fields(self) -> List[ResultField]:
        """
        https://www.gurock.com/testrail/docs/api/reference/result-fields

        Returns a list of available test result custom fields
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_result_fields'), ResultField)


class PrioritiesApi(Base):
    __sub_host = '/api/v2'

    def get_priorities(self) -> List[Priority]:
        """
        https://www.gurock.com/testrail/docs/api/reference/priorities#getpriorities

        Returns a list of available priorities
        :return:
        """
        return self._valid(self._session.request('get', f'{self.__sub_host}/get_priorities'), Priority)

    def _service_priorities(self):
        return {priority.name.lower(): priority.id for priority in self.get_priorities()}
