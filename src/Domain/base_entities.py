from typing import Optional
import datetime
import uuid

from sqlalchemy import BigInteger, Column, DateTime, Index, PrimaryKeyConstraint, String, Uuid, text
from sqlmodel import Field, SQLModel

class Attachments(SQLModel, table=True):
    __tablename__ = 'Attachments'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Attachments_pkey'),
        Index('Attachments_file_hash_idx', 'file_hash'),
        Index('Attachments_uploaded_at_idx', 'uploaded_at'),
        Index('Attachments_uploaded_by_idx', 'uploaded_by'),
        Index('Attachments_uploaded_by_uploaded_at_idx', 'uploaded_by', 'uploaded_at')
    )

    id: uuid.UUID = Field(sa_column=Column('id', Uuid, primary_key=True, server_default=text('gen_random_uuid()')))
    filename: Optional[str] = Field(default=None, sa_column=Column('filename', String(255)))
    original_name: Optional[str] = Field(default=None, sa_column=Column('original_name', String(255)))
    file_path: Optional[str] = Field(default=None, sa_column=Column('file_path', String(500)))
    file_size: Optional[int] = Field(default=None, sa_column=Column('file_size', BigInteger))
    mime_type: Optional[str] = Field(default=None, sa_column=Column('mime_type', String(100)))
    file_hash: Optional[str] = Field(default=None, sa_column=Column('file_hash', String(64)))
    url: Optional[str] = Field(default=None, sa_column=Column('url', String(255)))
    uploaded_by: Optional[uuid.UUID] = Field(default=None, sa_column=Column('uploaded_by', Uuid))
    uploaded_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('uploaded_at', DateTime))
    deleted_at: Optional[datetime.datetime] = Field(default=None, sa_column=Column('deleted_at', DateTime))
