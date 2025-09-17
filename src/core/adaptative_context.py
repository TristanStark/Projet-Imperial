import json
from pathlib import Path
from typing import List, Type, TypeVar, Dict, Any, Optional
from pydantic import BaseModel
from src.models.quest_model import QuestModel, LocationBrief
from collections import defaultdict


class Place(BaseModel):
    name: str
    type: str  # ex: "forêt", "lac", "canal", "colline", "ruines"
    description: Optional[str]
    region: Optional[str]
    danger_level: int  # 0 à 100
    access_difficulty: str  # "facile", "modéré", "difficile", "impossible"
    magical_presence: int # 0 à 100
    creatures: List[str] # créatures typiques ou dominantes
    resources: List[str]  # ressources naturelles : herbes, minerais, bois, eau pure…
    landmarks: List[str]  # points d'intérêt (temple, obélisque, caverne)
    special_effects: List[str]  # ex : "illusion permanente", "corruption lente", "temps ralenti"
    tags: List[str]  # "sacré", "hanté", "interdit", "site ancien", etc.

    def __repr__(self):
        return f"<Place '{self.name}' ({self.type}) danger={self.danger_level}>"

    def summary(self, ctx=None) -> str:
        quest_lines = []
        if ctx:
            quests = ctx.find_quests_by_city_or_place(self.name)
            if quests:
                quest_lines = ["📜 Quêtes liées :"] + [f"- {q.titre} (par {q.giver.nom})" for q in quests]

        return "\n".join([
            f"🌍 {self.name} — {self.type.capitalize()} ({self.region or 'région inconnue'})",
            f"Difficulté d'accès : {self.access_difficulty} | Danger : {self.danger_level}/100 | Magie : {self.magical_presence}/100",
            f"Créatures : {', '.join(self.creatures) if self.creatures else 'aucune'}",
            f"Ressources : {', '.join(self.resources) if self.resources else 'aucune'}",
            f"Points d'intérêt : {', '.join(self.landmarks) if self.landmarks else 'aucun'}",
            f"Effets spéciaux : {', '.join(self.special_effects) if self.special_effects else 'aucun'}",
            f"Tags : {', '.join(self.tags) if self.tags else 'aucun'}",
            "",
            f"{self.description or 'Aucune description disponible.'}",
            *quest_lines
        ])

# Définition des modèles de base
class Faction(BaseModel):
    name: str
    description: str
    influence_level: int
    type: str

    def __repr__(self):
        return f"<Faction name='{self.name}' ({self.type}), description={self.description}, influence={self.influence_level}>"

    def summary(self) -> str:
        return f"{self.name} ({self.type}) — Influence : {self.influence_level}/100\n  {self.description}"

class Resource(BaseModel):
    name: str
    quantity: str
    is_critical: bool

    def __repr__(self):
        return f"<Resource name='{self.name}', quantity='{self.quantity}', critical={self.is_critical}>"
    
    def summary(self) -> str:
        crit = " (CRITIQUE)" if self.is_critical else ""
        return f"{self.name} : {self.quantity}{crit}"


class Landmark(BaseModel):
    name: str
    type: str
    description: str

    def __repr__(self):
        return f"<Landmark name='{self.name}', type='{self.type}'>"

    def summary(self) -> str:
        return f"{self.name} ({self.type}) : {self.description}"

class PopulationInfo(BaseModel):
    estimated: int
    density: str
    main_species: List[str]
    minority_species: List[str]
    average_age: float

    def __repr__(self):
        return f"<Population {self.estimated} hab, density='{self.density}', species={self.main_species}>"

    def summary(self) -> str:
        minorities = f", minorités : {', '.join(self.minority_species)}" if self.minority_species else ""
        return f"{self.estimated} habitants, densité {self.density}, espèce(s) dominante(s) : {', '.join(self.main_species)}{minorities}"

class Government(BaseModel):
    type: str
    ruler: str
    stability: int

    def __repr__(self):
        return f"<Government type='{self.type}', ruler='{self.ruler}', stability={self.stability}>"

    def summary(self) -> str:
        return f"Gouvernement : {self.type} dirigé par {self.ruler} — Stabilité : {self.stability}/100"

