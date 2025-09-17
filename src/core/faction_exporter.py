from src.models.factions_foundry import JournalEntryFaction, JournalPage, PageTitle, PageText, PageVideo, PageOwnership, PageStats, JournalStats, Relationship
import time
from src.services.chatgpt_service import ChatGPT
import json
from pathlib import Path
from typing import List

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

    print(f"  [!] [FACTION] Injection de la relation {relationships[0].name} ({relationships[0].role}) pour FACTION {json_path} ")

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
    jep = JournalEntryFaction.model_validate(raw_data)
    jep.flags["scene-packer"]["hash"] = ChatGPT.generate_entry_hash(jep.model_dump_json(by_alias=True))

    with open(json_path, "w", encoding="utf-8") as out:
        out.write(jep.model_dump_json(indent=2, by_alias=True))


def create_journal_entry_faction(nom: str, description: str) -> JournalEntryFaction:
    timestamp = int(time.time() * 1000)
    user_id = "5e25BVKy2W9e3XQq"
    unique_id = ChatGPT.generate_unique_id()
    page_id = ChatGPT.generate_unique_id()

    jef =  JournalEntryFaction(
        folder="NvMMetMEPF7fWM0g",
        name=nom,
        flags={
            "monks-enhanced-journal": {
                "pagetype": "organization",
                "img": "modules/monks-enhanced-journal/assets/organization.png",
                "alias_id": unique_id,
            },
            "scene-packer": {
                "hash": "",  # peut être rempli plus tard
                "sourceId": f"JournalEntry.{unique_id}",
                "packed": "true"
            },
            "exportSource": {
                "world": "la-couronne-des-immortels",
                "system": "pf2e",
                "coreVersion": "12.331",
                "systemVersion": "6.12.2"
            }
        },
        pages=[
            JournalPage(
                type="text",
                name=nom,
                flags={
                    "monks-enhanced-journal": {
                        "type": "organization",
                        "_lasttab": "notes",
                        "scrollPos": "{\".tab.description .tab-inner\":0}",
                        "alignment": "",
                        "location": "",
                        "appendix": False,
                        "relationships": [],
                        user_id: {
                            "notes": "<p>Note</p>"
                        }
                    }
                },
                id=page_id,
                system={},
                title=PageTitle(show=True, level=1),
                image={},
                text=PageText(format=1, content=f"<p>{description}</p>"),
                video=PageVideo(controls=True, volume=0.5),
                src=None,
                sort=0,
                ownership = PageOwnership({"default": -1, "5e25BVKy2W9e3XQq": 3}),
                stats=PageStats(
                    compendiumSource=f"JournalEntry.{page_id}",
                    duplicateSource=None,
                    coreVersion="12.331",
                    systemId="pf2e",
                    systemVersion="6.12.2",
                    createdTime=timestamp,
                    modifiedTime=timestamp,
                    lastModifiedBy=user_id
                )
            )
        ],
        stats=JournalStats(
            coreVersion="12.331",
            systemId="pf2e",
            systemVersion="6.12.2",
            createdTime=timestamp,
            modifiedTime=timestamp,
            lastModifiedBy=user_id,
            compendiumSource=f"JournalEntry.{unique_id}",
        ),
        id = unique_id
    )
    jef.flags["scene-packer"]["hash"] = ChatGPT.generate_entry_hash(jef.model_dump_json(by_alias=True))
    return jef
