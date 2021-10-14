import json
import os

import pytest
from _pytest.config import Config

from pytest_testrail_api_client import test_rail
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.modules.exceptions import TestRailError
from pytest_testrail_api_client.modules.plan import Run
from pytest_testrail_api_client.modules.session import Session
from pytest_testrail_api_client.service import is_main_loop, trim, replace_examples


def pytest_configure(config: Config):
    pytest.test_rail = test_rail.TestRail()
    file_name = Session.get_results_file(config)
    if os.path.isfile(file_name):
        os.remove(file_name)


def pytest_collection_modifyitems(config, items):
    x = pytest.test_rail.configs.get_configs()
    pass
    # config.option.markexpr = 'not not_in_scope'
    # print('\nUn-select all tests. Exporting is selected')
    # abs_path = os.path.join(config.rootdir, 'tests/groups')
    # features = get_features(abs_path, pytest.test_rail)
    # cases_list = {suite: pytest.test_rail.cases.get_cases(suite_id=suite) for suite
    #               in set(feature.main_suite for feature in features)}
    # template_id = next((template.id for template in pytest.test_rail.templates.get_templates()
    #                     if template.name == 'Test Case (Steps)'), None)
    # for feature in features:
    #     for scenario in feature.children:
    #         sc = scenario['scenario']
    #         case = {
    #             'section_id': feature.last_section,
    #             'title': sc['name'],
    #             'custom_steps_separated': sc['steps'],
    #             'estimate': '5m',
    #             'template_id': template_id,
    #             **sc['custom_fields']
    #         }
    #         if 'priority' in sc:
    #             case.update({'priority_id': sc['priority'][0]})
    #         if 'types' in sc:
    #             case.update({'type_id': sc['types'][0]})
    #         tr_case = tuple(filter(lambda x: trim(x.title) == sc['name'], cases_list[feature.main_suite]))
    #         if len(tr_case) > 0:
    #             x = pytest.test_rail.cases.add_case(**case)
    #             pytest.test_rail.cases.delete_case(x.id)
    #             # tr_case = tr_case[0]
    #             # pytest.test_rail
    #         else:
    #             pytest.test_rail.cases.add_case(**case)
    # for item in items:
    #     item.add_marker(pytest.mark.not_in_scope)


@pytest.hookimpl(tryfirst=True)
def pytest_bdd_after_scenario(request, feature, scenario):
    if 'pytest_testrail_export_test_results' in request.config.option and \
            request.config.option.pytest_testrail_export_test_results is True:
        suite_name = feature.name.split(' - ', maxsplit=1)[0]
        test_name, examples = request.node.name, scenario.examples.example_params
        test_examples, steps = test_name.split('[')[-1].replace(']', ''), []
        main_name = replace_examples(scenario.name, examples, test_examples, scenario.examples.examples)
        for step in scenario.steps:
            step_name = replace_examples(step.name, examples, test_examples, scenario.examples.examples)
            step_result = get_status_number(step.failed)
            data = {
                'content': f'**{step.keyword}:**{step_name}',
                'status_id': step_result,
                'actual': str(step.exception) if step.failed else ''
            }
            steps.append(data)
        main_result = {
            'name': main_name,
            'status_id': get_status_number(scenario.failed),
            'custom_step_results': steps
        }
        write_to_file(request, main_result, suite_name)


