import pytest_testrail_api_client.service as service


class TrFeature:
    def __init__(self, data: dict, path: str):
        if data is not None:
            self.path = path
            self.tags: list = data.get('tags')
            self.location: dict = data.get('location')
            self.language: str = data.get('language')
            self.keyword: str = data.get('keyword')
            self.name: str = data.get('name')
            if self.name is not None:
                self.name = service.trim(self.name)
            self.description: str = data.get('description')
            self.children: list = data.get('children')
            self.main_suite, self.last_section = None, None
            self.background = None
            if self.name is not None:
                name = self.name.split(' - ')
                self.main_suite, self.last_section = name[0], name[-1]
            if self.children is not None:
                background = tuple(filter(lambda x: 'background' in x, self.children))
                if len(background) > 0:
                    background = [service._make_step(step) for step in background[0]['background']['steps']]
                    self.children.pop(0)
                else:
                    background = None
                self.children = list(filter(lambda scenario: 'scenario' in scenario, self.children))
                for scenario in self.children:
                    if background is not None:
                        scenario['scenario']['steps'] = background + [service._make_step(step) for step in
                                                                      scenario['scenario']['steps']]
