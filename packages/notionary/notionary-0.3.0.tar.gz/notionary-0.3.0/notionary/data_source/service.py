from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from typing import TYPE_CHECKING, Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.data_source.http.client import DataSourceClient
from notionary.data_source.http.data_source_instance_client import DataSourceInstanceClient
from notionary.data_source.properties.schemas import (
    DataSourceMultiSelectProperty,
    DataSourceProperty,
    DataSourcePropertyOption,
    DataSourcePropertyT,
    DataSourceRelationProperty,
    DataSourceSelectProperty,
    DataSourceStatusProperty,
)
from notionary.data_source.query.builder import DataSourceQueryBuilder
from notionary.data_source.query.resolver import QueryResolver
from notionary.data_source.query.schema import (
    DataSourceQueryParams,
)
from notionary.data_source.schema.service import DataSourcePropertySchemaFormatter
from notionary.data_source.schemas import DataSourceDto
from notionary.exceptions.data_source.properties import DataSourcePropertyNotFound, DataSourcePropertyTypeError
from notionary.page.properties.models import PageTitleProperty
from notionary.page.schemas import NotionPageDto
from notionary.shared.entity.dto_parsers import (
    extract_cover_image_url_from_dto,
    extract_database_id,
    extract_description,
    extract_emoji_icon_from_dto,
    extract_external_icon_url_from_dto,
    extract_title,
)
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.entity.service import Entity
from notionary.user.schemas import PartialUserDto
from notionary.workspace.query.service import WorkspaceQueryService

if TYPE_CHECKING:
    from notionary import NotionDatabase, NotionPage


