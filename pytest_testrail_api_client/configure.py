import json
import os

import pytest
from _pytest.config import Config

import pytest_testrail_api_client.test_rail as test_rail
from pytest_testrail_api_client.modules.classes import Suite
from pytest_testrail_api_client.modules.exceptions import TestRailError
from pytest_testrail_api_client.modules.plan import Run
from pytest_testrail_api_client.modules.session import Session
from pytest_testrail_api_client.service import is_main_loop, trim


def pytest_configure(config: Config):
    pytest.test_rail = test_rail.TestRail()
    file_name = Session.get_results_file(config)
    if os.path.isfile(file_name):
        os.remove(file_name)


def pytest_bdd_after_scenario(request, feature, scenario):
    suite_name = feature.name.split(' - ', maxsplit=1)[0]
    test_name, examples = request.node.name, scenario.examples.example_params
    test_examples, steps = test_name.split('[')[-1].replace(']', '').split('-'), []
    main_name = replace_examples(scenario.name, examples, test_examples)
    for step in scenario.steps:
        step_name = replace_examples(step.name, examples, test_examples)
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
    if is_main_loop(session):
        print('Start publishing results')
        error_message = []
        for result_file in Session.get_results_files():
            with open(result_file, 'r') as file:
                suites = json.loads(file.read())
            os.remove(file)
            tr: test_rail.TestRail = pytest.test_rail
            configuration = 'REST, CHINA'
            plan_id = 653
            config = sort_configurations(configuration)
            plan = tr.plans.get_plan(plan_id)
            suites_list = tr.suites.get_suites()
            results = []
            for suite, results_list in suites.items():
                run_to_add = plan.get_run_from_entry_name_and_config(suite, config)
                suite_id = tr.service.get_suite_by_name(suite, suites_list)
                if isinstance(suite_id, Suite):
                    if run_to_add is None:
                        run_to_add = add_entry_to_plan(plan_id, suite_id, suite, config)
                    tests_list = tr.tests.get_tests(run_to_add.id)
                    tests_in_suite, need_add = tr.cases.get_cases(suite_id=suite_id), []
                    for result in results_list:
                        result_test = [test.id for test in tests_list if test.title == result['name']]
                        if len(result_test) == 0:
                            test_in_suite = [test.id for test in tests_in_suite if test.title == result['name']]
                            if len(test_in_suite) > 0:
                                result.update({'test_id': test_in_suite[0]})
                                results.append(result)
                                need_add.append(test_in_suite[0])
                            else:
                                error_message.append(f'Can\'t find scenario {result["name"]}')
                        else:
                            result.update({'test_id': result_test[0]})
                            results.append(result)
                    if len(need_add) > 0:
                        case_ids = [test.id for test in tests_list] + need_add
                        tr.plans.update_run_in_plan_entry(run_to_add.id, case_ids=case_ids)
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


def replace_examples(where: str, examples: list, variables: list):
    for index, param in enumerate(examples):
        if len(variables) > index:
            where = where.replace(f'<{param}>', variables[index])
    return where


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
