from itertools import chain

import pytest_testrail_api_client.configure as configure
from pytest_testrail_api_client.modules.category import Base


class ServiceApi(Base):
    def convert_configs_to_ids(self, configs: (str, list)):
        all_configs = tuple(chain.from_iterable((x.configs for x in self._session.configs.get_configs())))
        if isinstance(configs, str):
            configs = configure.trim(configs).split(', ')
        config_ids = []
        for config in configs:
            config_id = [conf_id.id for conf_id in all_configs if conf_id.name.lower() == config.lower()]
            if len(config_id) > 0:
                config_ids.append(config_id[0])
        return config_ids
