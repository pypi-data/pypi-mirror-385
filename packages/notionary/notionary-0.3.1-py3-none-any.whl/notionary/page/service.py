from collections.abc import Callable
from typing import Self

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.rich_text.rich_text_markdown_converter import convert_rich_text_to_markdown
from notionary.comments.models import Comment
from notionary.comments.service import CommentService
from notionary.page.content.factory import PageContentServiceFactory
from notionary.page.content.markdown.builder import MarkdownBuilder
from notionary.page.content.service import PageContentService
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.factory import PagePropertyHandlerFactory
from notionary.page.properties.models import PageTitleProperty
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import NotionPageDto
from notionary.shared.entity.service import Entity
from notionary.workspace.query.service import WorkspaceQueryService


class NotionPage(Entity):
    def __init__(
        self,
        dto: NotionPageDto,
        title: str,
        page_property_handler: PagePropertyHandler,
        block_client: NotionBlockHttpClient,
        comment_service: CommentService,
        page_content_service: PageContentService,
        metadata_update_client: PageMetadataUpdateClient,
    ) -> None:
        super().__init__(dto=dto)

        self._title = title
        self._archived = dto.archived

        self._block_client = block_client
        self._comment_service = comment_service
        self._page_content_service = page_content_service
        self._metadata_update_client = metadata_update_client
        self.properties = page_property_handler

    @classmethod
    async def from_id(
        cls,
        page_id: str,
        page_property_handler_factory: PagePropertyHandlerFactory | None = None,
    ) -> Self:
        factory = page_property_handler_factory or PagePropertyHandlerFactory()
        dto = await cls._fetch_page_dto(page_id)
        return await cls._create_from_dto(dto, factory)

    @classmethod
    async def from_title(
        cls,
        page_title: str,
        search_service: WorkspaceQueryService | None = None,
    ) -> Self:
        service = search_service or WorkspaceQueryService()
        return await service.find_page(page_title)

    @classmethod
    async def _fetch_page_dto(cls, page_id: str) -> NotionPageDto:
        async with NotionPageHttpClient(page_id=page_id) as client:
            return await client.get_page()

    @classmethod
    async def _create_from_dto(
        cls,
        dto: NotionPageDto,
        page_property_handler_factory: PagePropertyHandlerFactory,
    ) -> Self:
        title_task = cls._extract_title_from_dto(dto)
        page_property_handler = page_property_handler_factory.create_from_page_response(dto)

        title = await title_task

        return cls._create_with_dependencies(
            dto=dto,
            title=title,
            page_property_handler=page_property_handler,
        )

    @classmethod
    def _create_with_dependencies(
        cls,
        dto: NotionPageDto,
        title: str,
        page_property_handler: PagePropertyHandler,
    ) -> Self:
        block_client = NotionBlockHttpClient()
        comment_service = CommentService()

        page_content_service_factory = PageContentServiceFactory()
        page_content_service = page_content_service_factory.create(page_id=dto.id, block_client=block_client)

        metadata_update_client = PageMetadataUpdateClient(page_id=dto.id)

        return cls(
            dto=dto,
            title=title,
            page_property_handler=page_property_handler,
            block_client=block_client,
            comment_service=comment_service,
            page_content_service=page_content_service,
            metadata_update_client=metadata_update_client,
        )

    @staticmethod
    async def _extract_title_from_dto(response: NotionPageDto) -> str:
        title_property = next(
            (prop for prop in response.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )
        rich_text_title = title_property.title if title_property else []
        return await convert_rich_text_to_markdown(rich_text_title)

    @property
    def _entity_metadata_update_client(self) -> PageMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def archived(self) -> bool:
        return self._archived

    @property
    def markdown_builder() -> MarkdownBuilder:
        return MarkdownBuilder()

    async def get_comments(self) -> list[Comment]:
        return await self._comment_service.list_all_comments_for_page(page_id=self._id)

    async def post_top_level_comment(self, comment: str) -> None:
        await self._comment_service.create_comment_on_page(page_id=self._id, text=comment)

    async def post_reply_to_discussion(self, discussion_id: str, comment: str) -> None:
        await self._comment_service.reply_to_discussion_by_id(discussion_id=discussion_id, text=comment)

    async def set_title(self, title: str) -> None:
        await self.properties.set_title_property(title)
        self._title = title

    async def append_markdown(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder]),
    ) -> None:
        await self._page_content_service.append_markdown(content=content)

    async def replace_content(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder]),
    ) -> None:
        await self._page_content_service.clear()
        await self._page_content_service.append_markdown(content=content)

    async def clear_page_content(self) -> None:
        await self._page_content_service.clear()

    async def get_markdown_content(self) -> str:
        return await self._page_content_service.get_as_markdown()
