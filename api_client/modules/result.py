from api_client.modules.category import Base
from api_client.modules.session import Session
from api_client.service import get_date_from_timestamp


class Result(Base):
    def __init__(self, session: Session, data: dict):
        super().__init__(session)
        self.session = session
        if data is not None:
            self.id: int = data.get('id')
            self.test_id: int = data.get('test_id')
            self.status_id: int = data.get('status_id')
            self.created_on = get_date_from_timestamp(data.get('created_on'))
            self.assignedto_id = data.get('assignedto_id')
            self.comment = data.get('comment')
            self.version = data.get('version')
            self.elapsed = data.get('elapsed')
            self.defects = data.get('defects')
            self.created_by: int = data.get('created_by')
            self.custom_step_results: list = data.get('custom_step_results')
            self.attachment_ids: list = data.get('attachment_ids')
