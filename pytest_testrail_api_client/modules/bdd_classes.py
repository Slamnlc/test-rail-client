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
