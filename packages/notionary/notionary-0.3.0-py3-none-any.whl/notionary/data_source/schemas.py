from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.data_source.properties.schemas import DiscriminatedDataSourceProperty
from notionary.page.schemas import NotionPageDto
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.parent import Parent


class UpdateDataSourceDto(NotionEntityUpdateDto):
    title: list[RichText]
    description: list[RichText]
    archived: bool


class QueryDataSourceResponse(BaseModel):
    results: list[NotionPageDto]
    next_cursor: str | None = None
    has_more: bool


class DataSourceDto(EntityResponseDto):
    database_parent: Parent
    title: list[RichText]
    description: list[RichText]
    archived: bool
    properties: dict[str, DiscriminatedDataSourceProperty]
