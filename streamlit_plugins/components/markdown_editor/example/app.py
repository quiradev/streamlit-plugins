import json
import sys
from pathlib import Path

import streamlit as st


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from streamlit_plugins.components.markdown_editor import (
    st_markdown_block_editor,
    st_markdown_editor_with_preview,
)


st.set_page_config(page_title="Editor Markdown por bloques", layout="wide")
EDITOR_HEIGHT = 700

INITIAL_MARKDOWN = r"""# Documento por bloques

Edita bloques Markdown en modo raw o visual. Prueba la barra de formato, los atajos de teclado y el historial.

## Contenido compatible

> Cita de primer nivel.
> > Cita anidada: Tab aumenta el nivel y Shift+Tab lo reduce.

- Enter crea otro ítem; Ctrl+Enter crea un párrafo debajo.
    - Sublista: Tab indenta y Shift+Tab desindenta.
- Shift+Enter continúa el mismo ítem.

- [x] Tarea completada.
- [ ] Tarea pendiente.
    - [ ] Subtarea.

Matemáticas: $E = mc^2$ y $\alpha + \beta = \gamma$.

```python
def saludo(nombre: str) -> str:
    return f'Hola, {nombre}'
```

| Formato | Cómo se edita |
| --- | --- |
| Título | `# texto` |
| Tabla | Sintaxis GFM |

```mermaid
flowchart LR
    A[Editar bloque] --> B[Guardar Markdown]
```"""

REVISED_MARKDOWN = INITIAL_MARKDOWN.replace(
    "Prueba la barra de formato",
    "Texto **revisado** para mostrar la comparación",
) + "\n\n## Nueva sección"


st.title("Editor Markdown por bloques")
st.caption(
    "Demo del componente `st_markdown_block_editor`: edición raw/visual, "
    "guardado automático o manual y revisión de cambios."
)

BLOCK_TYPES = [
    "paragraph", "h1", "h2", "h3", "h4", "h5", "h6", "quote", "list",
    "ordered_list", "task_list", "code", "table", "image", "link", "mermaid",
    "math", "rule",
]
TOOLBAR_SECTIONS = ["view", "format", "block", "history", "changes"]


def parse_sidebar_json(label: str, value: str | None) -> dict | None:
    if value is None or not value.strip():
        return None
    try:
        result = json.loads(value)
    except json.JSONDecodeError as error:
        st.sidebar.error(f"{label}: JSON inválido (línea {error.lineno}).")
        st.stop()
    if not isinstance(result, dict):
        st.sidebar.error(f"{label}: debe ser un objeto JSON.")
        st.stop()
    return result


if "markdown_editor_revision" not in st.session_state:
    st.session_state["markdown_editor_revision"] = 0
with st.sidebar:
    st.header("Configuración del ejemplo")
    if st.button("Restablecer el documento", key="reset_markdown_editor"):
        st.session_state["markdown_editor_revision"] += 1

    with st.expander("Editor y vista", expanded=True):
        editor_modes = st.multiselect(
            "Modos de edición",
            ["raw_visual", "visual"],
            default=["raw_visual", "visual"],
            format_func=lambda value: {"raw_visual": "Raw / visual", "visual": "Visual"}[value],
        )
        if not editor_modes:
            st.error("Selecciona al menos un modo de edición.")
            st.stop()
        mode = st.selectbox("Modo inicial", editor_modes)
        if mode is None:
            st.stop()
        height_kind = st.selectbox("Altura", ["Píxeles", "Adaptable", "Contenido", "Predeterminada"])
        if height_kind == "Píxeles":
            height = st.slider("Altura en píxeles", 240, 1200, EDITOR_HEIGHT, step=20)
        elif height_kind == "Adaptable":
            height = "stretch"
        elif height_kind == "Contenido":
            height = "content"
        else:
            height = None
        only_view = st.toggle("Solo lectura", value=False)
        placeholder = st.text_input("Placeholder", value="Escribe aquí…")
        if placeholder is None:
            st.stop()
        show_status_bar = st.toggle("Mostrar barra de estado", value=True)
        show_copy_button = st.toggle("Mostrar controles de copia", value=True)
        debug_blocks = st.toggle("Mostrar tipo e ID de bloques", value=False)

    with st.expander("Barra y bloques"):
        reorder_mode = st.selectbox(
            "Controles de reordenamiento",
            ["drag_buttons", "drag", "buttons"],
            format_func=lambda value: {
                "drag": "Arrastrar",
                "drag_buttons": "Arrastrar y flechas",
                "buttons": "Solo flechas",
            }[value],
        )
        toolbar_sections = st.multiselect(
            "Secciones de la barra",
            TOOLBAR_SECTIONS,
            default=TOOLBAR_SECTIONS,
            format_func=lambda value: {
                "view": "Vista",
                "format": "Formato",
                "block": "Bloque",
                "history": "Historial",
                "changes": "Cambios",
            }[value],
        )
        allowed_block_types = st.multiselect(
            "Tipos de bloque permitidos",
            BLOCK_TYPES,
            default=BLOCK_TYPES,
        )
        if not allowed_block_types:
            st.error("Selecciona al menos un tipo de bloque.")
            st.stop()

    with st.expander("Guardado"):
        save_mode = st.selectbox("Guardado del editor principal", ["auto", "button"])
        manual_save_mode = st.selectbox("Guardado del ejemplo manual", ["button", "auto"])
        autosave_delay = st.slider("Demora del autoguardado (ms)", 0, 3000, 500, step=100)

    with st.expander("Vista previa"):
        toggle_label = st.text_input("Texto del toggle", value="Mostrar Markdown renderizado")
        if toggle_label is None:
            st.stop()
        toggle_position = st.selectbox(
            "Posición del toggle",
            ["top_right", "top_left", "bottom_right", "bottom_left"],
            format_func=lambda value: {
                "top_right": "Arriba a la derecha",
                "top_left": "Arriba a la izquierda",
                "bottom_right": "Abajo a la derecha",
                "bottom_left": "Abajo a la izquierda",
            }[value],
        )

    with st.expander("Revisión"):
        review_modes = st.multiselect(
            "Vistas de revisión",
            ["visual", "markdown"],
            default=["visual", "markdown"],
        )
        review_layouts = st.multiselect(
            "Disposiciones de revisión",
            ["before", "after", "split", "blocks"],
            default=["before", "after", "split", "blocks"],
        )
        if not review_modes or not review_layouts:
            st.error("Selecciona al menos una vista y una disposición de revisión.")
            st.stop()
        block_diff_style = st.selectbox("Estilo del diff por bloques", ["content", "inline"])

    with st.expander("Renderizado Mermaid y tablas"):
        mermaid_config = parse_sidebar_json(
            "Configuración Mermaid",
            st.text_area(
                "Configuración Mermaid (JSON; vacío para predeterminada)",
                value='{"theme":"default"}',
                height=100,
            ),
        )
        table_styles = parse_sidebar_json(
            "Estilos de tabla",
            st.text_area(
                "Estilos CSS de tabla (JSON; vacío para predeterminados)",
                value='{"th":{"background-color":"#f0f2f6"},"td":{"padding":"8px"}}',
                height=100,
            ),
        )

