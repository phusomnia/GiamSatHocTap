from typing import Any, TypeVar, Generic, Type, Optional, Sequence, Dict
from pydantic import BaseModel
from sqlalchemy import bindparam
from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession
from src.SharedKernel.persistence.Database import DatabaseSessionConfig

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID")

class CrudRepository(Generic[T, ID]):
    def __init__(self):
        self.session = DatabaseSessionConfig().session

    def get_table_name(self) -> str:
        """Get table name with proper quoting for MySQL or PostgreSQL."""
        table_args = getattr(self.model, '__table_args__', {})
        schema = None

        if isinstance(table_args, (list, tuple)):
            for arg in table_args:
                if isinstance(arg, dict) and 'schema' in arg:
                    schema = arg['schema']
                    break

        # PostgreSQL: use double quotes with schema prefix if specified
        if schema:
            return f'{schema}."{self.model.__tablename__}"'
        # PostgreSQL without schema or MySQL
        return f'"{self.model.__tablename__}"'

    async def find_all(self) -> Sequence[T]:
        result = await self.session.exec(select(self.model))
        return result.all()

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def find_by_id(self, id: str(ID)) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def update(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def delete(self, entity: BaseModel) -> None:
        await self.session.delete(entity)
        await self.session.commit()

    async def fetch_all(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Sequence[Dict[str, Any]]:
        """Query with raw SQL and bindparams, returns list of dicts."""
        stmt = text(sql)
        if params:
            stmt = stmt.bindparams(**params)
        result = await self.session.exec(stmt)
        return [dict(row) for row in result.mappings()]

    async def fetch_one(self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        """Fetch single result with raw SQL and bindparams."""
        stmt = text(sql)
        if params:
            stmt = stmt.bindparams(**params)
        result = await self.session.exec(stmt)
        return result.first()

    async def execute(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        commit: bool = False
    ):
        """Execute raw SQL with optional commit/rollback."""
        try:
            stmt = text(sql)
            if params is not None:
                stmt = stmt.bindparams(**params)

            result = await self.session.exec(stmt)

            if commit:
                await self.session.commit()

            return result.all()
        except Exception as e:
            if commit:
                await self.session.rollback()
            raise e

    def update_model_from_dto(
        self,
        model: T,
        dto: BaseModel
    ) -> T:
        """Auto-map fields from DTO to entity, only updating valid values."""
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value not in [None, "None", ""] and hasattr(model, field):
                setattr(model, field, value)
        return model