class NotionDataSource(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        archived: bool,
        in_trash: bool,
        url: str,
        properties: dict[str, DataSourceProperty],
        parent_database_id: str | None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        public_url: str | None = None,
        data_source_instance_client: DataSourceInstanceClient | None = None,
        query_resolver: QueryResolver | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._parent_database_id = parent_database_id
        self._parent_database: NotionDatabase | None = None
        self._title = title
        self._archived = archived
        self._url = url
        self._public_url = public_url
        self._description = description
        self._properties = properties or {}
        self._data_source_client = data_source_instance_client or DataSourceInstanceClient(data_source_id=id)
        self.query_resolver = query_resolver or QueryResolver()

    @classmethod
    async def from_id(
        cls,
        data_source_id: str,
        data_source_client: DataSourceClient | None = None,
        rich_text_converter: RichTextToMarkdownConverter | None = None,
    ) -> Self:
        client = data_source_client or DataSourceClient()
        converter = rich_text_converter or RichTextToMarkdownConverter()
        data_source_dto = await client.get_data_source(data_source_id)
        return await cls._create_from_dto(data_source_dto, converter)

    @classmethod
    async def from_title(
        cls,
        data_source_title: str,
        search_service: WorkspaceQueryService | None = None,
    ) -> Self:
        service = search_service or WorkspaceQueryService()
        return await service.find_data_source(data_source_title)

    @classmethod
    async def _create_from_dto(
        cls,
        response: DataSourceDto,
        rich_text_converter: RichTextToMarkdownConverter,
    ) -> Self:
        title, description = await asyncio.gather(
            extract_title(response, rich_text_converter),
            extract_description(response, rich_text_converter),
        )

        parent_database_id = extract_database_id(response)

        return cls._create(
            id=response.id,
            title=title,
            description=description,
            created_time=response.created_time,
            created_by=response.created_by,
            last_edited_time=response.last_edited_time,
            last_edited_by=response.last_edited_by,
            archived=response.archived,
            in_trash=response.in_trash,
            url=response.url,
            properties=response.properties,
            parent_database_id=parent_database_id,
            emoji_icon=extract_emoji_icon_from_dto(response),
            external_icon_url=extract_external_icon_url_from_dto(response),
            cover_image_url=extract_cover_image_url_from_dto(response),
            public_url=response.url,
        )

    @classmethod
    def _create(
        cls,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        archived: bool,
        in_trash: bool,
        url: str,
        properties: dict[str, DataSourceProperty],
        parent_database_id: str | None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
        description: str | None = None,
        public_url: str | None = None,
    ) -> Self:
        data_source_instance_client = DataSourceInstanceClient(data_source_id=id)
        return cls(
            id=id,
            title=title,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            archived=archived,
            in_trash=in_trash,
            url=url,
            parent_database_id=parent_database_id,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
            description=description,
            public_url=public_url,
            properties=properties,
            data_source_instance_client=data_source_instance_client,
        )

    @property
    def _entity_metadata_update_client(self) -> EntityMetadataUpdateClient:
        return self._data_source_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def archived(self) -> bool:
        return self._archived

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def properties(self) -> dict[str, DataSourceProperty]:
        return self._properties

    @property
    def url(self) -> str:
        return self._url

    @property
    def public_url(self) -> str | None:
        return self._public_url

    async def get_parent_database(self) -> NotionDatabase | None:
        if self._parent_database is None and self._parent_database_id:
            self._parent_database = await NotionDatabase.from_id(self._parent_database_id)
        return self._parent_database

    async def create_blank_page(self, title: str | None = None) -> NotionPage:
        return await self._data_source_client.create_blank_page(title=title)

    async def set_title(self, title: str) -> None:
        data_source_dto = await self._data_source_client.update_title(title)
        self._title = data_source_dto.title

    async def archive(self) -> None:
        if self._archived:
            self.logger.info("Data source is already archived.")
            return
        await self._data_source_client.archive()
        self._archived = True

    async def unarchive(self) -> None:
        if not self._archived:
            self.logger.info("Data source is not archived.")
            return
        await self._data_source_client.unarchive()
        self._archived = False

    async def update_description(self, description: str) -> None:
        self._description = await self._data_source_client.update_description(description)

    async def get_options_for_property_by_name(self, property_name: str) -> list[str]:
        prop = self._properties.get(property_name)

        if prop is None:
            return []

        if isinstance(prop, DataSourceSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceMultiSelectProperty):
            return prop.option_names

        if isinstance(prop, DataSourceStatusProperty):
            return prop.option_names

        if isinstance(prop, DataSourceRelationProperty):
            return await self._get_relation_options(prop)

        return []

    def get_select_options_by_property_name(self, property_name: str) -> list[str]:
        select_prop = self._get_typed_property_or_raise(property_name, DataSourceSelectProperty)
        return select_prop.option_names

    def get_multi_select_options_by_property_name(self, property_name: str) -> list[DataSourcePropertyOption]:
        multi_select_prop = self._get_typed_property_or_raise(property_name, DataSourceMultiSelectProperty)
        return multi_select_prop.option_names

    def get_status_options_by_property_name(self, property_name: str) -> list[str]:
        status_prop = self._get_typed_property_or_raise(property_name, DataSourceStatusProperty)
        return status_prop.option_names

    async def get_relation_options_by_property_name(self, property_name: str) -> list[str]:
        relation_prop = self._get_typed_property_or_raise(property_name, DataSourceRelationProperty)
        return await self._get_relation_options(relation_prop)

    async def _get_relation_options(self, relation_prop: DataSourceRelationProperty) -> list[str]:
        related_data_source_id = relation_prop.related_data_source_id
        if not related_data_source_id:
            return []

        async with DataSourceInstanceClient(related_data_source_id) as related_client:
            search_results = await related_client.query()

        page_titles = []
        for page_response in search_results.results:
            title = self._extract_title_from_notion_page_dto(page_response)
            if title:
                page_titles.append(title)

        return page_titles

    def _extract_title_from_notion_page_dto(self, page: NotionPageDto) -> str | None:
        if not page.properties:
            return None

        title_property = next(
            (prop for prop in page.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )

        if not title_property:
            return None

        return "".join(item.plain_text for item in title_property.title)

    def _get_typed_property_or_raise(self, name: str, property_type: type[DataSourcePropertyT]) -> DataSourcePropertyT:
        prop = self._properties.get(name)

        if prop is None:
            raise DataSourcePropertyNotFound(
                property_name=name,
                available_properties=list(self._properties.keys()),
            )

        if not isinstance(prop, property_type):
            raise DataSourcePropertyTypeError(
                property_name=name, expected_type=property_type.__name__, actual_type=type(prop).__name__
            )

        return prop

    def filter(self) -> DataSourceQueryBuilder:
        return DataSourceQueryBuilder(properties=self._properties)

    async def query_pages(
        self, filter_fn: Callable[[DataSourceQueryBuilder], DataSourceQueryBuilder]
    ) -> list[NotionPage]:
        builder = DataSourceQueryBuilder(properties=self._properties)
        configured_builder = filter_fn(builder)
        query_params = configured_builder.build()

        return await self.get_pages(query_params)

    async def query_pages_stream(
        self, filter_fn: Callable[[DataSourceQueryBuilder], DataSourceQueryBuilder]
    ) -> AsyncIterator[NotionPage]:
        builder = DataSourceQueryBuilder(properties=self._properties)
        configured_builder = filter_fn(builder)
        query_params = configured_builder.build()

        async for page in self.get_pages_stream(query_params):
            yield page

    async def get_pages(
        self,
        query_params: DataSourceQueryParams | None = None,
    ) -> list[NotionPage]:
        from notionary import NotionPage

        resolved_params = await self._resolve_query_params_if_needed(query_params)
        query_response = await self._data_source_client.query(query_params=resolved_params)
        return [await NotionPage.from_id(page.id) for page in query_response.results]

    async def get_pages_stream(
        self,
        query_params: DataSourceQueryParams | None = None,
    ) -> AsyncIterator[NotionPage]:
        from notionary import NotionPage

        resolved_params = await self._resolve_query_params_if_needed(query_params)

        async for page in self._data_source_client.query_stream(query_params=resolved_params):
            yield await NotionPage.from_id(page.id)

    async def _resolve_query_params_if_needed(
        self,
        query_params: DataSourceQueryParams | None,
    ) -> DataSourceQueryParams | None:
        if query_params is None:
            return None

        return await self.query_resolver.resolve_params(query_params)

    async def get_schema_description(self) -> str:
        formatter = DataSourcePropertySchemaFormatter(relation_options_fetcher=self._get_relation_options)
        return await formatter.format(title=self._title, description=self._description, properties=self._properties)
