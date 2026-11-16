# Editor Markdown por bloques para Streamlit

Componente de Streamlit para editar documentos Markdown como bloques independientes. El editor permite alternar entre la sintaxis raw y una vista visual, conservar identificadores estables por bloque y revisar cambios entre versiones.

## Requisitos

- Python 3.10 o superior
- Streamlit 1.51.0 o superior

El editor integra sus renderizadores en el bundle del frontend. No requiere instalar paquetes Python adicionales para Mermaid, LaTeX o resaltado de código.

## Instalación

Desde la raíz del repositorio, genera e instala el wheel:

```shell
python streamlit_plugins/components/markdown_editor/packaging/setup.py bdist_wheel
```

El wheel se genera en `dist/streamlit-plugins-component-markdown-editor/`. Para usar el componente desde el repositorio, basta con tener instaladas sus dependencias declaradas en `packaging/requirements.txt`.

## Uso

```python
import streamlit as st

from streamlit_plugins.components.markdown_editor import st_markdown_block_editor

blocks = [
    {"id": "title", "markdown": "# Mi documento"},
    {"id": "body", "markdown": "Texto **editable** en Markdown."},
]

document = st_markdown_block_editor(
    blocks,
    key="document-editor",
    mode="raw_visual",
    save_mode="auto",
)

st.code(document["markdown"], language="markdown")
```

La función devuelve un diccionario con `blocks`, `markdown`, `mode` y `save_mode`. Cada bloque contiene un `id` y su contenido Markdown; si se omite el ID en los datos iniciales, se genera uno por posición.

También se puede pasar Markdown raw como `str`; el editor separa los bloques en el cliente. Usa una secuencia de bloques cuando necesites asignar IDs estables:

```python
document = st_markdown_block_editor(
    "# Mi documento\n\nTexto **editable** en Markdown.",
    key="document-editor",
    save_mode="auto",
)
```

Para alternar entre el editor y el renderizado nativo de Streamlit sin gestionar el estado de la vista, usa `st_markdown_editor_with_preview`. Acepta las mismas opciones del editor mediante `**editor_options`; `toggle_position` puede ser `"top_left"`, `"top_right"`, `"bottom_left"` o `"bottom_right"`. Con `save_mode="button"`, muestra junto al toggle un aviso de que los cambios sin guardar se perderán al mostrar la vista previa. La función gestiona la revisión al volver de la vista previa.

```python
from streamlit_plugins.components.markdown_editor import st_markdown_editor_with_preview

document = st_markdown_editor_with_preview(
    "# Mi documento\n\nTexto **editable**.",
    key="document",
    toggle_position="top_left",
    height=600,
    save_mode="auto",
)
```

## Opciones

| Opción | Descripción |
| --- | --- |
| `key` | Clave de Streamlit, obligatoria y no vacía. |
| `revision` | Entero no negativo para reinicializar el documento desde `initial_blocks`. |
| `height` | Altura en píxeles o `"stretch"`, `"content"` o `None`. |
| `mode` | `"raw_visual"` para alternar entre sintaxis y vista visual, o `"visual"` para iniciar en visual. |
| `save_mode` | `"auto"` publica cambios tras el debounce; `"button"` espera a que se pulse Guardar. |
| `autosave_delay` | Debounce en milisegundos, definido en Python: `500` por defecto. `0` publica sin espera. |
| `allowed_block_types` | Tipos ofrecidos en el selector y niveles de título del submenú. Por defecto, todos. No restringe el Markdown escrito ni elimina bloques existentes. |
| `reorder_mode` | Controles de reordenamiento: `"drag"`, `"drag_buttons"` o `"buttons"`. Por defecto, `"drag_buttons"`. |
| `mermaid_config` | Configuración visual Mermaid: `theme`, `themeVariables` y `fontFamily`. Mantiene `securityLevel="strict"`; sin controles adicionales en la interfaz. |
| `table_styles` | Propiedades CSS por elemento: `{"table": {...}, "th": {...}, "td": {...}}`. Se aplican en visual y solo lectura, sin controles adicionales. |
| `only_view` | Muestra el documento sin edición. Puede combinarse con `diff` para revisión. |
| `diff` | Versiones anterior y nueva como strings o como pareja `before_blocks` / `after_blocks`. |
| `editor_modes` | Modos de edición permitidos: `"raw_visual"` y/o `"visual"`. |
| `review_modes` | Vistas disponibles durante la revisión: `"visual"` y/o `"markdown"`. |
| `review_layouts` | Disposiciones disponibles: `"before"`, `"after"`, `"split"` y `"blocks"`. |
| `block_diff_style` | `"content"` muestra el diff debajo de los bloques complejos; `"inline"` marca los cambios dentro del contenido compatible. |
| `toolbar_sections` | Secciones visibles de la barra: `view`, `format`, `block`, `history` y `changes`. |
| `debug_blocks` | Muestra información de depuración de los bloques. |
| `show_status_bar` | Muestra la barra inferior de bloques, caracteres y estado de guardado. Activada por defecto; usa `False` para ocultarla. En solo lectura permanece oculta. |
| `show_copy_button` | Muestra u oculta los controles para copiar el documento o un bloque. |
| `placeholder` | Texto mostrado en bloques vacíos; `""` lo oculta. |

