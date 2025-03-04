import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from skimage import io as skio, exposure, restoration, transform, color

# Configuración de la página en modo ancho
st.set_page_config(page_title="Aplicación Quita Marca de Agua", layout="wide")

# Constantes configurables
DEFAULT_WATERMARK_REMOVAL_METHODS = ["color_filter", "inpainting"]
DEFAULT_COLOR_RANGES = {
    "black_text": {"lower": [0, 0, 0], "upper": [130, 130, 130]},
    "light_watermark": {"lower": [180, 180, 180], "upper": [255, 255, 255]},
    "colored_watermark": {"lower": [0, 0, 0], "upper": [255, 255, 255]},
    "red_watermark": {"lower": [0, 0, 150], "upper": [100, 100, 255]},  # Rojo en formato BGR
    "gray_watermark": {"lower": [100, 100, 100], "upper": [200, 200, 200]}  # Marcas de agua grises
}


def detect_watermark_area(image, threshold=0.8):
    """
    Detecta área potencial de marca de agua usando análisis de gradiente
    """
    # Convertir a escala de grises si no lo está
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Aplicar filtro de detección de bordes
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx ** 2 + sobely ** 2)

    # Normalizar y umbralizar para detectar áreas con menos detalle
    max_val = gradient_magnitude.max()
    if max_val > 0:
        normalized = gradient_magnitude / max_val
    else:
        normalized = np.zeros_like(gradient_magnitude)

    mask = normalized < threshold

    # Operaciones morfológicas para limpiar la máscara
    kernel = np.ones((5, 5), np.uint8)
    mask = mask.astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask

def detect_red_watermark(image):
    """
    Detecta si la imagen contiene una marca de agua roja
    """
    # Convertir a HSV para mejor detección de color
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Rango para rojo (HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    # Crear máscaras para ambos rangos de rojo
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2  # Combinar las máscaras

    # Contar píxeles rojos
    red_pixel_count = cv2.countNonZero(mask)

    # Si hay suficientes píxeles rojos, considerar que hay una marca de agua roja
    threshold = image.shape[0] * image.shape[1] * 0.001  # 0.1% de la imagen
    return red_pixel_count > threshold

def detect_text_watermark(image):
    """
    Detecta marcas de agua de texto basándose en patrones repetitivos
    """
    # Convertir a escala de grises si no lo está
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Aplicar umbralización adaptativa para resaltar el texto
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Buscar componentes conectados (letras, palabras)
    connectivity = 4  # 4 u 8
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)

    # Filtrar componentes por tamaño
    min_size = 50  # Ajustar según el tamaño esperado de las letras
    mask = np.zeros(gray.shape, dtype=np.uint8)

    # Analizar cada componente
    for i in range(1, num_labels):  # Empezar desde 1 para saltar el fondo
        if stats[i, cv2.CC_STAT_AREA] < min_size:
            # Los componentes pequeños podrían ser parte de una marca de agua
            mask[labels == i] = 255

    # Operaciones morfológicas para limpiar la máscara
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask

def is_bw_illustration(image, threshold=0.9):
    """
    Detecta si la imagen es una ilustración en blanco y negro
    """
    # Convertir a escala de grises si no lo está
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Calcular histograma
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # Normalizar histograma
    hist = hist / hist.sum()

    # Calcular proporción de píxeles cercanos a blanco y negro
    black_pixels = hist[:30].sum()  # Primeros 30 niveles (cercanos a negro)
    white_pixels = hist[225:].sum()  # Últimos 30 niveles (cercanos a blanco)

    # Si la mayoría de píxeles son muy blancos o muy negros, probablemente es B&N
    return (black_pixels + white_pixels) > threshold


def enhance_bw_illustration(image):
    """
    Mejora y limpia ilustraciones en blanco y negro
    """
    # Convertir a escala de grises si no lo está
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Aumentar contraste con CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Binarizar para limpiar ruido y realzar líneas
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convertir de nuevo a 3 canales si la entrada era RGB
    if len(image.shape) == 3:
        enhanced_color = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        return enhanced_color
    else:
        return binary