def pytest_sessionfinish(session):
    if 'pytest_testrail_export_test_results' in session.config.option and \
            session.config.option.pytest_testrail_export_test_results is True:
        if is_main_loop(session):
            print('Start publishing results')
            error_message, suites = [], dict()
            tr: test_rail.TestRail = pytest.test_rail
            for result_file in tr.get_results_files():
                with open(result_file, 'r') as file:
                    for key, value in json.loads(file.read()).items():
                        if key in suites:
                            suites[key] += value
                        else:
                            suites.update({key: value})
                os.remove(result_file)
            plan_id = session.config.option.pytest_testrail_test_plan_id
            config = sort_configurations(session.config.option.pytest_testrail_test_configuration_name)
            plan, suites_list = tr.plans.get_plan(plan_id), tr.suites.get_suites()
            results = []
            for suite, results_list in suites.items():
                run_to_add = plan.get_run_from_entry_name_and_config(suite, config)
                suite_id = tr.service.get_suite_by_name(suite, suites_list)
                if isinstance(suite_id, Suite):
                    if run_to_add is None:
                        run_to_add = add_entry_to_plan(plan_id, suite_id.id, suite, config)
                    tr.plans.update_run_in_plan_entry(run_to_add.id, include_all=True)
                    tests_list = tr.tests.get_tests(run_to_add.id)
                    for index, test_in_list in enumerate(tests_list):
                        tests_list[index].title = trim(tests_list[index].title)
                    for result in results_list:
                        result_test = [test.id for test in tests_list if test.title == trim(result['name'])]
                        if len(result_test) == 0:
                            error_message.append(f'Can\'t find scenario {result["name"]}')
                        else:
                            result.update({'test_id': result_test[0]})
                            results.append(result)
                    tr.results.add_results(run_id=run_to_add.id, results=results)
                    tr.service.delete_untested_tests_from_run(run_to_add.id)
            if len(error_message) > 0:
                print('\n'.join(error_message))
            print('Results published')


def add_entry_to_plan(plan_id: int, suite_id: int, name: str, config: list) -> Run:
    tr: test_rail.TestRail = pytest.test_rail
    config_ids = tr.service.convert_configs_to_ids(config)
    runs = [{'include_all': True, 'config_ids': config_ids}]
    entry = tr.plans.add_plan_entry(
        plan_id, suite_id, name=name, config_ids=config_ids, include_all=True, runs=runs)
    if not isinstance(entry, str):
        return entry.runs[0]
    else:
        raise TestRailError(entry)


def sort_configurations(configuration) -> str:
    config_split, config = trim(configuration).split(', '), []
    tr: test_rail.TestRail = pytest.test_rail
    for param in tr.configs.get_configs():
        for suite in config_split:
            if suite.lower() in [conf.name.lower() for conf in param.configs]:
                config.append(suite)
    return ', '.join(config)


def get_status_number(status):
    return {True: 5, False: 1, None: 2}.get(status, 3)


def write_to_file(request, result: dict, suite_name: str):
    file_path = Session.get_results_file(request)
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps({suite_name: [result]}))
    else:
        with open(file_path, 'r+') as file:
            data = json.loads(file.read())
            if suite_name not in data:
                data[suite_name] = [result]
            else:
                data[suite_name].append(result)
            file.seek(0)
            json.dump(data, file)


def pytest_addoption(parser):
    group = parser.getgroup("pytest-rail")
    commands = ('--pytest-testrail-export-test-results', '--pytest-testrail-test-plan-id',
                '--pytest-testrail-test-configuration-name')
    actions = ('store_true', 'store', 'store')
    types = (None, 'int', 'string')
    defaults = (False, None, None)
    helps = ('TestRail export Test Results', 'TestRail Test Plan to export results',
             'TestRail Test Configuration used for testing')
    for index, value in enumerate(commands):
        data = {'action': actions[index], 'default': defaults[index], 'help': helps[index]}
        if types[index] is not None:
            data['type'] = types[index]
        group.addoption(value, **data)


def pytest_bdd_step_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def pytest_bdd_step_validation_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def pytest_bdd_step_func_lookup_error(scenario, step, exception):
    _step_error(exception, scenario, step)


def _step_error(exception, scenario, step):
    scenario.exception = exception
    scenario.failed = True
    is_blocked = False
    for scenario_step in scenario.steps:
        scenario_step.failed = None if is_blocked else False
        if scenario_step == step:
            scenario_step.exception = exception
            scenario_step.failed = True
            is_blocked = True
    exception_message = exception.msg if hasattr(exception, 'msg') \
        else exception.message if hasattr(exception, 'message') \
        else exception.args[0] if hasattr(exception, 'args') and exception.args.__len__() > 0 \
        else 'no error message'
    scenario.exception_message = exception_message
