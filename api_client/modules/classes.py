from api_client.service import get_date_from_timestamp


class CaseType:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.is_default: bool = data.get('is_default')

    def __str__(self):
        return f'{self.name}, id = {self.id}'


class Project:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.announcement = data.get('announcement')
            self.show_announcement: bool = data.get('show_announcement')
            self.is_completed: bool = data.get('is_completed')
            self.completed_on = data.get('completed_on')
            self.suite_mode: int = data.get('suite_mode')
            self.url: str = data.get('url')

    def __str__(self):
        return self.name


class Status:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.label: str = data.get('label')
            self.color_dark: int = data.get('color_dark')
            self.color_medium: int = data.get('color_medium')
            self.color_bright: int = data.get('color_bright')
            self.is_system: bool = data.get('is_system')
            self.is_untested: bool = data.get('is_untested')
            self.is_final: bool = data.get('is_final')

    def __str__(self):
        return self.label


class User:
    def __init__(self, data: dict):
        if data is not None:
            self.name: str = data.get('name')
            self.id: int = data.get('id')
            self.email: str = data.get('email')
            self.is_active: bool = data.get('is_active')
            self.role_id: int = data.get('role_id')
            self.role: str = data.get('role')

    def __str__(self):
        return self.name


class Suite:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.description = data.get('description')
            self.project_id: int = data.get('project_id')
            self.is_master: bool = data.get('is_master')
            self.is_baseline: bool = data.get('is_baseline')
            self.is_completed: bool = data.get('is_completed')
            self.completed_on = data.get('completed_on')
            self.url: str = data.get('url')

    def __str__(self):
        return f'{self.name}, id = {self.id}'


class Template:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.is_default: bool = data.get('is_default')

    def __str__(self):
        return f'{self.name}, id = {self.id}'


class ResultField:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.is_active: bool = data.get('is_active')
            self.type_id: int = data.get('type_id')
            self.name: str = data.get('name')
            self.system_name: str = data.get('system_name')
            self.label: str = data.get('label')
            self.description = data.get('description')
            self.configs: list = data.get('configs')
            self.display_order: int = data.get('display_order')
            self.include_all: bool = data.get('include_all')
            self.template_ids: list = data.get('template_ids')

    def __str__(self):
        return self.label


class Priority:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.short_name: str = data.get('short_name')
            self.is_default: bool = data.get('is_default')
            self.priority: int = data.get('priority')

    def __str__(self):
        return self.name


class Section:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.suite_id: int = data.get('suite_id')
            self.name: str = data.get('name')
            self.description: str = data.get('description')
            self.parent_id = data.get('parent_id')
            self.display_order: int = data.get('display_order')
            self.depth: int = data.get('depth')

    def __str__(self):
        return self.name


class Milestone:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.description: str = data.get('description')
            self.start_on = get_date_from_timestamp(data.get('start_on'))
            self.started_on: int = get_date_from_timestamp(data.get('started_on'))
            self.is_started: bool = data.get('is_started')
            self.due_on = get_date_from_timestamp(data.get('due_on'))
            self.is_completed: bool = data.get('is_completed')
            self.completed_on: int = data.get('completed_on')
            self.project_id: int = data.get('project_id')
            self.parent_id = data.get('parent_id')
            self.refs: str = data.get('refs')
            self.url: str = data.get('url')
            self.milestones: list = data.get('milestones')

    def __str__(self):
        return self.name
