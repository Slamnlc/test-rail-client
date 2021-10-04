import pytest

def pytest_collection_modifyitems(config, items):
    if 'tags' in config.option:
        raw_tags = config.option.tags
        for item in items:
            item_tags = [marker.name for marker in item.own_markers]
