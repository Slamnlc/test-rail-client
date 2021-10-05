import json
import os

import pytest
from pytest_bdd.parser import Feature, Scenario
from pytest_testrail_api_client.modules.session import Session
from pytest_testrail_api_client.test_rail import TestRail


def pytest_configure():
    pytest.test_rail = TestRail()


def pytest_bdd_before_scenario(request, feature: Feature, scenario: Scenario):
    folders = feature.name.split(' - ', maxsplit=1)
    suite_name, sub_folder = folders[0], folders[1]
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
        'sub_folder': sub_folder,
        'name': main_name,
        'status_id': get_status_number(scenario.failed),
        'custom_step_results': steps
    }
    write_to_file(main_result, suite_name)


def pytest_sessionfinish(session):
    results = json.loads(open(Session.result_cache, 'r').read())
    tr: TestRail = pytest.test_rail
    suites = tr.suites.get_suites()
    configuration = 'REST, CHINA'
    plan_id = 653
    plan = tr.plans.get_plan(plan_id)
    x = plan.get_run_from_entry_name_and_config('api', configuration)

    # tr_run = tr.

    1 == 1


def replace_examples(where: str, examples: list, variables: list):
    for index, param in enumerate(examples):
        if len(variables) > index:
            where = where.replace(f'<{param}>', variables[index])
    return where


def get_status_number(status):
    return {True: 5, False: 1, None: 3}.get(status, 3)


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
