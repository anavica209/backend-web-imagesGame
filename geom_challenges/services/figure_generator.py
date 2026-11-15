"""

Module to generate figures

"""
import random
from io import BytesIO
from PIL import Image
from .magic_eye import MagicEye
from ..constants import FIGURE_NAMES, BORDER_WIDTH, FIGURE_MAPPINGS
from .figures import Figure


def _lighten_color(color_hex: str, amount: float = 0.8) -> str:
    color_hex = color_hex.lstrip("#")
    rgb = tuple(int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
    light_rgb = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
    return "#{:02x}{:02x}{:02x}".format(*light_rgb)


class FiguresGenerator:
    """Factory that creates figure instances and renders them into images."""

    def create_figure(self, name: str) -> Figure:
        """" Create one of the figures from the FIGURE_MAPPINGS """
        figure_type = FIGURE_MAPPINGS.get(name.lower())
        if figure_type is None:
            raise ValueError(f"Unsupported figure: {name}")
        return figure_type(name=name.lower())

    def create_random_figure(self) -> Figure:
        """" Create a random figure """
        return self.create_figure(random.choice(FIGURE_NAMES))

    def build_image(self, figure_name: str, color: str, border_width: int = BORDER_WIDTH) -> tuple[bytes, str]:
        """ Build image """

        image = Image.new("RGB", (800, 600), color="white")
        figure = self.create_figure(figure_name)
        #fill_color = _lighten_color(color)
        #remove: one parameter color 
        figure.draw(image, color=color, fill_color=color, border_width=border_width)
        figure.apply_3d_shading(image)

        magic_eye = MagicEye(image,)
        image, extension=magic_eye.crear_ojo_magico_pro()
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue() , extension
