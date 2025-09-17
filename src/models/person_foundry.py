from pydantic import BaseModel, Field, RootModel, ConfigDict, model_validator
from typing import Optional, Dict, List, Any


# -- Relationship générique
class Relationship(BaseModel):
    id: str
    uuid: str
    hidden: bool
    name: Optional[str]
    img: Optional[str]
    type: Optional[str]
    role: Optional[str]
    alias_id: str


# -- Attributs visibles sur la fiche
class SheetAttributeShown(BaseModel):
    shown: bool


class SheetSettings(BaseModel):
    attributes: Dict[str, SheetAttributeShown]


# -- Attributs textuels du personnage
class PersonAttributes(BaseModel):
    race: Optional[str] = None
    ancestry: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    profession: Optional[str] = None
    faction: Optional[str] = None
    traits: Optional[str] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None


# -- Flags de la page type "person"
class MonksEnhancedJournalPersonFlags(BaseModel):
    type: str
    _lasttab: Optional[str]
    scrollPos: Optional[str]
    sheet_settings: Optional[SheetSettings] = Field(alias="sheet-settings")
    role: Optional[str]
    location: Optional[str]
    appendix: Optional[bool]
    attributes: Optional[PersonAttributes]
    relationships: Optional[List[Relationship]]

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="before")
    @classmethod
    def migrate_extra_user_data(cls, data: Any) -> Any:
        if isinstance(data, dict) and "extra_user_data" in data:
            extra = data.pop("extra_user_data")
            if isinstance(extra, dict):
                data.update(extra)
        return data


# -- Flags de page
class PageFlags(BaseModel):
    monks_enhanced_journal: MonksEnhancedJournalPersonFlags = Field(alias="monks-enhanced-journal")

    model_config = ConfigDict(populate_by_name=True)


# -- Composants de page
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
    _id: str
    system: Dict[str, Any]
    title: PageTitle
    image: Dict[str, Any]
    text: PageText
    video: PageVideo
    src: Optional[str]
    sort: int
    ownership: PageOwnership
    _stats: PageStats


# -- Entrée globale
class MonksEnhancedJournalFlags(BaseModel):
    pagetype: str
    img: Optional[str]
    alias_id: str

class ScenePackerFlags(BaseModel):
    hash: str
    sourceId: str


class ExportSourceFlags(BaseModel):
    world: str
    system: str
    coreVersion: str
    systemVersion: str


class EntryFlags(BaseModel):
    monks_enhanced_journal: MonksEnhancedJournalFlags = Field(alias="monks-enhanced-journal")
    scene_packer: ScenePackerFlags = Field(alias="scene-packer")
    exportSource: ExportSourceFlags

    model_config = ConfigDict(populate_by_name=True)


class EntryStats(BaseModel):
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str


class JournalEntryPersonn(BaseModel):
    folder: str
    name: str
    flags: EntryFlags
    pages: List[Page]
    _stats: EntryStats
