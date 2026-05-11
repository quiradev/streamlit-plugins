import streamlit as st
import random

from streamlit_plugins.components.sankey_input import sankey_input

st.set_page_config(
    page_title="Sankey Input",
    layout="wide",
)

st.title("Sankey Input Component")
st.divider()
COLUMN_COLORS = ["#ff7675", "#74b9ff", "#55efc4", "#fdcb6e", "#a55eea"]

config = [
    {
        "id": "col0",
        "title": "Región",
        "type": "radio",
        "nodes": [
            {"id": "n1_1", "label": "América", "targets": ["n2_1", "n2_2", "n2_4"]},
            {"id": "n1_2", "label": "Europa",  "targets": ["n2_2", "n2_3"]},
            {"id": "n1_3", "label": "Asia",    "targets": ["n2_3", "n2_4"]},
        ],
    },
    {
        "id": "col1",
        "title": "Plataforma",
        "type": "radio",
        "nodes": [
            {"id": "n2_1", "label": "AWS",        "targets": ["n3_1", "n3_2"]},
            {"id": "n2_2", "label": "Azure",      "targets": ["n3_2", "n3_3"]},
            {"id": "n2_3", "label": "GCP",        "targets": ["n3_3", "n3_4"]},
            {"id": "n2_4", "label": "On-Premise", "targets": ["n3_1", "n3_4"]},
        ],
    },
    {
        "id": "col2",
        "title": "Base de Datos",
        "type": "radio",
        "nodes": [
            {"id": "n3_1", "label": "PostgreSQL", "targets": ["n4_1", "n4_2"]},
            {"id": "n3_2", "label": "MongoDB",    "targets": ["n4_2"]},
            {"id": "n3_3", "label": "Redis",      "targets": ["n4_2", "n4_3"]},
            {"id": "n3_4", "label": "Oracle",     "targets": ["n4_1", "n4_3"]},
        ],
    },
    {
        "id": "col3",
        "title": "Nivel SLA",
        "type": "radio",
        "nodes": [
            {"id": "n4_1", "label": "Básico 99%",      "targets": ["n5_1", "n5_3"]},
            {"id": "n4_2", "label": "Premium 99.9%",   "targets": ["n5_1", "n5_2", "n5_4"]},
            {"id": "n4_3", "label": "Crítico 99.99%",  "targets": ["n5_2", "n5_5"]},
        ],
    },
    {
        "id": "col4",
        "title": "Módulos",
        "type": "group",
        "converge": True,
        "nodes": [
            {"id": "n5_1", "label": "Auth Service"},
            {"id": "n5_2", "label": "Data Analytics"},
            {"id": "n5_3", "label": "File Storage"},
            {"id": "n5_4", "label": "Cache Layer"},
            {"id": "n5_5", "label": "AI Processing"},
        ],
    },
]

def _build_random_selections(columns):
    selections = []
    next_allowed = None

    for column in columns:
        nodes = column.get("nodes", [])
        if not nodes:
            selections.append([])
            next_allowed = None
            continue

        node_ids = [node["id"] for node in nodes]
        candidates = [node_id for node_id in node_ids if next_allowed is None or node_id in next_allowed]
        if not candidates:
            candidates = node_ids

        selected_id = random.choice(candidates)
        selections.append([selected_id])

        selected_node = next(node for node in nodes if node["id"] == selected_id)
        next_allowed = set(selected_node.get("targets", []))

    return selections


if "sankey_selections" not in st.session_state:
    st.session_state.sankey_selections = _build_random_selections(config)

st.subheader("Controles")

col_a, col_b, col_c, col_d, col_e = st.columns(5)
with col_a:
    use_gradients = st.toggle("Gradientes", value=False)
with col_b:
    show_suggestions = st.toggle("Mostrar sugerencias", value=True)
with col_c:
    single_path = st.toggle("Single path", value=False)
with col_d:
    converge_group = st.toggle("Grupo convergente", value=True)
with col_e:
    view_only = st.toggle("Solo visualización", value=False)

op_col_1, op_col_2, op_col_3, op_col_4 = st.columns(4)
with op_col_1:
    op_inactive = st.slider("Opacidad inactivos", 0.0, 1.0, 0.5, 0.05)
with op_col_2:
    op_suggest = st.slider("Opacidad sugeridos", 0.0, 1.0, 0.2, 0.05)
with op_col_3:
    op_partial = st.slider("Opacidad parciales", 0.0, 1.0, 0.35, 0.05)
with op_col_4:
    op_active = st.slider("Opacidad activos", 0.0, 1.0, 0.8, 0.05)

st.divider()

result = sankey_input(
    config=config,
    app_config={
        "useGradients": use_gradients,
        "showSuggestions": show_suggestions,
        "singlePath": single_path,
        "convergeGroup": converge_group,
        "opInactive": op_inactive,
        "opSuggest": op_suggest,
        "opPartial": op_partial,
        "opActive": op_active,
        "columnColors": COLUMN_COLORS,
    },
    initial_selections=st.session_state.sankey_selections,
    view_only=view_only,
    key="sankey_demo",
)

if result and result.selections is not None:
    st.session_state.sankey_selections = result.selections

if result and result.selections:
    col_titles = [col["title"] for col in config]
    st.subheader("Selecciones actuales")
    any_selected = False
    for i, sel in enumerate(result.selections):
        if sel:
            any_selected = True
            node_labels = [
                n["label"]
                for n in config[i]["nodes"]
                if n["id"] in sel
            ]
            st.write(f"**{col_titles[i]}**: {', '.join(node_labels)}")
    if not any_selected:
        st.info("Haz clic en los nodos del diagrama para seleccionarlos.")
