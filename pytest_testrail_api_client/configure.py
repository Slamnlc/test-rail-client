import json
import os

import pytest
from _pytest.config import Config

import pytest_testrail_api_client.test_rail as test_rail
from pytest_testrail_api_client.modules.session import Session
from pytest_testrail_api_client.service import is_main_loop, trim


def pytest_configure(config: Config):
    pytest.test_rail = test_rail.TestRail()
    if is_main_loop(config):
        if os.path.isfile(Session.result_cache):
            os.remove(Session.result_cache)


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
    write_to_file(main_result, suite_name)


def pytest_sessionfinish(session):
    if is_main_loop(session):
        with open(Session.result_cache, 'r') as file:
            suites = json.loads(file.read())
        tr: test_rail.TestRail = pytest.test_rail
        configuration = 'REST, CHINA'
        plan_id = 653
        config = sort_configurations(configuration)
        plan = tr.plans.get_plan(plan_id)
        suites_list = tr.suites.get_suites()
        results = []
        for suite, results_list in suites.items():
            run_to_add = plan.get_run_from_entry_name_and_config(suite, config)
            suite_id = [project_suite.id for project_suite in suites_list if
                        project_suite.name.lower() == suite.lower()]
            if len(suite_id) > 0:
                suite_id = suite_id[0]
                if run_to_add is None:
                    entry = tr.plans.add_plan_entry(plan_id, suite_id, name=suite,
                                                    config_ids=tr.service.convert_configs_to_ids(config),
                                                    include_all=True)
                    1 == 1
                tests_list = tr.tests.get_tests(run_to_add.id)
                tests_in_suite = tr.cases.get_cases(suite_id=suite_id)
                for result in results_list:
                    result_test = [test.id for test in tests_list if test.title == result['name']]
                    if len(result_test) == 0:

                        pass
                    else:
                        result.update({'test_id': result_test[0]})
                        results.append(result)
                tr.results.add_results(run_id=run_to_add.id, results=results)
            1 == 1
    # tr_run = tr.

    1 == 1


def replace_examples(where: str, examples: list, variables: list):
    for index, param in enumerate(examples):
        if len(variables) > index:
            where = where.replace(f'<{param}>', variables[index])
    return where


def add_run_to_plan(plan_id, suite_id, name, config):
    tr: test_rail.TestRail = pytest.test_rail

    tr.plans.add_plan_entry(plan_id, suite_id, name=name, )
    pass


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


def write_to_file(result: dict, suite_name: str):
    file_path = Session.result_cache
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write(json.dumps({suite_name: [result]}))
    else:
        with open(file_path, 'r+') as file:
            data = json.loads(file.read())
            if not suite_name in data:
                data[suite_name] = [result]
            else:
                data[suite_name].append(result)
            file.seek(0)
            json.dump(data, file)


def pytest_addoption(parser):
    group = parser.getgroup("pytest-rail")
