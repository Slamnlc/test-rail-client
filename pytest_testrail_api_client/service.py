import os
from datetime import datetime

from _pytest.config import Config
from _pytest.main import Session
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

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
            return status_id
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
        parsed_feature = TrFeature(get_feature(feature))
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
        return Parser().parse(TokenScanner(file.read()))['feature']


def _make_step(step: dict) -> str:
    return {'content': f'**{step["keyword"].replace(" ", "")}:** {trim(step["text"])}', 'expected': ''}


def _get_case_options(case_tags: list, tr_tags: dict, tr_case_types: dict, tr_priority: dict):
    custom_fields, cases_type, priority = dict(), [], []
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
    for key, value in tr_priority.items():
        if key in case_tags:
            priority.append(value)
    for key, value in tr_case_types.items():
        if key in case_tags:
            cases_type.append(value), case_tags.remove(key)

    return custom_fields, cases_type, priority
