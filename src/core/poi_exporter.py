import time
from typing import Optional
from src.services.chatgpt_service import ChatGPT
from src.models.poi_foundry import JournalEntryPOI, Page, PageFlags, PageTitle, PageText, PageVideo, PageOwnership, PageStats, MonksEnhancedJournalPageFlags
from src.models.poi_foundry import MonksEnhancedJournalFlags, EntryFlags, ScenePackerFlags, ExportSourceFlags, EntryStats

def poi_create_journal_entry(name: str, location: str, text_content: str, user_id: str = "5e25BVKy2W9e3XQq") -> JournalEntryPOI:
    now = int(time.time() * 1000)
    entry_id = ChatGPT.generate_unique_id()

    return JournalEntryPOI(
        folder="tws3gVRVN96Qb7L8",
        name=name,
        flags=EntryFlags(
            monks_enhanced_journal=MonksEnhancedJournalFlags(
                pagetype="poi",
                img="modules/monks-enhanced-journal/assets/poi.png"
            ),
            scene_packer=ScenePackerFlags(
                hash="",
                sourceId=f"JournalEntry.{entry_id}"
            ),
            exportSource=ExportSourceFlags(
                world="la-couronne-des-immortels",
                system="pf2e",
                coreVersion="12.331",
                systemVersion="6.12.1"
            )
        ),
        pages=[
            Page(
                type="text",
                name=name,
                flags=PageFlags(
                    monks_enhanced_journal=MonksEnhancedJournalPageFlags(
                        type="poi",
                        _lasttab="notes",
                        location=location,
                        appendix=False,
                        scrollPos='{"tab.description .tab-inner":0}',
                        relationships=[],
                        extra_user_data={user_id: {"notes": "<p>Notes</p>"}}
                    )
                ),
                _id=entry_id,
                system={},
                title=PageTitle(show=True, level=1),
                image={},
                text=PageText(format=1, content=text_content),
                video=PageVideo(controls=True, volume=0.5),
                src=None,
                sort=0,
                ownership=PageOwnership({"default": -1, user_id: 3}),
                _stats=PageStats(
                    compendiumSource=None,
                    duplicateSource=None,
                    coreVersion="12.331",
                    systemId="pf2e",
                    systemVersion="6.12.1",
                    createdTime=now,
                    modifiedTime=now,
                    lastModifiedBy=user_id
                )
            )
        ],
        _stats=EntryStats(
            coreVersion="12.331",
            systemId="pf2e",
            systemVersion="6.12.1",
            createdTime=now,
            modifiedTime=now,
            lastModifiedBy=user_id
        )
    )
