# Aplicación para Eliminar Marcas de Agua en Imágenes

### Joel Miguel Maya Castrejón │ mike.maya@ciencias.unam.mx │ 417112602


Este proyecto consiste en una aplicación web interactiva creada con **Python** y **Streamlit** que permite eliminar marcas de agua de imágenes utilizando técnicas avanzadas de procesamiento de imágenes.

## Características Principales

La aplicación puede detectar y eliminar diferentes tipos de marcas de agua, incluyendo:

1. **Marcas de agua transparentes o semitransparentes**
2. **Texto y logotipos superpuestos**
3. **Marcas de agua rojas tipo "PREVIEW"**
4. **Marcas de agua en ilustraciones en blanco y negro**
5. **Sellos y firmas digitales**

## Métodos de Eliminación

La aplicación implementa tres métodos principales que pueden combinarse entre sí:

- **Filtrado por Color (color_filter)**: Elimina marcas de agua basándose en su rango de color.
- **Relleno Inteligente (inpainting)**: Reconstruye áreas con marcas de agua usando información de píxeles circundantes.
- **Eliminación Adaptativa (adaptive)**: Combina técnicas avanzadas para casos difíciles (disponible en modo profundo).

## Requisitos

- Python 3.7 o superior
- [Streamlit](https://docs.streamlit.io/) para la interfaz web
- [OpenCV](https://opencv.org/) para procesamiento de imágenes
- [NumPy](https://numpy.org/) para operaciones numéricas
- [Pillow](https://pillow.readthedocs.io/) para manipulación de imágenes
- [scikit-image](https://scikit-image.org/) para técnicas avanzadas de procesamiento

Todas las dependencias están listadas en el archivo **requirements.txt**.

## Instalación

1. **Clona** [este repositorio](https://github.com/mikemayac/Remove-Watermark) en tu máquina local.
2. Crea un **entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate        # En Linux/Mac
   # o en Windows: venv\Scripts\activate
   ```
3. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución de la Aplicación

1. Activa el entorno virtual y ejecuta:
   ```bash
   streamlit run remove_watermark.py
   ```
2. Se abrirá tu navegador mostrando la interfaz de la aplicación. Si no se abre automáticamente, copia la URL que aparece en la terminal.

## Uso de la Aplicación

1. **Sube una o varias imágenes** usando el selector en la barra lateral. La aplicación acepta formatos JPG, JPEG o PNG.

2. **Selecciona los métodos de eliminación** que deseas utilizar:
   - **color_filter**: Ideal para marcas de agua con colores distintivos
   - **inpainting**: Efectivo para reconstruir áreas dañadas
   - **adaptive**: Para casos difíciles, solo funciona con modo profundo activado

3. **Activa o desactiva el modo profundo**:
   - Con modo profundo: Procesamiento más intensivo para marcas difíciles
   - Sin modo profundo: Procesamiento más rápido y conservador

4. **Visualiza los resultados**:
   - La aplicación mostrará la imagen original y la imagen procesada
   - Cada resultado incluye un botón para descargar la imagen procesada

5. **Recomendaciones de uso**:
   - Comienza con la configuración predeterminada (color_filter + inpainting)
   - Para marcas difíciles, activa el modo profundo
   - Si aún persisten marcas, añade el método adaptive
   - Prueba diferentes combinaciones para obtener los mejores resultados

## Tipos de Marcas de Agua Compatibles

La aplicación está optimizada para detectar y eliminar:

- **Marcas de agua transparentes**: Comunes en stock photos y bancos de imágenes
- **Texto superpuesto**: Incluyendo textos de copyright y firmas digitales
- **Logotipos**: Marcas y símbolos superpuestos a la imagen
- **Marcas tipo "PREVIEW"**: Especialmente en color rojo
- **Marcas de agua en ilustraciones B&N**: Con procesamiento especial para preservar detalles finos

## Estructura del Proyecto

```
├── remove_watermark.py    # Código principal de la aplicación
├── README.md              # Archivo de documentación
├── requirements.txt       # Dependencias del proyecto
│── .streamlit/            # Capeta de configuración 
│    └── config.toml       # Archivo usado para configuración del peso de las imágenes
└── venv/                  # Entorno virtual
```

## Funcionamiento Técnico Detallado

### 1. Algoritmos de Detección de Marcas de Agua

#### 1.1 Detección por Análisis de Gradiente

Este algoritmo (`detect_watermark_area`) funciona bajo el principio de que las marcas de agua suelen tener menos detalles o bordes que el contenido principal:

- **Cálculo de Gradiente**: Utiliza filtros Sobel en direcciones X e Y para calcular la magnitud del gradiente en cada punto.
- **Normalización y Umbralización**: Las áreas con gradientes débiles (cambios sutiles) son más propensas a ser marcas de agua.
- **Operaciones Morfológicas**: Se aplican operaciones de cierre y apertura para limpiar la máscara y unir regiones fragmentadas.
- **Eficacia**: Ideal para marcas de agua semitransparentes que se extienden sobre toda la imagen.

#### 1.2 Detección de Marcas de Agua Rojas

El algoritmo `detect_red_watermark` está especializado en identificar texto rojo típico como "PREVIEW":

- **Conversión a Espacio de Color HSV**: Facilita la separación del componente de color (tono) de la luminosidad.
- **Rango Dual para Rojo**: El rojo aparece en ambos extremos del espectro H (0-10° y 170-180°), por lo que se usan dos rangos.
- **Umbral Proporcional**: Considera una imagen como marcada si al menos el 0.1% de sus píxeles caen dentro del rango rojo.

#### 1.3 Detección de Marcas de Agua de Texto

El método `detect_text_watermark` se basa en la identificación de componentes pequeños y repetitivos:

- **Umbralización Adaptativa**: Resalta el texto independientemente de las variaciones de iluminación.
- **Análisis de Componentes Conectados**: Identifica letras individuales como componentes separados.
- **Filtrado por Tamaño**: Los componentes pequeños (menos de 50 píxeles) suelen ser parte de marcas de agua de texto.
- **Morfología Matemática**: Une componentes cercanos para formar palabras completas.

#### 1.4 Identificación de Ilustraciones en Blanco y Negro

La función `is_bw_illustration` analiza la distribución de colores para identificar ilustraciones:

- **Análisis de Histograma**: Calcula la distribución de niveles de gris en la imagen.
- **Proporción de Píxeles B&N**: Si más del 90% de los píxeles son muy claros o muy oscuros, se clasifica como ilustración B&N.
- **Importancia**: Permite aplicar algoritmos especializados que preservan mejor las líneas finas.

### 2. Métodos de Eliminación Explicados en Detalle

#### 2.1 Filtrado por Color (`color_filter_removal`)

Este método elimina marcas de agua basándose en sus características de color:

- **Rangos de Color Predefinidos**: La aplicación incluye rangos optimizados para diferentes tipos de marcas de agua:
  - Marcas claras (180-255)
  - Texto negro (0-130)
  - Marcas rojas (HSV específico)
  - Marcas grises (100-200)

- **Proceso para Marcas de Agua Rojas**:
  1. Detección específica en espacio HSV
  2. Aplicación de dilatación para expandir ligeramente la máscara
  3. Uso de inpainting con algoritmo TELEA para rellenar áreas marcadas

- **Proceso para Ilustraciones B&N**:
  1. Detección de texto mediante análisis de componentes
  2. Inpainting con radio pequeño usando algoritmo Navier-Stokes
  3. Mejora de contraste mediante CLAHE y umbralización Otsu

- **Proceso para Marcas Generales**:
  1. Creación de máscara basada en rango de color
  2. Inversión de máscara para preservar contenido principal
  3. Reemplazo de píxeles marcados con fondo blanco

#### 2.2 Relleno Inteligente (`inpainting_removal`)

Este método reconstruye áreas dañadas usando información de los alrededores:

- **Detección de Áreas**: Usa análisis de gradiente para identificar regiones con posibles marcas de agua.

- **Tipos de Algoritmos de Inpainting**:
  - **INPAINT_NS (Navier-Stokes)**: Para ilustraciones B&N. Basado en ecuaciones diferenciales parciales que preservan estructuras lineales y bordes. Ideal para conservar líneas finas en dibujos.
  
  - **INPAINT_TELEA (Fast Marching Method)**: Para fotografías e imágenes naturales. Reconstruye regiones propagando información desde los bordes hacia adentro, creando transiciones suaves y naturales.

- **Radio de Inpainting Adaptativo**: 
  - Radio pequeño (2px) para ilustraciones B&N
  - Radio estándar (3px) para fotografías y otras imágenes

#### 2.3 Eliminación Adaptativa (`adaptive_removal`)

Este método avanzado combina varias técnicas para casos difíciles:

- **Generación de Máscaras Combinadas**:
  1. Detección de áreas con poco detalle (máscara de gradiente)
  2. Umbralización adaptativa para separar contenido y marca de agua
  3. Combinación lógica (AND) de ambas máscaras

- **Preservación Selectiva**:
  - Reemplaza solo los píxeles de la marca de agua mientras preserva el contenido original
  - Maneja de forma diferente imágenes en color y en escala de grises
  - Se activa solo en modo profundo debido a su complejidad y tiempo de procesamiento

### 3. Técnicas de Post-Procesamiento

#### 3.1 Reducción de Ruido (`denoise_image`)

Elimina artefactos introducidos durante el proceso de eliminación:

- **Algoritmo Non-Local Means**: Reducción de ruido que preserva detalles importantes
- **Parametrización Adaptativa**:
  - Filtrado suave para ilustraciones B&N (h=3)
  - Filtrado más agresivo para fotografías (h=10)
- **Canales Independientes**: Procesa de forma diferente imágenes en color y en escala de grises

#### 3.2 Mejora de Nitidez (`sharpen_image`)

Aplica un kernel de convolución para realzar detalles:

- **Kernel de Nitidez**: Matriz 3×3 con valor central de 9 y -1 en todas las posiciones circundantes
- **Efecto**: Realza bordes y detalles finos que pueden haber quedado suavizados
- **Uso Selectivo**: Se aplica principalmente a ilustraciones B&N en modo profundo

### 4. Proceso Completo de Eliminación

El proceso completo (`remove_watermark_from_image`) sigue estos pasos secuenciales:

1. **Detección Automática**:
   - Determina si la imagen contiene marcas de agua rojas
   - Identifica si es una ilustración en blanco y negro

2. **Selección de Ruta de Procesamiento**:
   - Ruta especializada para marcas rojas
   - Ruta general para otras marcas de agua

3. **Aplicación Secuencial de Métodos**:
   - Primero `color_filter` (con selección automática de rangos en modo profundo)
   - Luego `adaptive` (si está en modo profundo)
   - Finalmente `inpainting` (con radio adaptado al tipo de imagen)

4. **Post-Procesamiento**:
   - Reducción de ruido adaptada al tipo de imagen
   - Mejora de nitidez para ilustraciones (en modo profundo)

5. **Resultados**:
   - Se preserva la resolución y formato de la imagen original
   - Se mantienen intactas las áreas sin marcas de agua

### 5. Combinación de Métodos

La aplicación permite usar métodos individuales o combinarlos para resultados óptimos:

- **Procesamiento Secuencial**: Cada método procesa el resultado del anterior
- **Filtrado + Inpainting**: Combinación ideal para la mayoría de marcas de agua
- **Triple Combinación**: Con modo profundo para casos extremadamente difíciles
- **Autodetección Inteligente**: Ajusta parámetros automáticamente según el tipo de imagen

## Contribuir

Si deseas contribuir:

1. Haz un **fork** de [este repositorio](https://github.com/mikemayac/Remove-Watermark).
2. Crea una **rama** con tu nueva funcionalidad: `git checkout -b nueva-funcionalidad`.
3. Realiza tus cambios y haz **commit**: `git commit -m 'Agrega nueva funcionalidad'`.
4. Haz un **push** a tu repositorio: `git push origin nueva-funcionalidad`.
5. Crea un **Pull Request** en este repositorio.

## Licencia

MIT.