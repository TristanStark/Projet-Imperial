from typing import Optional, List, Dict
from pydantic import BaseModel, Field, RootModel, ConfigDict
from pydantic import model_validator
from typing import Any


# -- Relationship
class Relationship(BaseModel):
    type: str
    uuid: str
    id: str
    relationship: str
    hidden: bool
    name: Optional[str] = None
    img: Optional[str] = None
    shoptype: Optional[str] = None
    role: Optional[str] = None
    alias_id: str


# -- Attributes internes d'une ville
class PlaceAttributes(BaseModel):
    age: Optional[str]
    size: Optional[str]
    government: Optional[str]
    inhabitants: Optional[str]


# -- Flags pour une page de type "place"
class MonksEnhancedJournalPlaceFlags(BaseModel):
    type: str
    _lasttab: Optional[str]
    scrollPos: Optional[str]
    placetype: Optional[str]
    location: Optional[str]
    appendix: Optional[bool]
    attributes: Optional[PlaceAttributes]
    relationships: Optional[List[Relationship]]
    extra_user_data: Optional[Dict[str, Dict[str, str]]] = Field(default_factory=dict, exclude=True)
    pagetype: str
    img: str
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def migrate_extra_user_data(cls, data: Any) -> Any:
        """
        Si 'extra_user_data' est présent, fusionne son contenu au niveau racine du modèle.
        """
        if isinstance(data, dict) and "extra_user_data" in data:
            extra = data.pop("extra_user_data")
            if isinstance(extra, dict):
                data.update(extra)
        return data




class PageFlags(BaseModel):
    monks_enhanced_journal: Optional[MonksEnhancedJournalPlaceFlags] = Field(alias="monks-enhanced-journal")

    model_config = {
        "populate_by_name": True
    }


# -- Composants des pages
class PageTitle(BaseModel):
    show: bool
    level: int


class PageText(BaseModel):
    format: int
    content: str


class PageVideo(BaseModel):
    controls: bool
    volume: float


class PageOwnership(RootModel[Dict[str, int]]):
    pass


class PageStats(BaseModel):
    compendiumSource: Optional[str]
    duplicateSource: Optional[str]
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str


class Page(BaseModel):
    type: str
    name: str
    flags: PageFlags
    id: str = Field(alias="_id")
    system: Dict = Field(default_factory=dict)
    title: PageTitle
    image: Dict = Field(default_factory=dict)
    text: PageText
    video: PageVideo
    src: Optional[str]
    sort: int
    ownership: PageOwnership
    stats: PageStats = Field(alias="_stats")
    model_config = {"populate_by_name": True}


# -- Flags globaux
class MonksEnhancedJournalFlags(BaseModel):
    pagetype: str
    img: Optional[str]
    alias_id: str


class ScenePackerFlags(BaseModel):
    hash: str = Field(default="f8b4aae18af0e51bdda187c363c93918c1474c5b")
    sourceId: str
    packed: bool = Field(default=True)


class ExportSourceFlags(BaseModel):
    world: str
    system: str
    coreVersion: str
    systemVersion: str


class EntryFlags(BaseModel):
    monks_enhanced_journal: MonksEnhancedJournalFlags = Field(alias="monks-enhanced-journal")
    scene_packer: ScenePackerFlags = Field(alias="scene-packer")
    exportSource: ExportSourceFlags
    model_config = {
        "populate_by_name": True
    }


# -- Stats globaux
class EntryStats(BaseModel):
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str
    compendiumSource: str


# -- Entrée de journal entière pour une ville
class JournalEntryPlace(BaseModel):
    folder: str
    name: str
    flags: EntryFlags
    pages: List[Page]
    stats: EntryStats = Field(alias="_stats")
    id: str = Field(alias="_id")

    model_config = ConfigDict(populate_by_name=True)
