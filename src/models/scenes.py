from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Définition partielle du modèle nécessaire
class Darkness(BaseModel):
    min: float = 0
    max: float = 1

class GlobalLight(BaseModel):
    enabled: bool = False
    alpha: float = 0.5
    bright: bool = False
    color: Optional[str] = None
    coloration: int = 1
    luminosity: float = 0
    saturation: float = 0
    contrast: float = 0
    shadows: float = 0
    darkness: Darkness = Darkness()

class EnvironmentSection(BaseModel):
    hue: float = 0
    intensity: float = 0
    luminosity: float = 0
    saturation: float = 0
    shadows: float = 0

class Environment(BaseModel):
    darknessLevel: float = 0
    darknessLock: bool = False
    globalLight: GlobalLight = GlobalLight()
    cycle: bool = True
    base: EnvironmentSection = EnvironmentSection()
    dark: EnvironmentSection = EnvironmentSection(hue=0.7139, luminosity=-0.25)

class FogColors(BaseModel):
    explored: Optional[str] = None
    unexplored: Optional[str] = None

class Fog(BaseModel):
    exploration: bool = True
    overlay: Optional[str] = None
    colors: FogColors = FogColors()

class Grid(BaseModel):
    type: int = 0
    size: int = 150
    style: str = "solidLines"
    thickness: int = 1
    color: str = "#000000"
    alpha: float = 0
    distance: float = 5
    units: str = "ft"

class Initial(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    scale: float = 0.5

class Background(BaseModel):
    src: str
    anchorX: float = 0
    anchorY: float = 0
    offsetX: float = 0
    offsetY: float = 0
    fit: str = "fill"
    scaleX: float = 1
    scaleY: float = 1
    rotation: float = 0
    tint: str = "#ffffff"
    alphaThreshold: float = 0

class SceneModel(BaseModel):
    folder: Optional[str] = None
    name: str
    navigation: bool = True
    navOrder: int = 100000
    navName: str
    background: Background
    foreground: Optional[str] = None
    foregroundElevation: int = 20
    thumb: Optional[str] = None
    width: int
    height: int
    padding: float = 0.25
    initial: Initial = Initial()
    backgroundColor: str = "#000000"
    grid: Grid = Grid()
    tokenVision: bool = True
    fog: Fog = Fog()
    environment: Environment = Environment()
    playlist: Optional[str] = None
    playlistSound: Optional[str] = None
    journal: Optional[str] = None
    journalEntryPage: Optional[str] = None
    weather: str = ""
    flags: Dict[str, Any] = {}
    _stats: Dict[str, Any] = {}