def color_filter_removal(image, color_range_name="light_watermark"):
    """
    Elimina marca de agua basada en filtrado de color
    """
    # Parámetros específicos para "PREVIEW" en rojo
    if color_range_name == "red_watermark":
        # Hacer una copia de la imagen original
        result = image.copy()

        # Detectar específicamente el rojo
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Rango para rojo (HSV)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        # Crear máscaras para ambos rangos de rojo
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2  # Combinar las máscaras

        # Ampliar ligeramente la máscara
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)

        # Usar inpainting para rellenar las zonas de la marca de agua
        result = cv2.inpaint(result, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

        return result

    # Para imágenes en blanco y negro, mejor preservar los detalles finos
    if is_bw_illustration(image):
        # Usar un enfoque diferente para ilustraciones en B&N
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Crear máscara para áreas que podrían ser marcas de agua
        mask = detect_text_watermark(image)

        # Usar inpainting con un radio menor para preservar líneas finas
        result = cv2.inpaint(image, mask, inpaintRadius=2, flags=cv2.INPAINT_NS)

        # Mejorar la imagen resultante específicamente para ilustraciones B&N
        if is_bw_illustration(result, threshold=0.8):
            result = enhance_bw_illustration(result)

        return result

    # Código original para otros tipos de marcas de agua
    color_range = DEFAULT_COLOR_RANGES.get(color_range_name, DEFAULT_COLOR_RANGES["light_watermark"])

    # Crear máscara para los colores dentro del rango
    lower = np.array(color_range["lower"])
    upper = np.array(color_range["upper"])
    mask = cv2.inRange(image, lower, upper)

    # Invertir máscara para conservar contenido principal
    if color_range_name == "black_text":
        inverted_mask = mask
    else:
        inverted_mask = cv2.bitwise_not(mask)

    # Aplicar máscara a la imagen
    result = image.copy()
    background = np.full(image.shape, 255, dtype=np.uint8)  # Fondo blanco
    result = cv2.bitwise_and(result, result, mask=inverted_mask)
    background = cv2.bitwise_and(background, background, mask=cv2.bitwise_not(inverted_mask))
    result = cv2.add(result, background)

    return result

def adaptive_removal(image):
    """
    Elimina marca de agua usando técnicas adaptativas
    """
    # Convertir a escala de grises
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Detectar área potencial de marca de agua
    watermark_mask = detect_watermark_area(gray)

    # Aplicar umbralización adaptativa para separar el contenido de la marca de agua
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Combinar con la máscara de marca de agua
    combined_mask = cv2.bitwise_and(watermark_mask, cv2.bitwise_not(adaptive_thresh))

    # Crear imagen de resultado
    result = image.copy()
    if len(image.shape) == 3:
        # Para imágenes a color
        for i in range(3):
            result[:, :, i] = np.where(combined_mask == 255, 255, result[:, :, i])
    else:
        # Para imágenes en escala de grises
        result = np.where(combined_mask == 255, 255, result)

    return result

def inpainting_removal(image, inpaint_radius=3):
    """
    Elimina marca de agua usando inpainting (relleno inteligente)
    """
    # Para ilustraciones en B&N, usar un radio más pequeño para preservar detalles
    if is_bw_illustration(image):
        inpaint_radius = 2

    # Detectar área de marca de agua
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    mask = detect_watermark_area(gray)

    # Aplicar inpainting
    if is_bw_illustration(image):
        result = cv2.inpaint(image, mask, inpaintRadius=inpaint_radius, flags=cv2.INPAINT_NS)
    else:
        result = cv2.inpaint(image, mask, inpaintRadius=inpaint_radius, flags=cv2.INPAINT_TELEA)

    return result

def denoise_image(image, is_bw=False):
    """
    Aplica reducción de ruido adaptada al tipo de imagen
    """
    if is_bw:
        # Para ilustraciones B&N, usar un filtro que preserve bordes
        if len(image.shape) == 3:
            result = cv2.fastNlMeansDenoisingColored(image, None, 3, 3, 7, 21)
        else:
            result = cv2.fastNlMeansDenoising(image, None, 3, 7, 21)
    else:
        # Para fotos e imágenes generales
        if len(image.shape) == 3:
            result = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            result = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    return result

def sharpen_image(image):
    """
    Aplica filtro de nitidez para mejorar detalles
    """
    # Kernel para nitidez
    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]])

    # Aplicar filtro
    sharpened = cv2.filter2D(image, -1, kernel)

    return sharpened


def remove_watermark_from_image_st(image, methods=None, deep_mode=False):
    """
    Función principal para eliminar marcas de agua de imágenes (adaptada para Streamlit)

    Args:
        image: Imagen PIL
        methods: Lista de métodos a aplicar (None = usar todos)
        deep_mode: Si es True, aplica métodos más intensivos

    Returns:
        Imagen PIL procesada
    """
    try:
        # Determinar métodos a usar
        if methods is None:
            methods = DEFAULT_WATERMARK_REMOVAL_METHODS

        # Convertir imagen PIL a formato OpenCV (BGR)
        image_np = np.array(image)
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            cv_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            cv_image = image_np.copy()

        # Detectar automáticamente el tipo de marca de agua e imagen
        has_red = detect_red_watermark(cv_image)
        is_bw = is_bw_illustration(cv_image)

        # Aplicar métodos seleccionados
        result = cv_image.copy()

        # Para imágenes con marca de agua roja
        if has_red:
            result = color_filter_removal(result, "red_watermark")
        else:
            # Procesar con métodos estándar
            for method in methods:
                if method == "color_filter":
                    # En modo profundo, probar varios métodos
                    if deep_mode:
                        if is_bw:
                            # Especial para ilustraciones B&N
                            result = color_filter_removal(result)
                        else:
                            for color_range in ["light_watermark", "gray_watermark"]:
                                result = color_filter_removal(result, color_range)
                    else:
                        result = color_filter_removal(result, "light_watermark")

                elif method == "adaptive" and deep_mode:
                    # Solo usar estos métodos en modo profundo y si son necesarios
                    result = adaptive_removal(result)

                elif method == "inpainting":
                    inpaint_radius = 2 if is_bw else 3
                    result = inpainting_removal(result, inpaint_radius=inpaint_radius)

        # Aplicar mejoras finales según el tipo de imagen
        if is_bw:
            # Para ilustraciones B&N
            result = denoise_image(result, is_bw=True)
            if deep_mode:
                result = sharpen_image(result)
        elif deep_mode:
            # Para fotos normales en modo profundo
            result = denoise_image(result, is_bw=False)

        # Convertir resultado de vuelta a formato PIL
        if len(result.shape) == 3:
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            result_pil = Image.fromarray(result_rgb)
        else:
            result_pil = Image.fromarray(result)

        return result_pil

    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return None


