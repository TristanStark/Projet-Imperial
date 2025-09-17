from datetime import datetime
from typing import List
from uuid import uuid4
from src.models.shops import ShopFlags, ShopJournalEntry, ShopRelationship, TopFlags,PageFlags, ShopPage, ExportSource, PageStats, TopStats

def create_shop_journal_entry(
    name: str,
    shop_id: str,
    description: str,
    shoptype: str,
    location: str,
    relationships: List[ShopRelationship],
) -> ShopJournalEntry:
    current_time_ms = int(datetime.utcnow().timestamp() * 1000)
    user_id = "5e25BVKy2W9e3XQq"  # Peut être généré dynamiquement si besoin

    return ShopJournalEntry(
        folder="5bAu9tDmc7gxjagF",  # Dossier fictif, à adapter selon contexte
        name=name,
        flags=TopFlags(
            monks_enhanced_journal={
                "pagetype": "shop",
                "img": "modules/monks-enhanced-journal/assets/shop.png"
            },
            scene_packer={
                "hash": "dummyhashvalue",
                "sourceId": f"JournalEntry.{shop_id}"
            },
            exportSource=ExportSource(
                world="la-couronne-des-immortels",
                system="pf2e",
                coreVersion="12.331",
                systemVersion="6.12.1"
            )
        ),
        pages=[
            ShopPage(
                type="text",
                name=name,
                flags=PageFlags(
                    monks_enhanced_journal=ShopFlags(
                        type="shop",
                        _lasttab="items",
                        items=[],
                        scrollPos='{"tab.description .tab-inner":0}',
                        shoptype=shoptype,
                        location=location,
                        state="open",
                        autoopen=False,
                        purchasing="locked",
                        selling="locked",
                        appendix=False,
                        relationships=relationships,
                        twentyfour=True,
                        opening=480,
                        closing=900,
                        __root__={
                            user_id: {
                                "notes": "<p>Notes</p>"
                            }
                        }
                    )
                ),
                _id=shop_id,
                system={},
                title={"show": True, "level": 1},
                image={},
                text={"format": 1, "content": f"<p>{description}</p>"},
                video={"controls": True, "volume": 0.5},
                src=None,
                sort=0,
                ownership={"default": 2, user_id: 3},
                _stats=PageStats(
                    compendiumSource=None,
                    duplicateSource=None,
                    coreVersion="12.331",
                    systemId="pf2e",
                    systemVersion="6.12.1",
                    createdTime=current_time_ms,
                    modifiedTime=current_time_ms + 1000,
                    lastModifiedBy=user_id
                )
            )
        ],
        _stats=TopStats(
            coreVersion="12.331",
            systemId="pf2e",
            systemVersion="6.12.1",
            createdTime=current_time_ms,
            modifiedTime=current_time_ms,
            lastModifiedBy=user_id
        )
    )
