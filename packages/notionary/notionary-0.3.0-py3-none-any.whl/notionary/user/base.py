from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Self

from notionary.exceptions.search import NoUsersInWorkspace, UserNotFound
from notionary.user.client import UserHttpClient
from notionary.user.schemas import UserResponseDto, UserType
from notionary.utils.fuzzy import find_all_matches

if TYPE_CHECKING:
    from notionary.user.bot import BotUser
    from notionary.user.person import PersonUser


class BaseUser:
    def __init__(
        self,
        id: str,
        name: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        self._id = id
        self._name = name
        self._avatar_url = avatar_url

    @classmethod
    async def from_id_auto(
        cls,
        user_id: str,
        http_client: UserHttpClient | None = None,
    ) -> BotUser | PersonUser:
        from notionary.user.bot import BotUser
        from notionary.user.person import PersonUser

        client = http_client or UserHttpClient()
        user_dto = await client.get_user_by_id(user_id)

        if user_dto.type == UserType.BOT:
            return BotUser.from_dto(user_dto)
        elif user_dto.type == UserType.PERSON:
            return PersonUser.from_dto(user_dto)
        else:
            raise ValueError(f"Unknown user type: {user_dto.type}")

    @classmethod
    async def from_id(
        cls,
        user_id: str,
        http_client: UserHttpClient | None = None,
    ) -> Self:
        client = http_client or UserHttpClient()
        user_dto = await client.get_user_by_id(user_id)

        expected_type = cls._get_expected_user_type()
        if user_dto.type != expected_type:
            raise ValueError(f"User {user_id} is not a '{expected_type.value}', but '{user_dto.type.value}'")

        return cls.from_dto(user_dto)

    @classmethod
    async def from_name(
        cls,
        name: str,
        http_client: UserHttpClient | None = None,
    ) -> Self:
        client = http_client or UserHttpClient()
        all_users = await cls._get_all_users_of_type(client)

        user_type = cls._get_expected_user_type().value

        if not all_users:
            raise NoUsersInWorkspace(user_type)

        exact_match = cls._find_exact_match(all_users, name)
        if exact_match:
            return exact_match

        suggestions = cls._get_fuzzy_suggestions(all_users, name)
        raise UserNotFound(user_type, name, suggestions)

    @classmethod
    def _find_exact_match(cls, users: list[Self], query: str) -> Self | None:
        query_lower = query.lower()
        for user in users:
            if user.name and user.name.lower() == query_lower:
                return user
        return None

    @classmethod
    def _get_fuzzy_suggestions(cls, users: list[Self], query: str) -> list[str]:
        sorted_by_similarity = find_all_matches(
            query=query,
            items=users,
            text_extractor=cls._get_name_extractor(),
            min_similarity=0.6,
        )

        if sorted_by_similarity:
            return [user.name for user in sorted_by_similarity[:5] if user.name]

        return [user.name for user in users[:5] if user.name]

    @classmethod
    async def _get_all_users_of_type(cls, http_client: UserHttpClient) -> list[Self]:
        all_workspace_user_dtos = await http_client.get_all_workspace_users()
        expected_type = cls._get_expected_user_type()
        filtered_dtos = [dto for dto in all_workspace_user_dtos if dto.type == expected_type]
        return [cls.from_dto(dto) for dto in filtered_dtos]

    @classmethod
    @abstractmethod
    def _get_expected_user_type(cls) -> UserType:
        pass

    @classmethod
    @abstractmethod
    def from_dto(cls, user_dto: UserResponseDto) -> Self:
        pass

    @classmethod
    def _get_name_extractor(cls):
        return lambda user: user.name or ""

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def avatar_url(self) -> str | None:
        return self._avatar_url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r}, name={self._name!r})"
