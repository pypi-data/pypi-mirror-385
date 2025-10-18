from enum import StrEnum
from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, Field

from notionary.shared.properties.type import PropertyType
from notionary.shared.typings import JsonDict

# ============================================================================
# Base Model
# ============================================================================


class DataSourceProperty(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: PropertyType


# ============================================================================
# Enums and Shared Config Models
# ============================================================================


class PropertyColor(StrEnum):
    DEFAULT = "default"
    GRAY = "gray"
    BROWN = "brown"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"


class NumberFormat(StrEnum):
    NUMBER = "number"
    NUMBER_WITH_COMMAS = "number_with_commas"
    PERCENT = "percent"
    DOLLAR = "dollar"
    AUSTRALIAN_DOLLAR = "australian_dollar"
    CANADIAN_DOLLAR = "canadian_dollar"
    SINGAPORE_DOLLAR = "singapore_dollar"
    EURO = "euro"
    POUND = "pound"
    YEN = "yen"
    RUBLE = "ruble"
    RUPEE = "rupee"
    WON = "won"
    YUAN = "yuan"
    REAL = "real"
    LIRA = "lira"
    RUPIAH = "rupiah"
    FRANC = "franc"
    HONG_KONG_DOLLAR = "hong_kong_dollar"
    NEW_ZEALAND_DOLLAR = "new_zealand_dollar"
    KRONA = "krona"
    NORWEGIAN_KRONE = "norwegian_krone"
    MEXICAN_PESO = "mexican_peso"
    RAND = "rand"
    NEW_TAIWAN_DOLLAR = "new_taiwan_dollar"
    DANISH_KRONE = "danish_krone"
    ZLOTY = "zloty"
    BAHT = "baht"
    FORINT = "forint"
    KORUNA = "koruna"
    SHEKEL = "shekel"
    CHILEAN_PESO = "chilean_peso"
    PHILIPPINE_PESO = "philippine_peso"
    DIRHAM = "dirham"
    COLOMBIAN_PESO = "colombian_peso"
    RIYAL = "riyal"
    RINGGIT = "ringgit"
    LEU = "leu"
    ARGENTINE_PESO = "argentine_peso"
    URUGUAYAN_PESO = "uruguayan_peso"
    PERUVIAN_SOL = "peruvian_sol"


class RelationType(StrEnum):
    SINGLE_PROPERTY = "single_property"
    DUAL_PROPERTY = "dual_property"


class RollupFunction(StrEnum):
    AVERAGE = "average"
    CHECKED = "checked"
    COUNT_PER_GROUP = "count_per_group"
    COUNT = "count"
    COUNT_VALUES = "count_values"
    DATE_RANGE = "date_range"
    EARLIEST_DATE = "earliest_date"
    EMPTY = "empty"
    LATEST_DATE = "latest_date"
    MAX = "max"
    MEDIAN = "median"
    MIN = "min"
    NOT_EMPTY = "not_empty"
    PERCENT_CHECKED = "percent_checked"
    PERCENT_EMPTY = "percent_empty"
    PERCENT_NOT_EMPTY = "percent_not_empty"
    PERCENT_PER_GROUP = "percent_per_group"
    PERCENT_UNCHECKED = "percent_unchecked"
    RANGE = "range"
    UNCHECKED = "unchecked"
    UNIQUE = "unique"
    SHOW_ORIGINAL = "show_original"
    SHOW_UNIQUE = "show_unique"
    SUM = "sum"


class DataSourcePropertyOption(BaseModel):
    id: str
    name: str
    color: PropertyColor
    description: str | None = None


class DataSourceStatusGroup(BaseModel):
    id: str
    name: str
    color: PropertyColor
    option_ids: list[str]


# ============================================================================
# Config Models
# ============================================================================


class DataSourceStatusConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)
    groups: list[DataSourceStatusGroup] = Field(default_factory=list)


class DataSourceSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceMultiSelectConfig(BaseModel):
    options: list[DataSourcePropertyOption] = Field(default_factory=list)


class DataSourceRelationConfig(BaseModel):
    data_source_id: str
    type: RelationType = RelationType.SINGLE_PROPERTY
    single_property: JsonDict = Field(default_factory=dict)


