from itertools import chain

from pytest_testrail_api_client import test_rail
from pytest_testrail_api_client.client_config import NO_TAG_IN_FEATURE_HEADER, ONE_OF_TAGS, AT_LEAST_ONE
from pytest_testrail_api_client.modules.exceptions import TestRailError
from pytest_testrail_api_client.modules.plan import Plan
from pytest_testrail_api_client.service import trim


def validate_scenario_tags(scenarios: list, feature_path: str):
    errors = []
    if NO_TAG_IN_FEATURE_HEADER is True:
        if len(scenarios['tags']) != 0:
            errors.append(f'File "{feature_path}", line 1: Delete all tags from head of feature file')
    for scenario in scenarios['children']:
        if 'scenario' in scenario:
            scenario = scenario['scenario']
            line = scenario["location"]["line"]
            tag_names = tuple(tag['name'] for tag in scenario['tags'])
            for one_of in ONE_OF_TAGS:
                found_tags = tuple(filter(lambda x: x in one_of, tag_names))
                if len(found_tags) > 1:
                    errors.append(f'File "{feature_path}", line {line}: Using more than 1 tag from group {one_of}')
                elif len(found_tags) == 0:
                    errors.append(f'File "{feature_path}", line {line}: Missing any tags from {one_of}')
            if '/rest/' not in feature_path.lower() and '/web/' not in feature_path.lower():
                for one in AT_LEAST_ONE:
                    if not any((x in one for x in tag_names)):
                        errors.append(f'File "{feature_path}", line {line}: Missing at least one tag from {one}')

    return errors


def validate_configs(configuration: str, tr_client: test_rail.TestRail) -> None:
    bad_conf = []
    configs = tuple(x.name.lower() for x in chain.from_iterable([x.configs for x in tr_client.configs.get_configs()]))
    for param in trim(configuration).split(', '):
        if param.lower() not in configs:
            bad_conf.append(param)
    if len(bad_conf) != 0:
        raise TestRailError(f'Wrong configuration name: {", ".join(bad_conf)}')


def validate_plan_id(plan_id: int, tr_client: test_rail.TestRail) -> None:
    if not isinstance(tr_client.plans.get_plan(plan_id), Plan):
        raise TestRailError('Wrong plan id')
