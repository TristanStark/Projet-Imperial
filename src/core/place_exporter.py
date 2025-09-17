import time
from src.services.chatgpt_service import ChatGPT
import json
from typing import List
from pathlib import Path

from src.models.place_foundry import (
    JournalEntryPlace,
    EntryFlags,
    MonksEnhancedJournalFlags,
    ScenePackerFlags,
    ExportSourceFlags,
    Page,
    PageFlags,
    MonksEnhancedJournalPlaceFlags,
    PlaceAttributes,
    PageTitle,
    PageText,
    PageVideo,
    PageOwnership,
    PageStats,
    EntryStats,
    Relationship
)


def load_and_inject_relationships_place(
    json_path: Path,
    relationships: List[Relationship]
) -> None:
    """
    Charge un fichier JSON en JournalEntryFaction, ajoute les relationships, et retourne l'objet Pydantic.
    
    :param json_path: chemin du fichier JSON à charger
    :param relationships: liste d'objets Relationship à injecter
    :return: JournalEntryFaction mis à jour
    """
    print(f"  [!] [PLACE] Injection de la relation {relationships[0].name} ({relationships[0].type}) pour PLACE {json_path} ")

    with open(json_path, encoding="utf-8") as f:
        raw_data = json.load(f)

    # Injecter les relationships dans le bon sous-niveau
    if (
        "flags" in raw_data
        and "monks-enhanced-journal" in raw_data["flags"]
    ):
        existing = raw_data["pages"][0]["flags"]["monks-enhanced-journal"].get("relationships", [])
        existing_ids = {(r.get("id"), r.get("uuid")) for r in existing}
        new = [r.model_dump() for r in relationships if (r.id, r.uuid) not in existing_ids]
        raw_data["pages"][0]["flags"]["monks-enhanced-journal"]["relationships"] = existing + new
    else:
        raise ValueError("Structure du JSON invalide : 'flags.monks-enhanced-journal' manquant.")

    # Transformer en objet Pydantic
    jep = JournalEntryPlace.model_validate(raw_data)
    jep.flags.scene_packer.hash = ChatGPT.generate_entry_hash(jep.model_dump_json(by_alias=True))

    with open(json_path, "w", encoding="utf-8") as out:
        out.write(jep.model_dump_json(indent=2, by_alias=True))


def create_journal_entry_place(
    name: str,
    description: str,
    size: str,
    government: str,
    inhabitants: int,
    image_path: str,
    MEGADescription: str,
    location: str = "À définir",
    user_id: str = "5e25BVKy2W9e3XQq"
) -> JournalEntryPlace:
    now = int(time.time() * 1000)
    entry_id = ChatGPT.generate_unique_id()
    page_id = ChatGPT.generate_unique_id()

    jep =  JournalEntryPlace(
        folder="nk5j08cBb4PTrwAy",
        name=name,
        flags=EntryFlags(
            monks_enhanced_journal=MonksEnhancedJournalFlags(
                pagetype="place",
                img=image_path,
                alias_id=entry_id
            ),
            scene_packer=ScenePackerFlags(
                hash="f8b4aae18af0e51bdda187c363c93918c1474c5b",
                sourceId=f"JournalEntry.{entry_id}"
            ),
            exportSource=ExportSourceFlags(
                world="la-couronne-des-immortels",
                system="pf2e",
                coreVersion="12.331",
                systemVersion="6.12.2"
            )
        ),
        pages=[
            Page(
                type="text",
                name=name,
                flags=PageFlags(
                    monks_enhanced_journal=MonksEnhancedJournalPlaceFlags(
                        type="place",
                        _lasttab="relationships",
                        scrollPos='{"tab.entry-details .tab-inner":0,".tab.townsfolk .tab-inner":0,".tab.shops .tab-inner":0,".tab.description .tab-inner":0}',
                        placetype="Ville",
                        location=location,
                        appendix=False,
                        attributes=PlaceAttributes(
                            age="Inconnue",
                            size=size,
                            government=government,
                            inhabitants=str(inhabitants)
                        ),
                        relationships=[],
                        extra_user_data={user_id: {"notes": f"<p>{MEGADescription}</p>"}},
                        img=image_path,
                        pagetype="place"
                    )
                ),
                id=page_id,
                system={},
                title=PageTitle(show=True, level=1),
                image={},
                text=PageText(format=1, content=description),
                video=PageVideo(controls=True, volume=0.5),
                src=None,
                sort=0,
                ownership=PageOwnership({"default": -1, user_id: 3}),
                stats=PageStats(
                    compendiumSource=f"JournalEntry.{page_id}",
                    duplicateSource=None,
                    coreVersion="12.331",
                    systemId="pf2e",
                    systemVersion="6.12.2",
                    createdTime=now,
                    modifiedTime=now,
                    lastModifiedBy=user_id
                )
            )
        ],
        stats=EntryStats(
            coreVersion="12.331",
            systemId="pf2e",
            systemVersion="6.12.2",
            createdTime=now,
            modifiedTime=now,
            lastModifiedBy=user_id,
            compendiumSource=f"JournalEntry.{entry_id}"
        ),
        id=entry_id
    )
    jep.flags.scene_packer.hash = ChatGPT.generate_entry_hash(jep.model_dump_json(by_alias=True))
    return jep
