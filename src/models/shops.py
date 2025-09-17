from typing import Optional, List, Dict, Union
from typing import BaseModel, Field


class ShopRelationship(BaseModel):
    id: str
    uuid: str
    hidden: bool
    relationship: str
    name: str
    img: str
    type: str


class ShopFlags(BaseModel):
    type: str
    _lasttab: Optional[str]
    items: List[dict]  # Peut être modifié selon le format attendu
    scrollPos: Optional[str]
    shoptype: Optional[str]
    location: Optional[str]
    state: Optional[str]
    autoopen: Optional[bool]
    purchasing: Optional[str]
    selling: Optional[str]
    appendix: Optional[bool]
    relationships: List[ShopRelationship]
    twentyfour: Optional[bool]
    opening: Optional[int]
    closing: Optional[int]
    __root__: Optional[Dict[str, Dict[str, str]]] = Field(default=None, alias="5e25BVKy2W9e3XQq")


class PageTitle(BaseModel):
    show: bool
    level: int


class PageText(BaseModel):
    format: int
    content: str


class PageVideo(BaseModel):
    controls: bool
    volume: float


class PageOwnership(BaseModel):
    default: int
    __root__: Optional[Dict[str, int]] = Field(default=None, alias="5e25BVKy2W9e3XQq")


class PageStats(BaseModel):
    compendiumSource: Optional[str]
    duplicateSource: Optional[str]
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str


class PageFlags(BaseModel):
    monks_enhanced_journal: ShopFlags = Field(..., alias="monks-enhanced-journal")


class ShopPage(BaseModel):
    type: str
    name: str
    flags: PageFlags
    _id: str
    system: dict
    title: PageTitle
    image: dict
    text: PageText
    video: PageVideo
    src: Optional[str]
    sort: int
    ownership: PageOwnership
    _stats: PageStats


class ExportSource(BaseModel):
    world: str
    system: str
    coreVersion: str
    systemVersion: str


class TopFlags(BaseModel):
    monks_enhanced_journal: Dict[str, Union[str, None]] = Field(..., alias="monks-enhanced-journal")
    scene_packer: Dict[str, str] = Field(..., alias="scene-packer")
    exportSource: ExportSource


class TopStats(BaseModel):
    coreVersion: str
    systemId: str
    systemVersion: str
    createdTime: int
    modifiedTime: int
    lastModifiedBy: str


class ShopJournalEntry(BaseModel):
    folder: str
    name: str
    flags: TopFlags
    pages: List[ShopPage]
    _stats: TopStats