class City(BaseModel):
    name: str
    region: str
    description: str
    population: PopulationInfo
    government: Government
    factions: List[Faction]
    economy: List[Resource]
    landmarks: List[Landmark]
    military_strength: int
    magical_presence: int
    technological_level: int
    external_threats: List[str]
    internal_problems: List[str]
    importance: str
    climate: str
    access_routes: List[str]
    special_rules: List[str]
    tags: List[str]  # "sacré", "hanté", "interdit", "site ancien", etc.

    def __repr__(self):
        return f"""<City '{self.name}' ({self.importance}) in {self.region}, pop={self.population.estimated}.
        government={self.government}, factions={len(self.factions)} ({[f.name for f in self.factions]}), economy={len(self.economy)} ({[f for f in self.economy]}),
        landmarks={len(self.landmarks)} ({[l for l in self.landmarks]}), au climat {self.climate}.>"""

    def summary(self, ctx=None) -> str:
        lines = [
            f"🏙️ {self.name} ({self.importance}) — {self.region}",
            f"Climat : {self.climate} | Accès : {', '.join(self.access_routes) if self.access_routes else 'aucun'}",
            self.population.summary(),
            self.government.summary(),
            f"Puissance militaire : {self.military_strength} | Présence magique : {self.magical_presence} | Technologie : {self.technological_level}",
            "",
            "Factions : " + (", ".join(f.name for f in self.factions) if self.factions else "aucune"),
            "Ressources : " + (", ".join(r.name for r in self.economy) if self.economy else "aucune"),
            "Lieux notables : " + (", ".join(l.name for l in self.landmarks) if self.landmarks else "aucun"),
            "",
            "Problèmes internes : " + (", ".join(self.internal_problems) if self.internal_problems else "aucun"),
            "Menaces externes : " + (", ".join(self.external_threats) if self.external_threats else "aucune"),
            "",
            f"Règles spéciales : {', '.join(self.special_rules) if self.special_rules else 'aucune'}"
        ]

        if ctx:
            quests = ctx.find_quests_by_city_or_place(self.name)
            if quests:
                lines.append("")
                lines.append("📜 Quêtes liées :")
                lines.extend(f"- {q.titre} (par {q.giver.nom})" for q in quests)

        return "\n".join(lines)

# Alias de type générique
T = TypeVar('T', bound=BaseModel)

