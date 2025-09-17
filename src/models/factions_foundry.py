from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pydantic import RootModel


class Relationship(BaseModel):
    type: str
    uuid: str
    id: str
    name: str
    img: str
    role: str
    relationship: str
    hidden: bool
    alias_id: str


class MonksEnhancedJournalFlags(BaseModel):
    type: str
    _lasttab: Optional[str]
    scrollPos: Optional[str]
    alignment: Optional[str]
    location: Optional[str]
    appendix: Optional[bool]
    relationships: List[Relationship]
    notes_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        extra = "allow"  # Pour permettre d'autres champs comme "5e25BVKy2W9e3XQq"


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


class JournalPage(BaseModel):
    type: str
    name: str
    flags: Dict[str, Any]
    id: str = Field(alias="_id")
    system: Dict[str, Any]
    title: PageTitle
    image: Dict[str, Any]
    text: PageText
    video: PageVideo
    src: Optional[str]
    sort: int
    ownership: PageOwnership
    stats: PageStats = Field(alias="_stats")

    model_config = {"populate_by_name": True}


class JournalStats(BaseModel):
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str
    compendiumSource: str


class JournalEntryFaction(BaseModel):
    folder: str
    name: str
    flags: Dict[str, Any]
    pages: List[JournalPage]
    stats: JournalStats = Field(alias="_stats")
    id: str = Field(alias="_id")

    model_config = {
        "populate_by_name": True
    }

        