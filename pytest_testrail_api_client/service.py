import os
from copy import deepcopy
from datetime import datetime
from typing import List, Union

from _pytest.config import Config
from _pytest.main import Session
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

from pytest_testrail_api_client.client_config import PRIORITY_REPLACE
from pytest_testrail_api_client.modules.bdd_classes import TrFeature


def get_dict_from_locals(locals_dict: dict, replace_underscore: bool = False, exclude: list = None):
    exclude = ('self', 'kwargs') if exclude is None else tuple(['self', 'kwargs'] + exclude)
    result = {key if replace_underscore else key: value for key, value in
              locals_dict.items() if key not in exclude and '__py' not in key and value is not None}
    if 'kwargs' in locals_dict:
        result.update(locals_dict['kwargs'])
    return result


def split_by_coma(*args):
    def sub_split(value):
        if value is not None:
            if not isinstance(value, (tuple, list)):
                value = trim(value).split(', ')
            return value

    if all([arg is None for arg in args]):
        return None
    elif len(args) > 1:
        return [sub_split(val) for val in args]
    else:
        return args[0].replace(' ', '').split(',') if not isinstance(args[0], (tuple, list)) else args[0]


def validate_id(status_id):
    if status_id is not None:
        if isinstance(status_id, (list, tuple)):
            return ','.join(tuple(map(str, status_id)))
        elif isinstance(status_id, str):
            return status_id.replace(' ', '')


def get_date_from_timestamp(date):
    return None if date is None else datetime.fromtimestamp(date)


def is_main_loop(session: (Session, Config)):
    if isinstance(session, Session):
        if not hasattr(session.config, 'workerinput'):
            return True
        else:
            return session.config.option.dist != "no"
    else:
        if not hasattr(session, 'workerinput'):
            return True
        else:
            return session.option.dist != "no"


def get_worker_id(config):
    if hasattr(config, 'config'):
        config = config.config
    return config.workerinput['workerid'] if hasattr(config, 'workerinput') else 'main'


def trim(string: str) -> str:
    return ' '.join(string.split())


def get_features(path: str, test_rail):
    if path.split('.')[-1] == 'feature':
        feature_files = [path]
    else:
        feature_files = tuple(f"{root}/{file}" for root, dirs, files in os.walk(path, topdown=False)
                              for file in files if file.split('.')[-1] == 'feature')
    features = []
    suites_list = test_rail.suites.get_suites()
    custom_tags = test_rail.case_fields._service_case_fields()
    case_types = test_rail.case_types._service_case_types()
    priority_list = test_rail.priorities._service_priorities()
    sections = {suite.id: test_rail.sections.get_sections(suite.id) for suite in suites_list}
    for feature in feature_files:
        parsed_feature = get_feature(feature)
        for scenario in parsed_feature.children:
            tags = list(tag['name'].lower().replace('@', '') for tag in scenario['scenario']['tags'])
            scenario['scenario']['custom_fields'], scenario['scenario']['types'], scenario['scenario']['priority'] = \
                _get_case_options(tags, custom_tags, case_types, priority_list)

        suite_id = tuple(suite.id for suite in suites_list if parsed_feature.main_suite == suite.name)
        if len(suite_id) > 0:
            parsed_feature.main_suite = suite_id[0]
            section_id = tuple(section.id for section in sections[parsed_feature.main_suite] if
                               section.name == parsed_feature.last_section)
            if len(section_id) > 0:
                parsed_feature.last_section = section_id[0]

        features.append(parsed_feature)
    return features


def get_feature(file_path: str):
    with open(file_path, "r") as file:
        feature = TrFeature(Parser().parse(TokenScanner(file.read()))['feature'], file_path)
    examples_scenarios = []
    for scenario in feature.children:
        if len(scenario['scenario']['examples']) > 0:
            examples = scenario['scenario']['examples'][0]
            examples_names = tuple(var_name['value'] for var_name in examples['tableHeader']['cells'])
            examples_values = []
            for var in tuple(var['cells'] for var in examples['tableBody']):
                examples_values.append([y['value'] for y in var])
            for example in examples_values:
                sc = deepcopy(scenario)
                for index, name in enumerate(examples_names):
                    sc['scenario']['name'] = sc['scenario']['name'].replace(f'<{name}>', example[index])
                    for step in sc['scenario']['steps']:
                        step['content'] = step['content'].replace(f'<{name}>', example[index])
                examples_scenarios.append(sc)
            feature.children.remove(scenario)
    for scenario in examples_scenarios:
        feature.children.append(scenario)
    return feature


def _make_step(step: dict) -> str:
    return {'content': f'**{step["keyword"].replace(" ", "")}:** {trim(step["text"])}', 'expected': ''}


def _get_case_options(case_tags: list, tr_tags: dict, tr_case_types: dict, tr_priority: dict):
    custom_fields, cases_type, priority = dict(), [], None
    for key, value in tr_tags.items():
        if key in case_tags:
            if value['name'] in custom_fields:
                custom_fields[value['name']].append(value['id'])
            else:
                custom_fields[value['name']] = [value['id']]
            case_tags.remove(key)
    for key, value in custom_fields.items():
        if len(value) == 1:
            custom_fields[key] = value[0]
    for key, value in PRIORITY_REPLACE.items():
        for val in value:
            if val.lower() in case_tags:
                priority = tr_priority[key.lower()]
                break
    if priority is None:
        priority = tr_priority['low']
    for key, value in tr_case_types.items():
        if key in case_tags:
            cases_type.append(value), case_tags.remove(key)

    return custom_fields, cases_type, priority


def replace_examples(where: str, examples: list, variables: str, all_vars: list):
    current_vars, variables = [], variables.lower()
    for var in all_vars:
        if all((x.lower() in variables for x in var)):
            current_vars = var
            break
    for index, param in enumerate(examples):
        if len(current_vars) > index:
            where = where.replace(f'<{param}>', current_vars[index])
    return where


def to_json(obj_list: List[object]) -> dict:
    return tuple(obj.to_json() if 'to_json' in dir(obj) else obj.__dict__ for obj in obj_list)


def split_list(array: List[Union[tuple, list]], separator: int = 250) -> list:
    if isinstance(array, (tuple, list)):
        if isinstance(separator, int):
            if len(array) > 0:
                result, index = [], 0
                while True:
                    result.append(array[index:index + separator])
                    index += separator
                    if index > len(array):
                        break
                return result
            else:
                return []
        else:
            raise ValueError('separator must be integer')
    else:
        raise ValueError('array variable must be tuple or list')


def validate_variable(variable, var_types, var_name: str):
    if not isinstance(variable, var_types):
        raise ValueError(f'{var_name} must be {var_types}')


def _write_feature(file_path: str, line: int, column: int, value: str) -> None:
    def count_symbols(to_line: str, arr: list) -> int:
        return sum((len(length.encode()) for length in arr[:to_line]))

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        symbols_count = count_symbols(line - 1, lines) + column
        file.seek(symbols_count)
        rem = file.read()
        file.seek(symbols_count)
        file.write(f'{value} {rem}')
