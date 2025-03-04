# Aplicación de Filtros de Imágenes con Streamlit

### Joel Miguel Maya Castrejón │ mike.maya@ciencias.unam.mx │ 417112602

Este proyecto consiste en una aplicación web interactiva creada con **Python** y **Streamlit** que permite aplicar diferentes filtros a una imagen. Entre los filtros implementados se encuentran:

1. **Mosaico**  
2. **Tono de Gris**  
3. **Alto Contraste**  
4. **Inverso (Negativo)**  
5. **Filtro RGB (solo un canal de color)**  
6. **Brillo**

## Requisitos

- Python 3.12 o superior.
- [Streamlit](https://docs.streamlit.io/) para el desarrollo de la interfaz.
- [Pillow](https://pillow.readthedocs.io/) (PIL) para leer las imágenes.

En el archivo **requirements.txt** están listadas las dependencias necesarias (Streamlit y Pillow). Asegúrate de instalarlas antes de ejecutar la aplicación.

## Instalación

1. **Clona** o **descarga** [este repositorio](https://github.com/mikemayac/Image-Filter-Application) en tu máquina local.
2. Crea un **entorno virtual** (opcional, pero recomendado) e instálalo:
   ```bash
   python -m venv venv
   source venv/bin/activate        # En Linux/Mac
   # o en Windows: venv\Scripts\activate
   ```
3. Instala los paquetes necesarios:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución de la Aplicación

1. Dentro del entorno virtual y en la carpeta donde se encuentra el archivo principal `tarea1_pdi.py`, ejecuta:
   ```bash
   streamlit run tarea1_pdi.py
   ```
2. Automáticamente se abrirá tu navegador mostrando la interfaz de la aplicación. Si no se abre, puedes copiar la URL que aparece en la terminal y pegarla en tu navegador.

## Uso de la Aplicación

1. **Sube una imagen** en la barra lateral (sidebar). Acepta formatos `JPG`, `JPEG` o `PNG`. En caso de que la imagen esté en formato RGBA la convierte a RGB.
2. **Selecciona** el filtro que deseas aplicar desde la lista desplegable (selectbox):
   - **Mosaico**: Divide la imagen en bloques y asigna el color promedio a cada bloque.
   - **Tono de Gris**: Convierte la imagen a blanco y negro, usando un promedio `(R+G+B)/3` o un método ponderado `(0.3*R + 0.7*G + 0.1*B)`.
   - **Alto Contraste**: Primero convierte a gris, luego aplica un umbral para convertir los píxeles a blanco o negro.
   - **Inverso (Negativo)**: Cada píxel `(R, G, B)` se convierte en `(255-R, 255-G, 255-B)`.
   - **Filtro RGB**: Muestra únicamente un canal (Rojo, Verde o Azul), poniendo los demás en `0`.
   - **Brillo**: Suma (o resta) un valor a los tres canales `(R, G, B)`, lo cual incrementa o reduce el brillo de la imagen.
3. **Ajusta** los parámetros en la barra lateral (por ejemplo, tamaño del mosaico, umbral de alto contraste, canal de color, ajuste de brillo, etc.).
4. Observa cómo se muestra la **imagen original** en la columna izquierda y la **imagen resultante** en la columna derecha.
5. Se puede descargar la imagen procesada con el botón que parece en la parte superior derecha.

## Estructura del Proyecto

```
├── tarea1_pdi.py          # Código principal de la aplicación
│── .streamlit/            # Capeta de configuración 
│    └── config.toml       # Archivo usado para configuración del peso de las imágenes
├── README.md              # Archivo de documentación
├── requirements.txt       # Dependencias del proyecto
└── venv/                  # Entorno virtual
```

## Contribuir

Si deseas contribuir:

1. Haz un **fork** de este repositorio.
2. Crea una **rama** con una nueva funcionalidad o corrección de errores: `git checkout -b nueva-funcionalidad`.
3. Realiza tus cambios y haz **commit**: `git commit -m 'Agrega nueva funcionalidad'`.
4. Haz un **push** a tu repositorio: `git push origin nueva-funcionalidad`.
5. Crea un **Pull Request** en este repositorio para revisar y fusionar tus cambios.

## Licencia

MIT.