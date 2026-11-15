"""

Constants file.

"""
from typing import Dict, Type
from .services.figures import (
    ArrowFigure,
    CircleFigure,
    CrescentFigure,
    CrossFigure,
    DiagonalFigure,
    DropletFigure,
    EllipseFigure,
    Figure,
    FlowerFigure,
    HeartFigure,
    HexagonFigure,
    PacmanFigure,
    PentagonFigure,
    RainbowFigure,
    RectangleFigure,
    SpiralFigure,
    SquareFigure,
    StarFigure,
    SunFigure,
    TextFigure,
    TriangleFigure,
)




FIGURE_NAMES = [
    "square",
    "circle",
    "rectangle",
    "ellipse",
    "triangle",
    "pentagon",
    "hexagon",
    "star",
    "sun",
    "flower",
    "crescent",
    "heart",
    "cross",
    "pacman",
    "droplet",
    "diagonal",
    "arrow",
    "spiral",
    "rainbow",
    "text",
]

SHAPE_COLORS = [
    "#2563eb",
    "#f59e0b",
    "#10b981",
    "#ec4899",
    "#8b5cf6",
    "#ef4444",
    "#14b8a6",
    "#38bdf8",
    "#f97316",
    "#a855f7",
]
BORDER_WIDTH = 10

FIGURE_MAPPINGS: Dict[str, Type[Figure]] = {
    "square": SquareFigure,
    "circle": CircleFigure,
    "rectangle": RectangleFigure,
    "ellipse": EllipseFigure,
    "triangle": TriangleFigure,
    "pentagon": PentagonFigure,
    "hexagon": HexagonFigure,
    "star": StarFigure,
    "sun": SunFigure,
    "flower": FlowerFigure,
    "crescent": CrescentFigure,
    "heart": HeartFigure,
    "cross": CrossFigure,
    "pacman": PacmanFigure,
    "droplet": DropletFigure,
    "diagonal": DiagonalFigure,
    "arrow": ArrowFigure,
    "spiral": SpiralFigure,
    "rainbow": RainbowFigure,
    "text": TextFigure,
    }