class DataSourceNumberConfig(BaseModel):
    format: NumberFormat


class DataSourceFormulaConfig(BaseModel):
    expression: str


class DataSourceUniqueIdConfig(BaseModel):
    prefix: str | None = None


class DataSourceRollupConfig(BaseModel):
    function: RollupFunction
    relation_property_id: str
    relation_property_name: str
    rollup_property_id: str
    rollup_property_name: str


class DataSourceDateConfig(BaseModel): ...


class DataSourceCreatedTimeConfig(BaseModel): ...


class DataSourceCreatedByConfig(BaseModel): ...


class DataSourceLastEditedTimeConfig(BaseModel): ...


class DataSourceLastEditedByConfig(BaseModel): ...


class DataSourceLastVisitedTimeConfig(BaseModel): ...


class DataSourceTitleConfig(BaseModel): ...


class DataSourceRichTextConfig(BaseModel): ...


class DataSourceURLConfig(BaseModel): ...


class DataSourcePeopleConfig(BaseModel): ...


class DataSourceCheckboxConfig(BaseModel): ...


class DataSourceEmailConfig(BaseModel): ...


class DataSourcePhoneNumberConfig(BaseModel): ...


class DataSourceFilesConfig(BaseModel): ...


class DataSourceButtonConfig(BaseModel): ...


class DataSourceLocationConfig(BaseModel): ...


class DataSourceVerificationConfig(BaseModel): ...


class DataSourcePlaceConfig(BaseModel): ...


# ============================================================================
# Property Models
# ============================================================================


class DataSourceStatusProperty(DataSourceProperty):
    type: Literal[PropertyType.STATUS] = PropertyType.STATUS
    status: DataSourceStatusConfig = Field(default_factory=DataSourceStatusConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.status.options]

    @property
    def group_names(self) -> list[str]:
        return [group.name for group in self.status.groups]


class DataSourceSelectProperty(DataSourceProperty):
    type: Literal[PropertyType.SELECT] = PropertyType.SELECT
    select: DataSourceSelectConfig = Field(default_factory=DataSourceSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.select.options]


class DataSourceMultiSelectProperty(DataSourceProperty):
    type: Literal[PropertyType.MULTI_SELECT] = PropertyType.MULTI_SELECT
    multi_select: DataSourceMultiSelectConfig = Field(default_factory=DataSourceMultiSelectConfig)

    @property
    def option_names(self) -> list[str]:
        return [option.name for option in self.multi_select.options]


class DataSourceRelationProperty(DataSourceProperty):
    type: Literal[PropertyType.RELATION] = PropertyType.RELATION
    relation: DataSourceRelationConfig = Field(default_factory=DataSourceRelationConfig)

    @property
    def related_data_source_id(self) -> str | None:
        return self.relation.data_source_id


class DataSourceDateProperty(DataSourceProperty):
    type: Literal[PropertyType.DATE] = PropertyType.DATE
    date: DataSourceDateConfig = Field(default_factory=DataSourceDateConfig)


class DataSourceCreatedTimeProperty(DataSourceProperty):
    type: Literal[PropertyType.CREATED_TIME] = PropertyType.CREATED_TIME
    created_time: DataSourceCreatedTimeConfig = Field(default_factory=DataSourceCreatedTimeConfig)


class DataSourceCreatedByProperty(DataSourceProperty):
    type: Literal[PropertyType.CREATED_BY] = PropertyType.CREATED_BY
    created_by: DataSourceCreatedByConfig = Field(default_factory=DataSourceCreatedByConfig)


class DataSourceLastEditedTimeProperty(DataSourceProperty):
    type: Literal[PropertyType.LAST_EDITED_TIME] = PropertyType.LAST_EDITED_TIME
    last_edited_time: DataSourceLastEditedTimeConfig = Field(default_factory=DataSourceLastEditedTimeConfig)


class DataSourceLastEditedByProperty(DataSourceProperty):
    type: Literal[PropertyType.LAST_EDITED_BY] = PropertyType.LAST_EDITED_BY
    last_edited_by: DataSourceLastEditedByConfig = Field(default_factory=DataSourceLastEditedByConfig)


