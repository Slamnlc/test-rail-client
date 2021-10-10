import os
from datetime import datetime

from _pytest.config import Config
from _pytest.main import Session
from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner

from pytest_testrail_api_client.modules.bdd_classes import TrFeature


def get_dict_from_locals(locals_dict: dict, replace_underscore: bool = False, exclude: list = None):
    exclude = tuple('self', ) if exclude is None else tuple(['self'] + exclude)
    return {key if replace_underscore else key: value for key, value in
            locals_dict.items() if key not in exclude and '__py' not in key and value is not None}


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
    feature_files = tuple(f"{root}/{file}" for root, dirs, files in os.walk(path, topdown=False)
                          for file in files if file.split('.')[-1] == 'feature')
    features = []
    suites_list = test_rail.suites.get_suites()
    sections = {suite.id: test_rail.sections.get_sections(suite.id) for suite in suites_list}
    for feature in feature_files:
        parsed_feature = TrFeature(get_feature(feature))
        suite_id = tuple(suite.id for suite in suites_list if parsed_feature.main_suite == suite.name)
        if len(suite_id) > 0:
            parsed_feature.main_suite = suite_id[0]
            section_id = tuple(section.id for section in sections[parsed_feature.main_suite] if
                               section.name == parsed_feature.last_section)
            if len(section_id) > 0:
                section_id = section_id[0]

        features.append(TrFeature(get_feature(feature)))
    1 == 1


def get_feature(file_path: str):
    with open(file_path, "r") as file:
        return Parser().parse(TokenScanner(file.read()))['feature']


def make_step(step: dict) -> str:
    return f'**{step["keyword"].replace(" ", "")}** {trim(step["text"])}'
