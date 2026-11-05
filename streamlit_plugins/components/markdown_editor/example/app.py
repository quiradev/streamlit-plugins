import sys
from pathlib import Path

import streamlit as st


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from streamlit_plugins.components.markdown_editor import st_markdown_block_editor


st.set_page_config(page_title="Editor Markdown por bloques", layout="wide")
EDITOR_HEIGHT = 700

INITIAL_BLOCKS = [
    {"id": "title", "markdown": "# Documento por bloques"},
    {
        "id": "intro",
        "markdown": (
            "Edita bloques Markdown en modo raw o visual. Prueba la barra de formato, "
            "los atajos de teclado y el historial."
        ),
    },
    {"id": "heading", "markdown": "## Contenido compatible"},
    {
        "id": "quote",
        "markdown": "> Cita de primer nivel.\n> > Cita anidada: Tab aumenta el nivel y Shift+Tab lo reduce.",
    },
    {
        "id": "list",
        "markdown": (
            "- Enter crea otro ítem; Ctrl+Enter crea un párrafo debajo.\n"
            "    - Sublista: Tab indenta y Shift+Tab desindenta.\n"
            "- Shift+Enter continúa el mismo ítem."
        ),
    },
    {
        "id": "task-list",
        "markdown": "- [x] Tarea completada.\n- [ ] Tarea pendiente.\n    - [ ] Subtarea.",
    },
    {"id": "math", "markdown": r"Matemáticas: $E = mc^2$ y $\alpha + \beta = \gamma$."},
    {
        "id": "code",
        "markdown": "```python\ndef saludo(nombre: str) -> str:\n    return f'Hola, {nombre}'\n```",
    },
    {
        "id": "table",
        "markdown": "| Formato | Cómo se edita |\n| --- | --- |\n| Título | `# texto` |\n| Tabla | Sintaxis GFM |",
    },
    {
        "id": "mermaid",
        "markdown": "```mermaid\nflowchart LR\n    A[Editar bloque] --> B[Guardar Markdown]\n```",
    },
]


st.title("Editor Markdown por bloques")
st.caption(
    "Demo del componente `st_markdown_block_editor`: edición raw/visual, "
    "guardado automático o manual y revisión de cambios."
)

if "markdown_editor_revision" not in st.session_state:
    st.session_state["markdown_editor_revision"] = 0
if st.button("Restablecer el documento", key="reset_markdown_editor"):
    st.session_state["markdown_editor_revision"] += 1

debug_blocks = st.toggle("Mostrar tipo e ID de los bloques", value=False)
show_status_bar = st.toggle(
    "Mostrar barra inferior de bloques y caracteres",
    value=True,
    key="markdown_editor_show_status_bar",
)
toolbar_sections = st.multiselect(
    "Secciones visibles de la barra",
    ["view", "format", "block", "history", "changes"],
    default=["view", "format", "block", "history", "changes"],
    format_func=lambda section: {
        "view": "Vista",
        "format": "Formato",
        "block": "Bloque",
        "history": "Historial",
        "changes": "Cambios",
    }[section],
)

document = st_markdown_block_editor(
    INITIAL_BLOCKS,
    key="markdown_block_editor_demo",
    revision=st.session_state["markdown_editor_revision"],
    height=EDITOR_HEIGHT,
    mode="raw_visual",
    save_mode="auto",
    debug_blocks=debug_blocks,
    show_status_bar=show_status_bar,
    toolbar_sections=toolbar_sections,
)

markdown_tab, blocks_tab = st.tabs(["Markdown", "Bloques"])
with markdown_tab:
    st.code(document["markdown"], language="markdown")
with blocks_tab:
    st.json(document["blocks"])

revised_blocks = [
    {**INITIAL_BLOCKS[0]},
    {**INITIAL_BLOCKS[1], "markdown": "Texto **revisado** para mostrar la comparación."},
    *INITIAL_BLOCKS[2:],
    {"id": "new-section", "markdown": "## Nueva sección"},
]

with st.expander("Ejemplos de guardado manual y revisión"):
    save_column, review_column = st.columns(2, gap="large")
    with save_column:
        st.subheader("Guardado manual")
        if "changes" not in toolbar_sections:
            st.warning("Muestra la sección Cambios para poder guardar el borrador.")
        manual_document = st_markdown_block_editor(
            INITIAL_BLOCKS,
            key="markdown_editor_manual",
            height=EDITOR_HEIGHT,
            mode="visual",
            save_mode="button",
            debug_blocks=debug_blocks,
            show_status_bar=show_status_bar,
            toolbar_sections=toolbar_sections,
        )
        st.code(manual_document["markdown"], language="markdown")
    with review_column:
        st.subheader("Comparación de versiones")
        st_markdown_block_editor(
            INITIAL_BLOCKS,
            key="markdown_editor_readonly_diff",
            height=EDITOR_HEIGHT,
            only_view=True,
            debug_blocks=debug_blocks,
            diff={"before_blocks": INITIAL_BLOCKS, "after_blocks": revised_blocks},
        )