def process_multiple_images(uploaded_files, methods, deep_mode):
    """
    Procesa múltiples imágenes y devuelve los resultados

    Args:
        uploaded_files: Lista de archivos subidos
        methods: Métodos de eliminación a aplicar
        deep_mode: Modo de procesamiento profundo

    Returns:
        Lista de tuplas (nombre_archivo, imagen_original, imagen_procesada)
    """
    results = []

    # Crear barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, uploaded_file in enumerate(uploaded_files):
        # Actualizar progreso
        progress = int((i / len(uploaded_files)) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Procesando imagen {i + 1} de {len(uploaded_files)}: {uploaded_file.name}")

        # Cargar y procesar la imagen
        try:
            original_image = Image.open(uploaded_file).convert("RGB")
            result_image = remove_watermark_from_image_st(original_image, methods, deep_mode)

            if result_image is not None:
                results.append((uploaded_file.name, original_image, result_image))
        except Exception as e:
            st.error(f"Error al procesar {uploaded_file.name}: {str(e)}")

    # Completar progreso
    progress_bar.progress(100)
    status_text.text("¡Procesamiento completado!")

    return results


def main():
    st.sidebar.title("Configuraciones")

    # Opciones de procesamiento
    st.sidebar.subheader("Opciones de procesamiento")

    # Selector de métodos
    methods = st.sidebar.multiselect(
        "Métodos de eliminación:",
        ["color_filter", "inpainting", "adaptive"],
        default=["color_filter", "inpainting"]
    )

    # Opción de modo profundo
    deep_mode = st.sidebar.checkbox("Modo profundo", value=False,
                                    help="Aplica técnicas más intensivas para marcas de agua difíciles")

    # Opciones avanzadas (colapsables)
    with st.sidebar.expander("Opciones avanzadas"):
        # Aquí podrían agregarse ajustes específicos como umbrales, etc.
        st.warning("Las opciones avanzadas afectarán el rendimiento del procesamiento.")

    # Subir múltiples imágenes
    st.sidebar.subheader("Imágenes")
    uploaded_files = st.sidebar.file_uploader("Sube una o varias imágenes",
                                              type=["jpg", "jpeg", "png"],
                                              accept_multiple_files=True)

    # Título principal
    st.title("Aplicación para Quitar Marca de Agua de Imágenes")

    # Descripción
    st.markdown("""
    Esta aplicación permite eliminar marcas de agua de imágenes utilizando diferentes técnicas.
    Sube una o varias imágenes y ajusta las opciones en la barra lateral para obtener mejores resultados.
    """)

    if uploaded_files:
        # Comprobar si hay métodos seleccionados
        if not methods:
            st.warning("Por favor selecciona al menos un método de eliminación de marca de agua.")
            return

        # Procesar imágenes
        results = process_multiple_images(uploaded_files, methods, deep_mode)

        # Mostrar resultados
        if results:
            st.subheader(f"Resultados ({len(results)} imágenes procesadas)")

            # Mostrar cada imagen con su resultado
            for i, (filename, original, result) in enumerate(results):
                with st.expander(f"Imagen {i + 1}: {filename}", expanded=i == 0):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.image(original, caption="Imagen Original", use_container_width=True)

                    with col2:
                        st.image(result, caption="Imagen sin Marca de Agua", use_container_width=True)

                        # Botón de descarga
                        buf = BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            label=f"⬇️ Descargar imagen procesada",
                            data=buf.getvalue(),
                            file_name=f"{os.path.splitext(filename)[0]}_sin_marca.png",
                            mime="image/png"
                        )
        else:
            st.warning("No se pudieron procesar las imágenes.")
    else:
        st.info("Por favor, sube una o varias imágenes para quitar marcas de agua.")


if __name__ == "__main__":
    main()