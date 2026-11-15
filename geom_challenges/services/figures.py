"""

Module to create Figures. 

"""


import math
from abc import ABC, abstractmethod
from typing import ClassVar

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFilter import GaussianBlur
from PIL.Image import Image as PILImage


class Figure(ABC):
    """Base contract for every geometry figure."""

    shape_name: ClassVar[str] = ""

    def __init__(self, name: str | None = None) -> None:
        """Initialize a figure with an optional display name."""
        self._name = name or self.shape_name

    @property
    def name(self) -> str:
        """Return the figure's name."""
        return self._name

    def _scaled_border_width(self, image: PILImage, border_width: int) -> int:
        """Return a border width scaled to the canvas size."""
        scale = min(image.width / 800.0, image.height / 600.0)
        return max(1, int(border_width * scale))

    def _scale_point(self, image: PILImage, x: float, y: float) -> tuple[int, int]:
        """Map a point from the base 800x600 canvas to the current image size."""
        return (
            int(x * image.width / 800.0),
            int(y * image.height / 600.0),
        )

    def _scale_rect(self, image: PILImage, left: float, top: float, right: float, bottom: float) -> tuple[int, int, int, int]:
        """Map a rectangle from the base 800x600 canvas to the current image size."""
        return (
            int(left * image.width / 800.0),
            int(top * image.height / 600.0),
            int(right * image.width / 800.0),
            int(bottom * image.height / 600.0),
        )

    def _scale_points(self, image: PILImage, points: list[tuple[float, float]]) -> list[tuple[int, int]]:
        """Map a list of points from the base canvas to the current image size."""
        return [self._scale_point(image, x, y) for x, y in points]

    def apply_3d_shading(self, image: PILImage) -> None:
        """Add directional lighting, a visible side face, and a cast shadow."""
        pixels = np.array(image.convert("RGB"))
        mask = np.any(pixels < 250, axis=2)
        if not np.any(mask):
            return

        silhouette = Image.fromarray(mask.astype(np.uint8) * 255, "L")
        width, height = image.size
        offset_x = max(10, int(width * 0.025))
        offset_y = max(12, int(height * 0.035))

        shadow_mask = Image.new("L", image.size, 0)
        shadow_mask.paste(silhouette, (offset_x, offset_y))
        shadow_mask = shadow_mask.filter(GaussianBlur(max(6, int(min(image.size) * 0.02))))
        shadow_mask = shadow_mask.point(lambda value: int(value * 0.48))
        shaded_image = Image.new("RGB", image.size, "white")
        shadow_color = Image.new("RGB", image.size, (30, 36, 48))
        shaded_image.paste(shadow_color, mask=shadow_mask)

        shifted_silhouette = Image.new("L", image.size, 0)
        shifted_silhouette.paste(silhouette, (offset_x, offset_y))
        side_mask = (np.asarray(shifted_silhouette) > 0) & ~mask
        shifted_image = Image.new("RGB", image.size, "white")
        shifted_image.paste(image, (offset_x, offset_y))
        shifted_pixels = np.asarray(shifted_image, dtype=np.float32)
        canvas_pixels = np.array(shaded_image)
        side_pixels = np.clip(shifted_pixels * 0.48, 0, 255).astype(np.uint8)
        canvas_pixels[side_mask] = side_pixels[side_mask]

        rows, columns = np.where(mask)
        center_x = (columns.min() + columns.max()) / 2
        center_y = (rows.min() + rows.max()) / 2
        radius_x = max((columns.max() - columns.min()) / 2, 1)
        radius_y = max((rows.max() - rows.min()) / 2, 1)
        normalized_x = ((np.arange(width) - center_x) / radius_x)[None, :]
        normalized_y = ((np.arange(height) - center_y) / radius_y)[:, None]
        surface = np.exp(-1.8 * (normalized_x**2 + normalized_y**2))

        normal_x = 3.6 * normalized_x * surface
        normal_y = 3.6 * normalized_y * surface
        normal_z = np.ones_like(surface)
        normal_length = np.sqrt(normal_x**2 + normal_y**2 + normal_z**2)
        normal_x /= normal_length
        normal_y /= normal_length
        normal_z /= normal_length

        light = np.array([-0.48, -0.62, 0.62], dtype=np.float32)
        light /= np.linalg.norm(light)
        diffuse = np.clip(normal_x * light[0] + normal_y * light[1] + normal_z * light[2], 0, 1)
        half_vector = light + np.array([0, 0, 1], dtype=np.float32)
        half_vector /= np.linalg.norm(half_vector)
        specular = np.clip(
            normal_x * half_vector[0] + normal_y * half_vector[1] + normal_z * half_vector[2],
            0,
            1,
        ) ** 18

        bevel_radius = max(3, int(min(image.size) * 0.01))
        soft_silhouette = np.asarray(silhouette.filter(GaussianBlur(bevel_radius)), dtype=np.float32) / 255
        gradient_y, gradient_x = np.gradient(soft_silhouette)
        edge_light = np.clip((gradient_x + gradient_y) * bevel_radius, -1, 1)
        brightness = np.clip(0.44 + 0.52 * diffuse + 0.3 * specular + 0.12 * edge_light, 0.32, 1.22)
        face_pixels = np.clip(pixels.astype(np.float32) * brightness[:, :, None], 0, 255).astype(np.uint8)
        canvas_pixels[mask] = face_pixels[mask]
        image.paste(Image.fromarray(canvas_pixels, "RGB"))

    @abstractmethod
    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw the figure onto the provided image."""


class SquareFigure(Figure):
    """Represents a square figure."""

    shape_name = "square"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a square on the given image."""
        draw = ImageDraw.Draw(image)
        draw.rectangle(self._scale_rect(image, 200, 100, 600, 500), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class CircleFigure(Figure):
    """Represents a circle figure."""

    shape_name = "circle"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a circle on the given image."""
        draw = ImageDraw.Draw(image)
        draw.ellipse(self._scale_rect(image, 200, 100, 600, 500), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class RectangleFigure(Figure):
    """Represents a rectangle figure."""

    shape_name = "rectangle"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a rectangle on the given image."""
        draw = ImageDraw.Draw(image)
        draw.rectangle(self._scale_rect(image, 180, 160, 620, 440), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class EllipseFigure(Figure):
    """Represents an ellipse figure."""

    shape_name = "ellipse"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw an ellipse on the given image."""
        draw = ImageDraw.Draw(image)
        draw.ellipse(self._scale_rect(image, 180, 140, 620, 460), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class TriangleFigure(Figure):
    """Represents a triangle figure."""

    shape_name = "triangle"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a triangle on the given image."""
        draw = ImageDraw.Draw(image)
        points = self._scale_points(image, [(200, 500), (400, 120), (600, 500)])
        draw.polygon(points, fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class PentagonFigure(Figure):
    """Represents a pentagon figure."""

    shape_name = "pentagon"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a pentagon on the given image."""
        draw = ImageDraw.Draw(image)
        points = []
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            x = 400 + 210 * math.cos(angle)
            y = 300 + 210 * math.sin(angle)
            points.append((x, y))
        draw.polygon(self._scale_points(image, points), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class HexagonFigure(Figure):
    """Represents a hexagon figure."""

    shape_name = "hexagon"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a hexagon on the given image."""
        draw = ImageDraw.Draw(image)
        points = []
        for i in range(6):
            angle = i * (2 * math.pi / 6)
            x = 400 + 210 * math.cos(angle)
            y = 300 + 210 * math.sin(angle)
            points.append((x, y))
        draw.polygon(self._scale_points(image, points), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class StarFigure(Figure):
    """Represents a star figure."""

    shape_name = "star"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a star on the given image."""
        draw = ImageDraw.Draw(image)
        points = []
        for i in range(10):
            angle = i * (math.pi / 5) - math.pi / 2
            radius = 220 if i % 2 == 0 else 95
            x = 400 + radius * math.cos(angle)
            y = 300 + radius * math.sin(angle)
            points.append((x, y))
        draw.polygon(self._scale_points(image, points), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class SunFigure(Figure):
    """Represents a sun figure."""

    shape_name = "sun"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a sun on the given image."""
        draw = ImageDraw.Draw(image)
        for i in range(12):
            angle = i * (2 * math.pi / 12)
            x1 = 400 + 130 * math.cos(angle)
            y1 = 300 + 130 * math.sin(angle)
            x2 = 400 + 240 * math.cos(angle)
            y2 = 300 + 240 * math.sin(angle)
            draw.line([self._scale_point(image, x1, y1), self._scale_point(image, x2, y2)], fill=color, width=self._scaled_border_width(image, border_width))
        draw.ellipse(self._scale_rect(image, 270, 170, 530, 430), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class FlowerFigure(Figure):
    """Represents a flower figure."""

    shape_name = "flower"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a flower on the given image."""
        draw = ImageDraw.Draw(image)
        for i in range(6):
            angle = math.radians(i * 60)
            petal = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw_petal = ImageDraw.Draw(petal)
            petal_bounds = self._scale_rect(image, 320, 100, 480, 380)
            draw_petal.ellipse(petal_bounds, fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))
            rotated = petal.rotate(math.degrees(angle), center=self._scale_point(image, 400, 300))
            image.paste(rotated, (0, 0), rotated)
        draw.ellipse(self._scale_rect(image, 320, 220, 480, 380), fill="white", outline=color, width=self._scaled_border_width(image, border_width))


class CrescentFigure(Figure):
    """Represents a crescent figure."""

    shape_name = "crescent"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a crescent on the given image."""
        draw = ImageDraw.Draw(image)
        draw.ellipse(self._scale_rect(image, 220, 120, 580, 420), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))
        draw.ellipse(self._scale_rect(image, 310, 120, 640, 420), fill="white", outline="white", width=0)


class HeartFigure(Figure):
    """Represents a heart figure."""

    shape_name = "heart"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a heart on the given image."""
        draw = ImageDraw.Draw(image)
        points = []
        for t in range(0, 360, 2):
            rad = math.radians(t)
            x = 400 + 16.5 * (16 * math.sin(rad) ** 3)
            y = 300 - 16.5 * (13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad))
            points.append((x, y))
        draw.polygon(self._scale_points(image, points), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class CrossFigure(Figure):
    """Represents a cross figure."""

    shape_name = "cross"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a cross on the given image."""
        draw = ImageDraw.Draw(image)
        points = [
            (340, 60), (460, 60), (460, 200), (620, 200),
            (620, 320), (460, 320), (460, 540), (340, 540),
            (340, 320), (180, 320), (180, 200), (340, 200),
        ]
        draw.polygon(self._scale_points(image, points), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class PacmanFigure(Figure):
    """Represents a pacman-style figure."""

    shape_name = "pacman"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a pacman-like shape on the given image."""
        draw = ImageDraw.Draw(image)
        draw.pieslice(self._scale_rect(image, 200, 100, 600, 500), start=35, end=325, fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class DropletFigure(Figure):
    """Represents a droplet figure."""

    shape_name = "droplet"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a droplet on the given image."""
        draw = ImageDraw.Draw(image)
        draw.chord(self._scale_rect(image, 270, 240, 530, 500), start=0, end=180, fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))
        draw.polygon(self._scale_points(image, [(270, 370), (400, 100), (530, 370)]), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class DiagonalFigure(Figure):
    """Represents a diagonal line figure."""

    shape_name = "diagonal"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a diagonal line on the given image."""
        draw = ImageDraw.Draw(image)
        draw.line((self._scale_point(image, 100, 75), self._scale_point(image, 700, 525)), fill=color, width=self._scaled_border_width(image, border_width))


class ArrowFigure(Figure):
    """Represents an arrow figure."""

    shape_name = "arrow"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw an arrow on the given image."""
        draw = ImageDraw.Draw(image)
        draw.line([self._scale_point(image, 120, 300), self._scale_point(image, 500, 300)], fill=color, width=self._scaled_border_width(image, border_width))
        draw.polygon(self._scale_points(image, [(480, 180), (680, 300), (480, 420)]), fill=fill_color, outline=color, width=self._scaled_border_width(image, border_width))


class SpiralFigure(Figure):
    """Represents a spiral figure."""

    shape_name = "spiral"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a spiral on the given image."""
        draw = ImageDraw.Draw(image)
        spiral_points = []
        for i in range(320):
            angle = i * 0.15
            radius = i * 0.72
            x = 400 + radius * math.cos(angle)
            y = 300 + radius * math.sin(angle)
            spiral_points.append((x, y))
        draw.line(self._scale_points(image, spiral_points), fill=color, width=self._scaled_border_width(image, border_width))


class RainbowFigure(Figure):
    """Represents a rainbow figure."""

    shape_name = "rainbow"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a rainbow-like shape on the given image."""
        draw = ImageDraw.Draw(image)
        for i in range(6):
            offset = i * 28
            draw.pieslice(
                self._scale_rect(image, 150 + offset, 130 + offset, 650 - offset, 610 - offset),
                start=180,
                end=360,
                fill=fill_color,
                outline="white",
                width=self._scaled_border_width(image, border_width),
            )


class TextFigure(Figure):
    """Represents a text figure."""

    shape_name = "text"

    def draw(self, image: PILImage, color: str, fill_color: str, border_width: int = 10) -> None:
        """Draw a text-based figure on the given image."""
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 220)
        except OSError:
            font = ImageFont.load_default()
        scaled_font_size = max(12, int(220 * min(image.width / 800.0, image.height / 600.0)))
        try:
            font = ImageFont.truetype("arial.ttf", scaled_font_size)
        except OSError:
            font = ImageFont.load_default()
        draw.text(self._scale_point(image, 250, 160), "B4", fill=color, font=font, stroke_width=self._scaled_border_width(image, 10), stroke_fill=color)
