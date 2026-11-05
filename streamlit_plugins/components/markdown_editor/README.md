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

## Opciones

| Opción | Descripción |
| --- | --- |
| `key` | Clave de Streamlit, obligatoria y no vacía. |
| `revision` | Entero no negativo para reinicializar el documento desde `initial_blocks`. |
| `height` | Altura en píxeles o `"stretch"`, `"content"` o `None`. |
| `mode` | `"raw_visual"` para alternar entre sintaxis y vista visual, o `"visual"` para iniciar en visual. |
| `save_mode` | `"auto"` publica cambios al editar; `"button"` espera a que se pulse Guardar. |
| `only_view` | Muestra el documento sin edición. Puede combinarse con `diff` para revisión. |
| `diff` | Versiones anterior y nueva como strings o como pareja `before_blocks` / `after_blocks`. |
| `editor_modes` | Modos de edición permitidos: `"raw_visual"` y/o `"visual"`. |
| `review_modes` | Vistas disponibles durante la revisión: `"visual"` y/o `"markdown"`. |
| `review_layouts` | Disposiciones disponibles: `"before"`, `"after"`, `"split"` y `"blocks"`. |
| `toolbar_sections` | Secciones visibles de la barra: `view`, `format`, `block`, `history` y `changes`. |
| `debug_blocks` | Muestra información de depuración de los bloques. |
| `show_status_bar` | Muestra la barra inferior de bloques, caracteres y estado de guardado. Activada por defecto; usa `False` para ocultarla. En solo lectura permanece oculta. |

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