## Funcionalidades y diseño

### Edición por bloques

El documento se compone de bloques Markdown con IDs estables. El selector de tipo refleja el bloque activo y los cambios de tipo se aplican inmediatamente. Se puede trabajar en dos modos:

- **Raw**: se edita la sintaxis Markdown directamente.
- **Visual**: se edita el contenido con su formato renderizado.

Ambos modos serializan al mismo Markdown. Se admiten párrafos, títulos, citas anidadas, listas con viñetas y numeradas, listas de tareas, tablas, enlaces, imágenes, bloques de código, fórmulas LaTeX, diagramas Mermaid y separadores. Las listas, citas y continuaciones conservan su estructura al cambiar entre modos; la serialización añade las separaciones Markdown necesarias para mantener sublistas y niveles de cita.

| Tipo de bloque | Enter | Shift+Enter | Tab / Shift+Tab |
| --- | --- | --- | --- |
| Párrafo o enlace | Nueva línea en el bloque | Nueva línea en el bloque | Navegar entre controles |
| Título | Añade un bloque debajo | Nueva línea en el título | Navegar entre controles |
| Lista | Nuevo ítem; en un ítem vacío, desindenta o sale de la lista | Continuación sin marcador | Indentar o desindentar el ítem y sus hijos |
| Cita | Nueva línea conservando el nivel | Nueva línea conservando el nivel | Aumentar o reducir el nivel |
| Código o Mermaid | Nueva línea conservando la sangría | Nueva línea conservando la sangría | Añadir o quitar sangría |
| Tabla | Insertar fila debajo | Insertar columna a la derecha | Celda siguiente o anterior |
| Imagen o separador | Añade un bloque debajo | Sin acción | Navegar entre controles |

`Ctrl+Enter` o `Cmd+Enter` añade un párrafo debajo del bloque. En listas, `Backspace` sobre un ítem vacío permite salir de él sin eliminar sus hijos. El historial deshace y rehace cambios de texto, formato, inserción, eliminación y reordenación (`Ctrl/Cmd+Z`, `Ctrl/Cmd+Shift+Z` o `Ctrl+Y`).

Los bloques se reordenan según `reorder_mode`: solo con el tirador para arrastrar, con el tirador y las flechas, o solo con las flechas. En `drag_buttons`, las flechas aparecen al pasar el cursor sobre el tirador; en `buttons`, aparecen al pasar el cursor sobre el bloque. El menú contextual aparece junto al bloque y ofrece acciones comunes y acciones según su tipo. `Shift+F10` lo abre desde el teclado y `Escape` lo cierra. Sus acciones se pueden recorrer horizontalmente cuando no caben en el espacio disponible.

### Renderizado local

Los renderizadores se incluyen localmente en el componente; no se descargan desde un CDN:

- **Código**: Highlight.js para Python, JavaScript, TypeScript, JSON, YAML, SQL, Bash, XML/HTML y CSS. Los lenguajes no registrados se muestran como texto sin formato.
- **Matemáticas**: KaTeX genera MathML para fórmulas inline (`$...$`) y de bloque (`$$...$$`).
- **Diagramas**: Mermaid genera SVG con `securityLevel="strict"`.

Las fórmulas y los diagramas se muestran renderizados en modo Visual y permiten alternar a su fuente para editarla. Los errores de renderizado se notifican en el bloque. Las tablas visuales se muestran como cuadrícula; los controles tienen etiquetas accesibles y descripciones emergentes.

### Guardado, copia y revisión

`save_mode="auto"` agrupa los cambios en JavaScript y los publica tras `autosave_delay` milisegundos sin escribir. Cambiar a solo lectura o desmontar el editor publica el cambio pendiente; los ecos del documento guardado no reconstruyen el borrador ni su historial. Con `save_mode="button"`, los cambios se publican al pulsar **Guardar**. **Ver cambios** abre una revisión del borrador frente a la última versión guardada sin guardar ni descartar cambios; volver al editor conserva el borrador y el historial.

