from src.Domain.base_entities import Attachments
from src.SharedKernel.persistence.CrudRepository import CrudRepository
from src.SharedKernel.base.Container import Repository
import uuid

@Repository
class AttachmentRepository(CrudRepository[Attachments, uuid.UUID]):
    def __init__(self):
        super().__init__()
        self.model = Attachments

    async def search_attachment(self):
        table_name = self.get_table_name()
        query = f"SELECT * FROM {table_name}"
        result = await self.fetch_all(query)
        return result
