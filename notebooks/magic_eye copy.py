"""

Module to represent the Magic Eye transformation of given image.

"""


import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageDraw
#import random

#from io import BytesIO

#from .constants import BORDER_WIDTH, FIGURE_NAMES


class MagicEye:
    """Factory that creates figure instances and renders them into images."""

    def __init__(self, image, ancho_patron=90, object_3d=0.15, noise_frequency=0.5):
        self.image=image
        self.ancho_patron=ancho_patron
        self.object_3d=object_3d
        self.noise_frequency=noise_frequency


    def fusionar_estereoscopica_pil(self, img_izquierda:Image, img_derecha:Image) -> Image:
        """
        Recibe dos objetos PIL.Image, los transforma y devuelve un nuevo objeto PIL.Image en 3D.
        
        :param img_izquierda: Objeto PIL.Image (perspectiva del ojo izquierdo).
        :param img_derecha: Objeto PIL.Image (perspectiva del ojo derecho).
        :return: Un nuevo objeto PIL.Image transformado en anaglifo (Rojo/Cian).
        """
        # 1. Asegurar que ambas imágenes estén en modo RGB para poder extraer sus canales 
        # correctamente
            # 1. Forzar la conversión a objetos PIL.Image correctos y en modo RGB
            # Esto previene errores si los objetos de entrada no están bien inicializados
            #img_izq_rgb = img_izquierda.convert("RGB")
            #img_der_rgb = img_derecha.convert("RGB")
        img_izq_rgb = img_izquierda
        img_der_rgb = img_derecha

        # 2. Validar o forzar que tengan las mismas dimensiones para que coincidan los píxeles
        #if img_izq_rgb.size != img_der_rgb.size:
        #    img_der_rgb = img_der_rgb.resize(img_izq_rgb.size, Image.Resampling.LANCZOS)

        # 3. Separar cada imagen en sus canales individuales (Rojo, Verde, Azul)
        r_izq, _, _ = img_izq_rgb.split()
        _, g_der, b_der = img_der_rgb.split()

        # 4. Fusionar los canales para crear el efecto estereoscópico:
        # El ojo izquierdo (filtro rojo) verá el canal Rojo de la imagen izquierda.
        # El ojo derecho (filtro cian) verá los canales Verde y Azul de la imagen derecha.
        imagen_transformada = Image.merge("RGB", (r_izq, g_der, b_der))

        return imagen_transformada


#    def build_image2(self, figure_name: str, color: str,
#                       border_width: int = BORDER_WIDTH) -> bytes:
#
#        image = Image.new("RGB", (800, 600), color="white")
#        figure = self.create_figure(figure_name)
        #fill_color = _lighten_color(color)
        #remove: one parameter color
#        figure.draw(image,"black","black", border_width=border_width)
#        other_figure_name = figure_name
#        while other_figure_name == figure_name:
#            other_figure_name = random.choice(FIGURE_NAMES)

#        other_image = Image.new("RGB", (800, 600), color="white")
#        other_figure = self.create_figure(other_figure_name)
        #fill_color = _lighten_color(color)
        #remove: one parameter color 
#        other_figure.draw(other_image, color, color, border_width=border_width)