`only_view=True` muestra el documento sin edición. Si se proporciona `diff`, por defecto la revisión ofrece los modos **Visual** y **Diff Markdown**, además de las disposiciones permitidas por `review_layouts`: Antes, Después, Split o Bloques. El diff Markdown marca inserciones y eliminaciones por línea; la vista por bloques identifica contenido modificado, adiciones, eliminaciones y movimientos. En la vista Visual, `block_diff_style="content"` muestra el diff de contenido debajo de los bloques complejos; `"inline"` anota cambios dentro de los tipos compatibles.

Para revisar documentos por bloques se pasan ambas versiones:

```python
st_markdown_block_editor(
    old_blocks,
    key="document-review",
    only_view=True,
    diff={"before_blocks": old_blocks, "after_blocks": new_blocks},
)
```

Los IDs estables ayudan a identificar movimientos y cambios de contenido entre versiones. Si no se proporcionan IDs en los bloques iniciales, se generan a partir de su posición; para comparar versiones, conservar los IDs originales permite una correspondencia más precisa.

El botón **Copiar todo** y la acción de copia por bloque copian Markdown en modo Raw y contenido enriquecido en modo Visual. En la revisión se copia la versión mostrada sin las marcas del diff. La copia enriquecida requiere un contexto seguro del navegador (HTTPS o `localhost`) y permisos del portapapeles.

### Controles y presentación configurables

`editor_modes`, `review_modes` y `review_layouts` permiten limitar las opciones de edición y revisión visibles. Sus valores deben pertenecer a las opciones admitidas y no pueden repetirse; el modo inicial debe estar incluido en `editor_modes`. `toolbar_sections` controla la visibilidad de las secciones de la barra, no las acciones de edición disponibles. Para impedir la edición, usa `only_view=True`.

Cuando solo se permite una opción, su selector desaparece. Los tipos admitidos por `allowed_block_types` son `paragraph`, `h1` a `h6`, `quote`, `list`, `ordered_list`, `task_list`, `code`, `table`, `image`, `link`, `mermaid`, `math` y `rule`.

```python
document = st_markdown_block_editor(
    blocks,
    key="custom-editor",
    mode="visual",
    editor_modes=("visual",),
    allowed_block_types=("paragraph", "h2", "h3", "list", "table", "mermaid"),
    autosave_delay=800,
    mermaid_config={
        "theme": "base",
        "themeVariables": {"primaryColor": "#e6f4ff", "primaryTextColor": "#123456"},
        "fontFamily": "Arial",
    },
    table_styles={
        "th": {"background-color": "#e6f4ff"},
        "td": {"padding": "12px"},
    },
)
```

El botón **Enlace** de Formato permite añadir un enlace al texto seleccionado (o escribir el texto si no hay selección) y editar un enlace inline cuando el cursor está dentro de él. Su edición conserva el resto del párrafo, título, cita, lista o celda. Las propiedades de enlaces, imágenes, numeración de listas y lenguaje del código se editan en un diálogo con Aplicar, Cancelar y Escape.

La barra superior agrupa las acciones principales —historial, guardado, modos, copia y ayuda— y mantiene los grupos de herramientas separados. Los grupos de Formato y Bloque se pueden plegar; la ayuda incluye atajos de teclado. La barra inferior con el recuento de bloques y caracteres y el estado de guardado se puede ocultar con `show_status_bar=False`. `debug_blocks=True` añade información de tipo e ID para inspeccionar la estructura.

Para una demostración interactiva de edición, guardado manual y comparación, ejecuta:

```shell
python streamlit_plugins/components/markdown_editor/example/runner.py
```

## Desarrollo y pruebas

Los archivos `editor.html`, `editor.css` y `editor.js` se mantienen y editan directamente en `frontend/build/`, sin copias fuera de ese directorio. El bundle de renderizadores está incluido en el repositorio y en la distribución Python. Para regenerarlo después de modificar `renderers.js` o sus dependencias:

```shell
cd streamlit_plugins/components/markdown_editor/frontend
npm ci
npm run build
```

El script valida la sintaxis de `build/editor.js` y genera `build/renderers.bundle.js` y `build/THIRD_PARTY_LICENSES.txt`. El empaquetado base de `streamlit-plugins` ya incluye ese directorio para los componentes.

Para las pruebas Python, instala la dependencia de desarrollo y ejecuta:

```shell
python -m pip install -r streamlit_plugins/components/markdown_editor/tests/requirements.txt
python -m pytest streamlit_plugins/components/markdown_editor/tests/test_markdown_editor.py
```

Las pruebas de navegador requieren Chromium además de las dependencias Node:

```shell
cd streamlit_plugins/components/markdown_editor/tests
npm ci
npx playwright install chromium
npm test
```