class _ContextManager:
    def __init__(self, context_dir: str = "./data/adaptative_context"):
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(exist_ok=True)
        self.data: Dict[str, List[BaseModel]] = {
            "cities": [],
            "factions": [],
            "resources": [],
            "places": [],
            "quests": []
        }
        self.load_all()

    def _get_path(self, key: str) -> Path:
        return self.context_dir / f"{key}.json"

    def _save(self, key: str):
        path = self._get_path(key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([item.model_dump() for item in self.data[key]], f, ensure_ascii=False, indent=2)

    def _load(self, key: str, model_cls: Type[T]) -> List[T]:
        path = self._get_path(key)
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [model_cls(**item) for item in json.load(f)]

    def load_all(self):
        self.data["cities"] = self._load("cities", City)
        self.data["factions"] = self._load("factions", Faction)
        self.data["resources"] = self._load("resources", Resource)
        self.data["places"] = self._load("places", Place)
        self.data["quests"] = self._load("quests", QuestModel)

    def save_all(self):
        for key in self.data:
            self._save(key)

    def add_city(self, city: City):
        self.data["cities"].append(city)
        self._save("cities")
        # Ressources
        for res in city.economy:
            if not any(existing.name == res.name for existing in self.data["resources"]):
                self.data["resources"].append(res)
                print(f"[+] Ressource auto-ajoutée : {res.name}")
        self._save("resources")

        # Factions
        for fac in city.factions:
            if not any(existing.name == fac.name for existing in self.data["factions"]):
                self.data["factions"].append(fac)
                print(f"[+] Faction auto-ajoutée : {fac.name}")
        self._save("factions")

    def add_faction(self, faction: Faction):
        self.data["factions"].append(faction)
        self._save("factions")

    def add_resource(self, resource: Resource):
        self.data["resources"].append(resource)
        self._save("resources")

    def add_place(self, place: Place):
        self.data["places"].append(place)
        self._save("places")

    def get_all(self, key: str) -> List[BaseModel]:
        return self.data.get(key, [])

    def add_quest(self, quest: QuestModel):
        self.data["quests"].append(quest)
        self._save("quests")

    def find_quests_by_city_or_place(self, name: str) -> List[QuestModel]:
        return [
            quest for quest in self.data["quests"]
            if any(loc.nom == name for loc in quest.lieux)
        ]

    def find_quests_by_giver(self, pnj_name: str) -> List[QuestModel]:
        return [q for q in self.data["quests"] if q.giver.nom == pnj_name]

    def find_quests_by_tag(self, tag: str) -> List[QuestModel]:
        return [q for q in self.data["quests"] if tag in q.tags]

    def find_city(self, name: str) -> City | None:
        return next((c for c in self.data["cities"] if c.name == name), None)
    
    def search_places(self,
                    type: Optional[str] = None,
                    min_danger: Optional[int] = None,
                    has_tag: Optional[str] = None) -> List[Place]:
        results = self.data["places"]
        if type:
            results = [p for p in results if p.type == type]
        if min_danger is not None:
            results = [p for p in results if p.danger_level >= min_danger]
        if has_tag:
            results = [p for p in results if has_tag in p.tags]
        return results

    # 🔍 Rechercher les villes selon un critère
    def search_cities(self,
                      region: str = None,
                      min_population: int = None,
                      max_population: int = None,
                      species: str = None,
                      min_stability: int = None,
                      faction_name: str = None) -> List[City]:
        results = self.data["cities"]
        if region:
            results = [c for c in results if c.region == region]
        if min_population:
            results = [c for c in results if c.population.estimated >= min_population]
        if max_population:
            results = [c for c in results if c.population.estimated <= max_population]
        if species:
            results = [c for c in results if species in c.population.main_species + c.population.minority_species]
        if min_stability:
            results = [c for c in results if c.government.stability >= min_stability]
        if faction_name:
            results = [c for c in results if any(f.name == faction_name for f in c.factions)]
        return results

    def collect_and_register_factions(self, quest: QuestModel) -> List[str]:
        factions = set()

        # Giver
        if quest.giver.faction:
            factions.add(quest.giver.faction)

        # PNJ
        for pnj in quest.pnjs:
            if pnj.faction:
                factions.add(pnj.faction)

        # Ennemis humanoïdes uniquement
        for loc in quest.lieux:
            for ennemi in loc.ennemis:
                if ennemi.faction and ennemi.type in ("humain", "humanoïde"):
                    factions.add(ennemi.faction)

        # Déjà listées manuellement
        for f in quest.factions_associees:
            factions.add(f)

        # Sauvegarde dans le contexte si nouveau
        for faction_name in factions:
            if not any(f.name == faction_name for f in self.data["factions"]):
                print(f"[+] Faction auto-créée : {faction_name}")
                self.data["factions"].append(Faction(
                    name=faction_name,
                    description="A_COMPLETER",
                    influence_level=10,
                    type="non spécifié"
                ))
        self._save("factions")

        return sorted(factions)

    def add_quest_with_locations(self, quest: QuestModel):

        # Génère les lieux si absents
        for loc in quest.lieux:
            name = loc.nom
            print(f"[+] Lieu : {name} ({loc.type})")
            # Vérifie si la localisation est déjà enregistrée
            place_exists = any(p.name == name for p in self.data["places"])
            city_exists = any(c.name == name for c in self.data["cities"])

            if place_exists or city_exists:
                print(f"[!] {name} Lieu déjà enregistré, pas de création automatique.")
                continue

            if loc.type in ["ville", "village"]:
                city = City(
                    name=name,
                    region="A_COMPLETER",
                    description=loc.description,
                    population=PopulationInfo(
                        estimated=0,
                        main_species=["Humains"],
                        density="moyenne",
                        minority_species=[],
                        average_age=35.0
                    ),
                    government=Government(type="inconnu", ruler="inconnu", stability=0),
                    importance="ville" if loc.type == "ville" else "village",
                    factions=[],
                    economy=[],
                    climate="A_COMPLETER",
                    access_routes=[],
                    external_threats=[],
                    internal_problems=[],
                    military_strength=0,
                    magical_presence=0,
                    technological_level=0,
                    landmarks=[],
                    special_rules=[],
                    tags=["auto-généré", "TO_FAIRE"],
                )
                self.data["cities"].append(city)
                self._save("cities")

            else:
                place = Place(
                    name=name,
                    type=loc.type,
                    description=loc.description,
                    region="A_COMPLETER",
                    danger_level=int(loc.danger) if loc.danger and loc.danger.isdigit() else 0,
                    access_difficulty=getattr(loc, "access_difficulty", "facile"),
                    magical_presence=0,
                    creatures=[e.nom for e in loc.ennemis],
                    resources=[],
                    landmarks=[],
                    special_effects=[],
                    tags=["auto-généré", "TO_FAIRE"]
                )
                self.data["places"].append(place)
                self._save("places")

        # 🔄 Factions liées à la quête
        quest.factions_associees = self.collect_and_register_factions(quest)

        # 🧩 Ajouter ces factions dans les villes ou lieux associés
        for loc in quest.lieux:
            location_name = loc.nom
            # Cherche si c’est une ville
            for city in self.data["cities"]:
                if city.name == location_name:
                    for faction_name in quest.factions_associees:
                        if not any(f.name == faction_name for f in city.factions):
                            faction = next((f for f in self.data["factions"] if f.name == faction_name), None)
                            if faction:
                                city.factions.append(faction)
                                print(f"[+] Faction '{faction_name}' ajoutée à la ville '{city.name}'")
                    self._save("cities")
                    break

            # Cherche si c’est un lieu
            for place in self.data["places"]:
                if place.name == location_name:
                    # Tu peux décider si les lieux doivent aussi référencer des factions
                    # Par défaut, on ne fait rien ici (Places n'ont pas de champ faction pour l’instant)
                    break
        self.data["quests"].append(quest)
        self._save("quests")
        self.fix_missing_locations_from_steps()

    # 📊 Vérifier l'influence réelle d'une faction sur toutes les villes
    def faction_influence(self, faction_name: str) -> Dict[str, int]:
        influence_map = {}
        for city in self.data["cities"]:
            for faction in city.factions:
                if faction.name == faction_name:
                    influence_map[city.name] = faction.influence_level
        return influence_map

    def get_elements_with_tag_to_faire(self) -> dict:
        """
        Retourne toutes les villes et lieux marqués avec 'TO_FAIRE' dans leurs tags ou règles spéciales.
        """
        cities = [city for city in self.data["cities"] if "TO_FAIRE" in city.tags]
        places = [place for place in self.data["places"] if "TO_FAIRE" in place.tags]

        return {
            "cities": cities,
            "places": places
        }

    def fix_missing_locations_from_steps(self):
        updated = False
        for quest in self.data["quests"]:
            known_lieux = {loc.nom for loc in quest.lieux}
            missing = set()

            for step in quest.etapes:
                if step.lieu and step.lieu not in known_lieux:
                    missing.add(step.lieu)

            for missing_name in missing:
                print(f"[!] Lieu '{missing_name}' mentionné dans les étapes mais absent de quest.lieux. Ajout automatique.")
                quest.lieux.append(LocationBrief(
                    nom=missing_name,
                    type="inconnu",
                    description="A_COMPLETER",
                    ambiance=None,
                    danger=None,
                    pnj_associes=[],
                    illustration_prompt=None,
                    ennemis=[],
                    musique_theme=None
                ))
                updated = True

        if updated:
            self._save("quests")
            print("[INFO] Tous les lieux manquants dans les étapes ont été ajoutés dans quests.lieux")
        else:
            print("[INFO] Aucun lieu manquant détecté dans les étapes.")


    def synchronize_missing_factions_from_quests(self):
        existing_factions = {f.name for f in self.data["factions"]}
        discovered_factions = set()

        for quest in self.data["quests"]:
            # Giver
            if quest.giver.faction:
                discovered_factions.add(quest.giver.faction)

            # PNJ
            for p in quest.pnjs:
                if p.faction:
                    discovered_factions.add(p.faction)

            # Ennemis humanoïdes
            for loc in quest.lieux:
                for ennemi in loc.ennemis:
                    if ennemi.faction and ennemi.type in ("humain", "humanoïde"):
                        discovered_factions.add(ennemi.faction)

            # Factions listées dans factions_associees
            for f in quest.factions_associees:
                discovered_factions.add(f)

        # Compare
        missing = discovered_factions - existing_factions
        for name in sorted(missing):
            print(f"[+] Faction ajoutée : {name}")
            self.data["factions"].append(Faction(
                name=name,
                description="A_COMPLETER",
                influence_level=10,
                type="non spécifié"
            ))

        if missing:
            self._save("factions")
        else:
            print("Aucune faction manquante détectée.")

    def get_incomplete_factions(self) -> list:
        """
        Retourne toutes les factions qui ne sont pas finies (= A_COMPLETER dans la description).
        """
        return [faction for faction in self.data["factions"] if "A_COMPLETER" in faction.description]


    def get_factions(self) -> List[Faction]:
        """
        Retourne toutes les factions.
        """
        return self.data["factions"]

    # ⚖️ Vérifier les incohérences : factions référencées dans les villes mais pas globalement
    def detect_faction_inconsistencies(self) -> List[str]:
        declared_factions = {f.name for f in self.data["factions"]}
        referenced_factions = {
            f.name for city in self.data["cities"] for f in city.factions
        }
        missing = referenced_factions - declared_factions
        return list(missing)

    def context_summary(self) -> str:
        lines = []

        # === VILLES / VILLAGES ===
        cities = sorted(self.data["cities"], key=lambda c: c.population.estimated, reverse=True)
        lines.append("LISTE DES VILLES / VILLAGES (ordonné par nombre d'habitants décroissants):")
        for city in cities:
            factions = [f.name for f in city.factions]
            economy = [r.name for r in city.economy]
            landmarks = [l.name for l in city.landmarks]
            quests = self.find_quests_by_city_or_place(city.name)
            lines.append(f"- {city.name} ({city.importance}) — {city.description or 'Aucune description'}, "
                        f"{city.population.estimated} habitants.")
            lines.append(f"  Factions : {', '.join(factions) if factions else 'Aucune'}")
            lines.append(f"  Menaces extérieures : {', '.join(city.external_threats) if city.external_threats else 'Aucune'}")
            lines.append(f"  Problèmes internes : {', '.join(city.internal_problems) if city.internal_problems else 'Aucun'}")
            lines.append(f"  Économie : {', '.join(economy) if economy else 'Aucune'}")
            lines.append(f"  Monuments : {', '.join(landmarks) if landmarks else 'Aucun'}")
            lines.append(f"  Routes d'accès : {', '.join(city.access_routes) if city.access_routes else 'Aucune'}")
            lines.append(f"  Quêtes liées : {', '.join([q.titre for q in quests]) if quests else 'Aucune'}")
            lines.append("")

        # === LIEUX AUTRES ===
        lines.append("LISTE DES LIEUX AUTRES:")
        for place in self.data["places"]:
            lines.append(f"- {place.name}, {place.type}, {place.description or 'Aucune description'}, "
                        f"difficulté d'accès : {place.access_difficulty}, "
                        f"ressources : {', '.join(place.resources) if place.resources else 'aucune'}, "
                        f"créatures : {', '.join(place.creatures) if place.creatures else 'aucune'}")
        lines.append("")

        # === FACTIONS ===
        city_by_faction = defaultdict(list)
        for city in self.data["cities"]:
            for faction in city.factions:
                city_by_faction[faction.name].append(city.name)

        lines.append("LISTE DES FACTIONS:")
        for faction in self.data["factions"]:
            cities_here = city_by_faction[faction.name]
            lines.append(f"- {faction.name}, {faction.description or 'Aucune description'}, type : {faction.type}, "
                        f"présente dans : {', '.join(cities_here) if cities_here else 'aucune'}")
        lines.append("")

        # === QUÊTES ===
        lines.append("LISTE DES QUÊTES DEJA EXISTANTES:")
        for quest in self.data["quests"]:
            locations = [l.nom for l in quest.lieux]
            lines.append(f"- {quest.titre}, {quest.synopsis[:100] + '...' if len(quest.synopsis) > 100 else quest.synopsis}, "
                        f"donneur : {quest.giver.nom}, lieux : {', '.join(locations)}")
        lines.append("")

        return "\n".join(lines)

    def modify_element(self, category: str, updated_object: BaseModel):
        """
        Remplace un élément existant (identifié par son nom) dans la catégorie par un nouvel objet.

        :param category: 'cities', 'places', ou 'factions'
        :param updated_object: un objet BaseModel complet (City, Place ou Faction)
        """
        assert category in {"cities", "places", "factions"}, "Catégorie non reconnue"

        updated = False
        for idx, element in enumerate(self.data[category]):
            if element.name == updated_object.name:
                self.data[category][idx] = updated_object
                updated = True
                print(f"[✓] {category[:-1].capitalize()} '{updated_object.name}' modifié avec succès.")
                break

        if updated:
            self._save(category)
        else:
            print(f"[✗] Aucun(e) {category[:-1]} nommé(e) '{updated_object.name}' trouvé(e).")

ContextManager = _ContextManager()