class DataSourceTitleProperty(DataSourceProperty):
    type: Literal[PropertyType.TITLE] = PropertyType.TITLE
    title: DataSourceTitleConfig = Field(default_factory=DataSourceTitleConfig)


class DataSourceRichTextProperty(DataSourceProperty):
    type: Literal[PropertyType.RICH_TEXT] = PropertyType.RICH_TEXT
    rich_text: DataSourceRichTextConfig = Field(default_factory=DataSourceRichTextConfig)


class DataSourceURLProperty(DataSourceProperty):
    type: Literal[PropertyType.URL] = PropertyType.URL
    url: DataSourceURLConfig = Field(default_factory=DataSourceURLConfig)


class DataSourcePeopleProperty(DataSourceProperty):
    type: Literal[PropertyType.PEOPLE] = PropertyType.PEOPLE
    people: DataSourcePeopleConfig = Field(default_factory=DataSourcePeopleConfig)


class DataSourceNumberProperty(DataSourceProperty):
    type: Literal[PropertyType.NUMBER] = PropertyType.NUMBER
    number: DataSourceNumberConfig

    @property
    def number_format(self) -> NumberFormat:
        return self.number.format


class DataSourceCheckboxProperty(DataSourceProperty):
    type: Literal[PropertyType.CHECKBOX] = PropertyType.CHECKBOX
    checkbox: DataSourceCheckboxConfig = Field(default_factory=DataSourceCheckboxConfig)


class DataSourceEmailProperty(DataSourceProperty):
    type: Literal[PropertyType.EMAIL] = PropertyType.EMAIL
    email: DataSourceEmailConfig = Field(default_factory=DataSourceEmailConfig)


class DataSourcePhoneNumberProperty(DataSourceProperty):
    type: Literal[PropertyType.PHONE_NUMBER] = PropertyType.PHONE_NUMBER
    phone_number: DataSourcePhoneNumberConfig = Field(default_factory=DataSourcePhoneNumberConfig)


class DataSourceFilesProperty(DataSourceProperty):
    type: Literal[PropertyType.FILES] = PropertyType.FILES
    files: DataSourceFilesConfig = Field(default_factory=DataSourceFilesConfig)


class DataSourceFormulaProperty(DataSourceProperty):
    type: Literal[PropertyType.FORMULA] = PropertyType.FORMULA
    formula: DataSourceFormulaConfig

    @property
    def expression(self) -> str:
        return self.formula.expression


class DataSourceRollupProperty(DataSourceProperty):
    type: Literal[PropertyType.ROLLUP] = PropertyType.ROLLUP
    rollup: DataSourceRollupConfig

    @property
    def rollup_function(self) -> RollupFunction:
        return self.rollup.function


class DataSourceUniqueIdProperty(DataSourceProperty):
    type: Literal[PropertyType.UNIQUE_ID] = PropertyType.UNIQUE_ID
    unique_id: DataSourceUniqueIdConfig = Field(default_factory=DataSourceUniqueIdConfig)

    @property
    def prefix(self) -> str | None:
        return self.unique_id.prefix


# ============================================================================
# Discriminated Union
# ============================================================================

DiscriminatedDataSourceProperty = Annotated[
    DataSourceStatusProperty
    | DataSourceSelectProperty
    | DataSourceMultiSelectProperty
    | DataSourceRelationProperty
    | DataSourceDateProperty
    | DataSourceCreatedTimeProperty
    | DataSourceCreatedByProperty
    | DataSourceLastEditedTimeProperty
    | DataSourceLastEditedByProperty
    | DataSourceTitleProperty
    | DataSourceRichTextProperty
    | DataSourceURLProperty
    | DataSourcePeopleProperty
    | DataSourceNumberProperty
    | DataSourceCheckboxProperty
    | DataSourceEmailProperty
    | DataSourcePhoneNumberProperty
    | DataSourceFilesProperty
    | DataSourceFormulaProperty
    | DataSourceRollupProperty
    | DataSourceUniqueIdProperty,
    Field(discriminator="type"),
]

DataSourcePropertyT = TypeVar("DataSourcePropertyT", bound=DataSourceProperty)
