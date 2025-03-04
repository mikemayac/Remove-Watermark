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

## Funcionamiento Técnico

La aplicación implementa varios algoritmos de procesamiento de imágenes:

1. **Detección de marcas de agua**:
   - Análisis de gradiente para detectar áreas con menos detalle
   - Detección de componentes conectados para texto
   - Análisis de histograma para identificar tipo de imagen

2. **Eliminación de marcas de agua**:
   - Filtrado por rango de colores
   - Algoritmos de inpainting (Navier-Stokes y TELEA)
   - Umbralización adaptativa
   - Reducción de ruido y mejora de nitidez

3. **Post-procesamiento**:
   - Reducción de ruido adaptada al tipo de imagen
   - Mejora de nitidez para ilustraciones

## Contribuir

Si deseas contribuir:

1. Haz un **fork** de [este repositorio](https://github.com/mikemayac/Remove-Watermark).
2. Crea una **rama** con tu nueva funcionalidad: `git checkout -b nueva-funcionalidad`.
3. Realiza tus cambios y haz **commit**: `git commit -m 'Agrega nueva funcionalidad'`.
4. Haz un **push** a tu repositorio: `git push origin nueva-funcionalidad`.
5. Crea un **Pull Request** en este repositorio.

## Licencia

MIT.