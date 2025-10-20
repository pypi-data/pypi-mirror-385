from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class ParentType(StrEnum):
    DATABASE_ID = "database_id"
    DATA_SOURCE_ID = "data_source_id"
    PAGE_ID = "page_id"
    BLOCK_ID = "block_id"
    WORKSPACE = "workspace"


class DataSourceParent(BaseModel):
    type: Literal[ParentType.DATA_SOURCE_ID]
    data_source_id: str
    database_id: str


class PageParent(BaseModel):
    type: Literal[ParentType.PAGE_ID]
    page_id: str


class BlockParent(BaseModel):
    type: Literal[ParentType.BLOCK_ID]
    block_id: str


class WorkspaceParent(BaseModel):
    type: Literal[ParentType.WORKSPACE]
    workspace: bool


class DatabaseParent(BaseModel):
    type: Literal[ParentType.DATABASE_ID]
    database_id: str


Parent = DataSourceParent | PageParent | BlockParent | WorkspaceParent | DatabaseParent
