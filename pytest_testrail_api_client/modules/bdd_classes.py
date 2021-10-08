class TrFeature:
    def __init__(self, data: dict):
        if data is not None:
            self.tags: list = data.get('tags')
            self.location: dict = data.get('location')
            self.language: str = data.get('language')
            self.keyword: str = data.get('keyword')
            self.name: str = data.get('name')
            self.description: str = data.get('description')
            self.children: list = data.get('children')
            self.main_suite, self.last_section = None, None
            self.background = None
            if self.name is not None:
                name = self.name.split(' - ')
                self.main_suite, self.last_section = name[0], name[-1]
            if self.children is not None:
                for scenario in self.children:
                    pass

