from typing import Literal
from pydantic import BaseModel


class FoundryItem(BaseModel):
    name: str
    type: Literal["weapon", "equipment", "consumable", "armor", "treasure"]
    system: dict
    img: str = "icons/svg/item-bag.svg"


class FoundryActor(BaseModel):
    name: str
    type: Literal["npc"]
    system: dict
    items: list[FoundryItem]
    img: str
    prototypeToken: dict
    folder: str
    flags: dict = {}
    sort: int = 100000
    ownership: dict = {"default": 0}
    effects: list = []
    _id: str
    _stats: dict