document = st_markdown_editor_with_preview(
    INITIAL_MARKDOWN,
    key="markdown_block_editor_demo",
    revision=st.session_state["markdown_editor_revision"],
    toggle_label=toggle_label,
    toggle_position=toggle_position,
    height=height,
    mode=mode,
    save_mode=save_mode,
    only_view=only_view,
    debug_blocks=debug_blocks,
    show_status_bar=show_status_bar,
    show_copy_button=show_copy_button,
    placeholder=placeholder,
    editor_modes=editor_modes,
    review_modes=review_modes,
    review_layouts=review_layouts,
    block_diff_style=block_diff_style,
    toolbar_sections=toolbar_sections,
    allowed_block_types=allowed_block_types,
    reorder_mode=reorder_mode,
    autosave_delay=autosave_delay,
    mermaid_config=mermaid_config,
    table_styles=table_styles,
)
with st.expander("Ver Markdown y bloques"):
    markdown_tab, blocks_tab = st.tabs(["Markdown", "Bloques"])
    with markdown_tab:
        st.code(document["markdown"], language="markdown")
    with blocks_tab:
        st.json(document["blocks"])

with st.expander("Ejemplos de guardado manual y revisión"):
    save_column, review_column = st.columns(2, gap="large")
    with save_column:
        st.subheader("Guardado manual")
        if manual_save_mode == "button" and "changes" not in toolbar_sections:
            st.warning("Muestra la sección Cambios para poder guardar el borrador.")
        manual_document = st_markdown_block_editor(
            INITIAL_MARKDOWN,
            key="markdown_editor_manual",
            height=height,
            mode=mode,
            save_mode=manual_save_mode,
            only_view=only_view,
            debug_blocks=debug_blocks,
            show_status_bar=show_status_bar,
            show_copy_button=show_copy_button,
            placeholder=placeholder,
            editor_modes=editor_modes,
            review_modes=review_modes,
            review_layouts=review_layouts,
            block_diff_style=block_diff_style,
            toolbar_sections=toolbar_sections,
            allowed_block_types=allowed_block_types,
            reorder_mode=reorder_mode,
            autosave_delay=autosave_delay,
            mermaid_config=mermaid_config,
            table_styles=table_styles,
        )
        st.code(manual_document["markdown"], language="markdown")
    with review_column:
        st.subheader("Comparación de versiones")
        st_markdown_block_editor(
            INITIAL_MARKDOWN,
            key="markdown_editor_readonly_diff",
            height=height,
            only_view=True,
            mode=mode,
            debug_blocks=debug_blocks,
            diff={"before": INITIAL_MARKDOWN, "after": REVISED_MARKDOWN},
            editor_modes=editor_modes,
            review_modes=review_modes,
            review_layouts=review_layouts,
            block_diff_style=block_diff_style,
            placeholder=placeholder,
            show_copy_button=show_copy_button,
            toolbar_sections=toolbar_sections,
            allowed_block_types=allowed_block_types,
            autosave_delay=autosave_delay,
            mermaid_config=mermaid_config,
            table_styles=table_styles,
        )
