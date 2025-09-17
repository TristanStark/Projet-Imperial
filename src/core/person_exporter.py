import time
from src.services.chatgpt_service import ChatGPT

from src.models.person_foundry import (
    JournalEntryPersonn,
    EntryFlags,
    MonksEnhancedJournalFlags,
    ScenePackerFlags,
    ExportSourceFlags,
    Page,
    PageFlags,
    MonksEnhancedJournalPersonFlags,
    PageTitle,
    PageText,
    PageVideo,
    PageOwnership,
    PageStats,
    EntryStats,
    SheetSettings,
    SheetAttributeShown,
    PersonAttributes,
    Relationship
)
from pathlib import Path
from typing import List
import json

def load_and_inject_relationships(
    json_path: Path,
    relationships: List[Relationship]
) -> None:
    """
    Charge un fichier JSON en JournalEntryFaction, ajoute les relationships, et retourne l'objet Pydantic.
    
    :param json_path: chemin du fichier JSON à charger
    :param relationships: liste d'objets Relationship à injecter
    :return: JournalEntryFaction mis à jour
    """

    print(f"  [!] [PERSONNE] Injection de la relation {relationships[0].name} ({relationships[0].role}) pour FACTION {json_path} ")

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
    jep = JournalEntryPersonn.model_validate(raw_data)

    with open(json_path, "w", encoding="utf-8") as out:
        out.write(jep.model_dump_json(indent=2, by_alias=True))

def create_journal_entry_personn(
    name: str,
    role: str,
    location: str,
    description: str,
    race: str = "Humain",
    age: str = "Inconnu",
    profession: str = "Citoyen",
    user_id: str = "5e25BVKy2W9e3XQq"
) -> JournalEntryPersonn:
    now = int(time.time() * 1000)
    entry_id = ChatGPT.generate_unique_id()

    return JournalEntryPersonn(
        folder="PBVit1KlADrQniDo",
        name=name,
        flags=EntryFlags(
            monks_enhanced_journal=MonksEnhancedJournalFlags(
                pagetype="person",
                img="modules/monks-enhanced-journal/assets/person.png",
                alias_id=entry_id
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
                    monks_enhanced_journal=MonksEnhancedJournalPersonFlags(
                        type="person",
                        _lasttab="notes",
                        sheet_settings=SheetSettings(attributes={
                            "race": SheetAttributeShown(shown=True),
                            "gender": SheetAttributeShown(shown=True),
                            "profession": SheetAttributeShown(shown=True),
                            "faction": SheetAttributeShown(shown=True),
                            "eyes": SheetAttributeShown(shown=False),
                            "hair": SheetAttributeShown(shown=False),
                            "voice": SheetAttributeShown(shown=False),
                        }),
                        scrollPos='{"tab.entry-details .tab-inner":0,".tab.description .tab-inner":0,".relationships .items-list":0}',
                        role=role,
                        location=location,
                        appendix=False,
                        attributes=PersonAttributes(
                            race=race,
                            age=age,
                            profession=profession,
                            ancestry="Aucune",
                            gender="Inconnu",
                            faction="Aucune affiliation déclarée",
                            traits="Discret, observateur",
                            ideals="Préserver l'équilibre du monde",
                            bonds="Fidèle à ses racines",
                            flaws="Tendance à se méfier de tout"
                        ),
                        relationships=[],
                        **{user_id: {"notes": "<p>Notes</p>"}}
                    )
                ),
                _id=entry_id,
                system={},
                title=PageTitle(show=True, level=1),
                image={},
                text=PageText(format=1, content=description),
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
