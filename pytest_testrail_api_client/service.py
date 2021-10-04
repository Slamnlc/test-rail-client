import base64
from datetime import datetime


class Auth:
    def __init__(self, username, password):
        self.data = base64.b64encode(b':'.join((username.encode('ascii'),
                                                password.encode('ascii')))).strip().decode('ascii')

    def __call__(self, r):
        r.headers['Authorization'] = f'Basic {self.data}'
        return r

    def __del__(self):
        return 'BasicAuth'


def get_dict_from_locals(locals_dict: dict, replace_underscore: bool = False, exclude: list = None):
    exclude = tuple('self', ) if exclude is None else tuple(['self'] + exclude)
    return {key if replace_underscore else key: value for key, value in
            locals_dict.items() if key not in exclude and '__py' not in key and value is not None}


def split_by_coma(*args):
    def sub_split(value):
        if value is not None:
            if not isinstance(value, (tuple, list)):
                value = value.replace(' ', '').split(',')
            return value

    if all([arg is None for arg in args]):
        return None
    else:
        return [sub_split(val) for val in args]


def get_date_from_timestamp(date):
    return None if date is None else datetime.fromtimestamp(date)
