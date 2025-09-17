from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field, RootModel


class Relationship(BaseModel):
    type: str
    uuid: str
    id: str
    relationship: str
    hidden: bool


class MonksEnhancedJournalPageFlags(BaseModel):
    type: str
    _lasttab: Optional[str]
    location: Optional[str]
    appendix: Optional[bool]
    scrollPos: Optional[str]
    relationships: Optional[List[Relationship]]
    extra_user_data: Optional[Dict[str, Dict[str, str]]] = Field(default_factory=dict)

    model_config = {
        "populate_by_name": True
    }


class PageFlags(BaseModel):
    monks_enhanced_journal: Optional[MonksEnhancedJournalPageFlags] = Field(alias="monks-enhanced-journal")

    model_config = {
        "populate_by_name": True
    }


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
    system: Dict[str, Union[str, int, float, bool]]
    title: PageTitle
    image: Dict = Field(default_factory=dict)
    text: PageText
    video: PageVideo
    src: Optional[str]
    sort: int
    ownership: PageOwnership
    _stats: PageStats


class MonksEnhancedJournalFlags(BaseModel):
    pagetype: str
    img: Optional[str]


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

    model_config = {
        "populate_by_name": True
    }


class EntryStats(BaseModel):
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str


class JournalEntryPOI(BaseModel):
    folder: str
    name: str
    flags: EntryFlags
    pages: List[Page]
    _stats: EntryStats
    _id = str