#        buffer = BytesIO()
#        self.fusionar_estereoscopica_pil(image, other_image).save(buffer, format="PNG")
#        return buffer.getvalue()


   # def crear_ojo_magico_pro(self,):
        # ancho_patron=90, object_3d=0.15, noise_frequency=0.5
        """ Ancho del patron, un valor alto implica q tienes q desenfocar 
        los ojo al extremo de 90 a 100 es facil.mas dificil es 140
        object_3d, nos dice cuanto sobresale el objeto de 0.06 a 0.08 es 
        mas facil, sera mas plano, no deforma tanto el patron. Dificil: 0.12
        noise_frequency, 0.4 es mas ruidos. menos de 0.1 a 0.2

        """

    def _create_texture(self, alto):
        """
        Genera una textura de ruido aleatorio de alta frecuencia píxel a píxel.
        Ignora noise_frequency=0.5 para la base del estereograma, ya que las 
        frecuencias bajas destruyen la unificación en bordes rectos.
        """
        E = self.ancho_patron  # 90
        # Creamos ruido RGB aleatorio puro de alta frecuencia
        ruido = np.random.randint(0, 256, (alto, E, 3), dtype=np.uint8)
        return ruido


    def crear_ojo_magico_pro(self, image_texture=None, depth_map=None):
        # Keep scene depth independent from the repeating texture used to reveal it.
        if depth_map is None:
            img_profundidad = self._prepare_image()
        else:
            img_profundidad = depth_map.convert("L")
            if img_profundidad.size != self.image.size:
                img_profundidad = img_profundidad.resize(
                    self.image.size,
                    Image.Resampling.BILINEAR,
                )
        ancho, alto = img_profundidad.size
        mapa = np.array(img_profundidad)

        ancho_p = self.ancho_patron  # 90 (Separación base de los ojos)
        # Factor de profundidad (típicamente entre 0.1 y 0.3 para no forzar la vista)
        factor_3d = getattr(self, 'object_3d', 0.25)

        # 2. Cargar textura base (Ruido aleatorio si no se provee una)
        if image_texture is None:
            textura_base = self._create_texture(alto)
        else:
            # Asegurar que la textura tenga el alto correcto y el ancho del patrón (E)
            textura_base = np.array(image_texture.convert("RGB").resize((ancho_p, alto)))

        # Inicializar lienzo final en RGB (3 canales para color)
        resultado = np.zeros((alto, ancho, 3), dtype=np.uint8)

        # 3. ALGORITMO DE ENLACES (Sir Thimbleby & Inglis)
        for y in range(alto):
            enlaces = np.arange(ancho)  # Cada píxel apunta a sí mismo inicialmente

            for x in range(ancho):
                # Normalizar z entre 0.0 y 1.0
                z = mapa[y, x] / 255.0

                # La separación disminuye si el objeto está más "cerca" (z alto).
                separacion = int(ancho_p * (1.0 - factor_3d * z))

                # Vinculamos dos píxeles simétricos alrededor del punto de profundidad.
                izq = x - separacion // 2
                der = izq + separacion

                if 0 <= izq < ancho and 0 <= der < ancho:
                    visible = True
                    for offset in range(1, separacion // 2):
                        if mapa[y, x - offset] > mapa[y, x] and mapa[y, x + offset] > mapa[y, x]:
                            visible = False
                            break
                    if not visible:
                        continue

                    # Buscar la raíz del conjunto izquierdo
                    raiz_izq = enlaces[izq]
                    while raiz_izq != enlaces[raiz_izq]:
                        raiz_izq = enlaces[raiz_izq]

                    # Buscar la raíz del conjunto derecho
                    raiz_der = enlaces[der]
                    while raiz_der != enlaces[raiz_der]:
                        raiz_der = enlaces[raiz_der]

                    # Unificar las raíces (la raíz izquierda mantiene el orden de la fila).
                    if raiz_izq != raiz_der:
                        if raiz_izq < raiz_der:
                            enlaces[raiz_der] = raiz_izq
                        else:
                            enlaces[raiz_izq] = raiz_der
                            
            # 4. Compresión de caminos de la fila (Aplanado de punteros)
            for x in range(ancho):
                raiz = x
                while raiz != enlaces[raiz]:
                    raiz = enlaces[raiz]
                enlaces[x] = raiz
                
            # 5. Pintar la fila usando la textura asignada a cada raíz
            for x in range(ancho):
                raiz = enlaces[x]
                # La textura se repite periódicamente en cada componente enlazado.
                resultado[y, x] = textura_base[y, raiz % ancho_p]
                    
        # 6. Guardar e imbuir puntos de guía para ayudar a enfocar la vista
        img_final = Image.fromarray(resultado, mode="RGB")
        dibujo = ImageDraw.Draw(img_final)
        centro_x = ancho // 2
        
        # Dibujamos dos pequeños círculos negros con borde blanco en la parte superior
        r = 4  # Radio de los puntos guía
        for despliegue in [-(ancho_p // 2), (ancho_p // 2)]:
            px = centro_x + despliegue
            dibujo.ellipse((px - r, 20 - r, px + r, 20 + r), fill=(0, 0, 0), outline=(255, 255, 255))
        
        # Nota: Asegúrate de tener definido self._generate_extension() en tu clase
        return img_final, self._generate_extension()

    def crear_ojo_magico_pro2(self, image_texture=None):
        # 1. Cargar mapa de profundidad y aplicar un suavizado ligero
        img_profundidad = self.image.convert("L").filter(ImageFilter.GaussianBlur(radius=2))
        ancho, alto = img_profundidad.size
        mapa = np.array(img_profundidad)
        
        E = self.ancho_patron  # 90
        
        # 2. Cargar tu textura de mosaicos o ruido (ambas funcionarán ahora)
        # [COMENTADO PARA MOSTRAR MAPA DE ENLACES]
        # if image_texture is None:
        #     textura_base = np.random.randint(0, 256, (alto, E, 3), dtype=np.uint8)
        # else:
        #     textura_base = np.array(image_texture.convert("RGB").resize((E, alto)))
            
        # Cambiado a canal único (escala de grises) para almacenar las raíces normalizadas
        resultado = np.zeros((alto, ancho), dtype=np.uint8)
        
        # 3. ALGORITMO UNIDIRECCIONAL CON CORRECCIÓN DE FASE DE MAPA
        for y in range(alto):
            enlaces = np.arange(ancho)
            
            for x in range(ancho):
                # CORRECCIÓN CRÍTICA:
                z = mapa[y, x] / 255.0
                separacion = int(E - (z * E * self.object_3d))
                
                izq = x - separacion // 2
                der = x + separacion // 2
                
                # Enlazamos los extremos de la separación calculada en el centro 'x'
                if 0 <= izq < ancho and 0 <= der < ancho:
                    raiz_izq = enlaces[izq]
                    while raiz_izq != enlaces[raiz_izq]:
                        raiz_izq = enlaces[raiz_izq]
                        
                    raiz_der = enlaces[der]
                    while raiz_der != enlaces[raiz_der]:
                        raiz_der = enlaces[raiz_der]
                        
                    if raiz_izq != raiz_der:
                        if raiz_izq < raiz_der:
                            enlaces[raiz_der] = raiz_izq
                        else:
                            enlaces[raiz_izq] = raiz_der
                            
            # 4. Compresión de caminos de la fila
            for x in range(ancho):
                raiz = x
                while raiz != enlaces[raiz]:
                    raiz = enlaces[raiz]
                enlaces[x] = raiz
                
            # 5. [MODIFICADO] Guardar el mapa de enlaces normalizado (0 a 255)
            # Escalamos el valor de la raíz final de cada píxel para que sea visible
            fila_normalizada = (enlaces / (ancho - 1) * 255).astype(np.uint8)
            resultado[y, :] = fila_normalizada

            # [COMENTADO EL PINTADO PROGRESIVO ORIGINAL]
            # fila_colores = np.zeros((ancho, 3), dtype=np.uint8)
            # for x in range(ancho):
            #     raiz = enlaces[x]
            #     if raiz == x:
            #         fila_colores[x] = textura_base[y, x % E]
            #     else:
            #         fila_colores[x] = fila_colores[raiz]
            # resultado[y, :] = fila_colores
                    
        # 6. Guardar e imbuir puntos de guía
        # Convertimos el resultado en imagen de escala de grises ("L")
        img_final = Image.fromarray(resultado, mode="L")
        dibujo = ImageDraw.Draw(img_final)
        centro_x = ancho // 2
        
        # Dibujamos las guías en blanco (255) para que contrasten con el fondo gris
        dibujo.ellipse((centro_x - (E // 2) - 6, 20, centro_x - (E // 2) + 6, 32), fill=255)
        dibujo.ellipse((centro_x + (E // 2) - 6, 20, centro_x + (E // 2) + 6, 32), fill=255)
        
        return img_final, self._generate_extension()


    def _prepare_image(self) -> Image:
        """ Prepare the image performing a blur to remove high contrast"""
        # 1. Convertir a escala de grises
        gris = self.image.convert("L")

        # 2. Invertir los colores para que el fondo sea NEGRO (0) y el cuadrado sea CLARO
        # (Si el fondo original era blanco puro, ahora será negro absoluto)
        mapa_invertido = ImageOps.invert(gris)

        # 3. Aplicar un desenfoque Gaussiano para suavizar las paredes del cuadrado
        # Esto crea una "rampa" de degradado en los bordes, eliminando las líneas fijas
        return mapa_invertido.filter(ImageFilter.GaussianBlur(radius=8))

    def _create_texture2(self, alto):
        """ Create a sample texture """
        base_texture =np.zeros((alto, self.ancho_patron, 3), dtype=np.uint8)
        for y in range(alto):
            for x in range(self.ancho_patron):
                val = int(128 + 
                    127 * np.sin(x * self.noise_frequency) * np.cos(y * self.noise_frequency))
                base_texture[y, x] = [val, (val + 50) % 255, (val * 2) % 255]
        return base_texture

    def _generate_extension(self):
        """Gererate extension with details used for generation"""
        return f"{self.ancho_patron}-{self.object_3d}-{self.noise_frequency}"
