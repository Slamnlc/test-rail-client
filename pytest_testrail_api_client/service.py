from datetime import datetime

from _pytest.config import Config
from _pytest.main import Session


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
        return args[0].replace(' ', '').split(',') if isinstance(args[0], (tuple, list)) else args[0]


def validate_status_id(status_id):
    if status_id is not None:
        if isinstance(status_id, (list, tuple)):
            return ','.join(status_id)
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
