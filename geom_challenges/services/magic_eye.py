"""
Module to represent the Ishihara-style camouflage transformation of a given image.
"""

import random
import numpy as np
from PIL import Image, ImageDraw


class MagicEye:
    """Factory that creates figure instances and renders them into Ishihara-style images."""

    def __init__(self, image, ancho_patron=90, object_3d=0.15, noise_frequency=0.5):
        self.image = image
        self.ancho_patron = ancho_patron
        self.object_3d = object_3d
        self.noise_frequency = noise_frequency

    def _generate_extension(self):
        """Generate extension with details used for generation."""
        return f"{self.ancho_patron}-{self.object_3d}-{self.noise_frequency}"

    def _get_figure_mask(self, gray_img: Image.Image) -> np.ndarray:
        """
        Detect which pixels belong to the figure and which belong to the background,
        using the top-left corner (0, 0) as the background reference color.
        """
        arr = np.array(gray_img, dtype=np.float32)
        bg_color = arr[0, 0]
        mask = np.abs(arr - bg_color) > 30
        return mask

    def crear_ojo_magico_pro(self, image_texture=None, depth_map=None):
        """
        Generate an image with Ishihara color-blindness test style dot camouflage
        and return the tuple (final_img, self._generate_extension()).
        """
        base_img = depth_map if depth_map is not None else self.image
        gray_img = base_img.convert("L")
        width, height = gray_img.size

        figure_mask = self._get_figure_mask(gray_img)

        palettes = [
            {
                "figure": [(235, 94, 40), (242, 132, 68), (217, 78, 52), (247, 160, 114)],
                "background": [(116, 168, 146), (144, 190, 109), (87, 138, 117), (163, 196, 138)],
            },
            {
                "figure": [(88, 164, 176), (59, 130, 145), (123, 190, 201), (72, 149, 163)],
                "background": [(217, 155, 102), (199, 130, 80), (230, 179, 133), (184, 115, 68)],
            },
        ]
        current_palette = random.choice(palettes)

        final_img = Image.new("RGB", (width, height), (245, 245, 240))
        draw = ImageDraw.Draw(final_img)

        circles = []
        scale = min(width, height) / 400.0
        possible_radii = [
            max(2, int(14 * scale)),
            max(2, int(10 * scale)),
            max(2, int(7 * scale)),
            max(1, int(4 * scale)),
        ]

        max_attempts = 4500
        circle_spacing = 1.5

        for radius in possible_radii:
            for _ in range(max_attempts):
                cx = random.randint(radius, width - radius - 1)
                cy = random.randint(radius, height - radius - 1)

                collision = False
                for ox, oy, oradius in circles:
                    dist_sq = (cx - ox) ** 2 + (cy - oy) ** 2
                    min_dist_sq = (radius + oradius + circle_spacing) ** 2
                    if dist_sq < min_dist_sq:
                        collision = True
                        break

                if not collision:
                    circles.append((cx, cy, radius))
                    if figure_mask[cy, cx]:
                        color = random.choice(current_palette["figure"])
                    else:
                        color = random.choice(current_palette["background"])

                    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
                    draw.ellipse(bbox, fill=color)

        return final_img, self._generate_extension()
