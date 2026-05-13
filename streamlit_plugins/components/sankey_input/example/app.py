import streamlit as st
import random

from streamlit_plugins.components.sankey_input import sankey_input


class ConfigError(ValueError):
    pass


def build_config(simple_config: list[dict]) -> list[dict]:
    """
    Convierte una configuración simplificada al formato completo de sankey_input.

    Formato de entrada por columna:
        {
            "title": str,                  # obligatorio
            "type": str,                   # "radio" | "group"  (default "radio")
            "converge": bool,              # opcional, para tipo "group"
            "nodes": dict | list,
                # dict  -> {label_salida: targets}
                #   targets puede ser:
                #     "*"        -> todos los nodos de la columna siguiente
                #     None | []  -> ningún target
                #     [str, ...] -> lista de labels de la columna siguiente
                # list  -> [label, ...]  (columna final sin targets)
        }

    Raises:
        ConfigError: si la configuración no es válida.
    """
    VALID_TYPES = {"radio", "group"}

    # ── Validación estructural básica ────────────────────────────────────────
    if not isinstance(simple_config, list) or not simple_config:
        raise ConfigError("simple_config debe ser una lista no vacía de columnas.")

    for col_idx, col in enumerate(simple_config):
        ref = f"Columna {col_idx}"
        if not isinstance(col, dict):
            raise ConfigError(f"{ref}: cada columna debe ser un diccionario.")
        if "title" not in col:
            raise ConfigError(f"{ref}: falta el campo obligatorio 'title'.")
        if not isinstance(col["title"], str) or not col["title"].strip():
            raise ConfigError(f"{ref}: 'title' debe ser una cadena no vacía.")
        col_type = col.get("type", "radio")
        if col_type not in VALID_TYPES:
            raise ConfigError(f"{ref} ('{col['title']}'): 'type' debe ser uno de {VALID_TYPES}, se recibió '{col_type}'.")
        nodes_raw = col.get("nodes")
        if nodes_raw is None:
            raise ConfigError(f"{ref} ('{col['title']}'): falta el campo obligatorio 'nodes'.")
        if not isinstance(nodes_raw, (dict, list)):
            raise ConfigError(f"{ref} ('{col['title']}'): 'nodes' debe ser un dict o una lista.")
        labels = list(nodes_raw.keys()) if isinstance(nodes_raw, dict) else list(nodes_raw)
        if not labels:
            raise ConfigError(f"{ref} ('{col['title']}'): 'nodes' no puede estar vacío.")
        if len(labels) != len(set(labels)):
            dupes = [l for l in set(labels) if labels.count(l) > 1]
            raise ConfigError(f"{ref} ('{col['title']}'): labels duplicados: {dupes}.")

    # ── Paso 1: asignar IDs a cada nodo (col_idx, label) -> node_id ─────────
    label_to_id: dict[tuple[int, str], str] = {}
    col_labels: dict[int, list[str]] = {}
    for col_idx, col in enumerate(simple_config):
        nodes_raw = col["nodes"]
        labels = list(nodes_raw.keys()) if isinstance(nodes_raw, dict) else list(nodes_raw)
        col_labels[col_idx] = labels
        for node_idx, label in enumerate(labels):
            label_to_id[(col_idx, label)] = f"n{col_idx + 1}_{node_idx + 1}"

    # ── Paso 2: validar targets y construir el config completo ───────────────
    result = []
    last_idx = len(simple_config) - 1

    for col_idx, col in enumerate(simple_config):
        ref = f"Columna {col_idx} ('{col['title']}')"
        nodes_raw = col["nodes"]
        full_nodes = []

        if isinstance(nodes_raw, dict):
            next_labels = col_labels.get(col_idx + 1, [])

            for node_idx, (label, target_spec) in enumerate(nodes_raw.items()):
                node_id = f"n{col_idx + 1}_{node_idx + 1}"

                # Resolver target_spec → lista de labels
                if target_spec == "*":
                    if col_idx == last_idx:
                        raise ConfigError(f"{ref}, nodo '{label}': no puede haber targets ('*') en la última columna.")
                    resolved = next_labels
                elif not target_spec:          # None o []
                    resolved = []
                elif isinstance(target_spec, list):
                    if col_idx == last_idx and target_spec:
                        raise ConfigError(f"{ref}, nodo '{label}': la última columna no puede tener targets.")
                    # Verificar que todos los targets existen en la siguiente columna
                    unknown = [t for t in target_spec if t not in next_labels]
                    if unknown:
                        raise ConfigError(
                            f"{ref}, nodo '{label}': los siguientes targets no existen en la columna {col_idx + 1} "
                            f"('{simple_config[col_idx + 1]['title']}'): {unknown}. "
                            f"Labels disponibles: {next_labels}."
                        )
                    resolved = target_spec
                else:
                    raise ConfigError(
                        f"{ref}, nodo '{label}': 'targets' debe ser '*', None, [] o una lista de strings; "
                        f"se recibió: {type(target_spec).__name__!r}."
                    )

                targets = [label_to_id[(col_idx + 1, t)] for t in resolved]
                node_def: dict = {"id": node_id, "label": label}
                if targets:
                    node_def["targets"] = targets
                full_nodes.append(node_def)

        else:  # list → columna final
            if col_idx != last_idx:
                # Lista de labels en columna intermedia → sin targets (válido, solo advertencia implícita)
                pass
            for node_idx, label in enumerate(nodes_raw):
                full_nodes.append({"id": f"n{col_idx + 1}_{node_idx + 1}", "label": label})

        col_def: dict = {
            "id": f"col{col_idx}",
            "title": col["title"],
            "type": col.get("type", "radio"),
            "nodes": full_nodes,
        }
        if col.get("converge"):
            col_def["converge"] = True

        result.append(col_def)

    return result

st.set_page_config(
    page_title="Sankey Input",
    layout="wide",
)

st.title("Sankey Input Component")
st.divider()
COLUMN_COLORS = ["#ff7675", "#74b9ff", "#55efc4", "#fdcb6e", "#a55eea"]

# --- Ejemplo 1: Región → Plataforma → Base de Datos → Nivel SLA → Módulos ---
config = build_config([
    {
        "title": "Región",
        "type": "radio",
        "nodes": {
            "América": ["AWS", "Azure", "On-Premise"],
            "Europa":  ["Azure", "GCP"],
            "Asia":    ["GCP", "On-Premise"],
        },
    },
    {
        "title": "Plataforma",
        "type": "radio",
        "nodes": {
            "AWS":        ["PostgreSQL", "MongoDB"],
            "Azure":      ["MongoDB", "Redis"],
            "GCP":        ["Redis", "Oracle"],
            "On-Premise": ["PostgreSQL", "Oracle"],
        },
    },
    {
        "title": "Base de Datos",
        "type": "radio",
        "nodes": {
            "PostgreSQL": ["Básico 99%", "Premium 99.9%"],
            "MongoDB":    ["Premium 99.9%"],
            "Redis":      ["Premium 99.9%", "Crítico 99.99%"],
            "Oracle":     ["Básico 99%", "Crítico 99.99%"],
        },
    },
    {
        "title": "Nivel SLA",
        "type": "radio",
        "nodes": {
            "Básico 99%":     ["Auth Service", "File Storage"],
            "Premium 99.9%":  ["Auth Service", "Data Analytics", "Cache Layer"],
            "Crítico 99.99%": ["Data Analytics", "AI Processing"],
        },
    },
    {
        "title": "Módulos",
        "type": "group",
        "converge": True,
        "nodes": ["Auth Service", "Data Analytics", "File Storage", "Cache Layer", "AI Processing"],
    },
])

# --- Ejemplo 2: Idioma → Unidad → Output format → Ficheros ---
second_config = build_config([
    {
        "title": "Idioma",
        "type": "radio",
        "nodes": {
            "Castellano": ["PostgreSQL", "MongoDB", "Redis", "Oracle"],
            "Ingles":     ["PostgreSQL", "MongoDB", "Redis", "Oracle"],
            "Italiano":   ["PostgreSQL", "MongoDB", "Redis", "Oracle"],
        },
    },
    {
        "title": "Unidad",
        "type": "radio",
        "nodes": {
            "PostgreSQL": ["Bulleted", "Executive", "Extended"],
            "MongoDB":    ["Executive"],
            "Redis":      ["Executive", "Extended"],
            "Oracle":     ["Bulleted", "Extended"],
        },
    },
    {
        "title": "Output format",
        "type": "radio",
        "nodes": {
            "Bulleted":  ["Auth Service", "File Storage"],
            "Executive": ["Auth Service", "Data Analytics", "Cache Layer"],
            "Extended":  ["Data Analytics", "AI Processing"],
        },
    },
    {
        "title": "Ficheros",
        "type": "group",
        "converge": True,
        "nodes": ["Auth Service", "Data Analytics", "File Storage", "Cache Layer", "AI Processing"],
    },
])


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

CONFIGS = {"Ejemplo 1 – Región/Plataforma": config, "Ejemplo 2 – Idioma/Unidad": second_config}
selected_example = st.selectbox("Configuración de ejemplo", list(CONFIGS.keys()))
active_config = CONFIGS[selected_example]

if st.session_state.get("_last_example") != selected_example:
    st.session_state.sankey_selections = _build_random_selections(active_config)
    st.session_state["_last_example"] = selected_example

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

with st.expander("⚙️ Dimensiones y layout"):
    dim_c1, dim_c2, dim_c3, dim_c4, dim_c5 = st.columns(5)
    with dim_c1:
        path_thickness = st.slider("Grosor caminos (px)", 4, 40, 12)
    with dim_c2:
        normal_node_width = st.slider("Ancho nodo (px)", 8, 60, 20)
    with dim_c3:
        group_width = st.slider("Ancho grupo (px)", 80, 400, 170)
    with dim_c4:
        card_width = st.number_input("Ancho máx. tarjeta (px)", min_value=400, max_value=3000, value=1100, step=50)
    with dim_c5:
        card_height = st.number_input("Alto mín. tarjeta (px)", min_value=0, max_value=2000, value=0, step=50)
    lay_c1, lay_c2, lay_c3, lay_c4 = st.columns(4)
    with lay_c1:
        col_spacing = st.slider("Separación columnas (px)", 80, 400, 180)
    with lay_c2:
        min_node_gap = st.slider("Gap mín. nodos (px)", 5, 100, 35)
    with lay_c3:
        margin_top = st.slider("Margen superior (px)", 10, 120, 60)
    with lay_c4:
        margin_bottom = st.slider("Margen inferior (px)", 10, 120, 60)

with st.expander("🎨 Estilos custom"):
    enable_custom_palette = st.toggle("Personalizar paleta", value=False)
    palette_mode = st.selectbox(
        "Tipo de paleta",
        ["Categorical (Streamlit)", "Sequential (Streamlit)", "Diverging (Streamlit)", "Lista manual"],
        disabled=not enable_custom_palette,
    )

    custom_palette_colors = None
    if enable_custom_palette and palette_mode == "Lista manual":
        pal_c1, pal_c2, pal_c3, pal_c4, pal_c5 = st.columns(5)
        with pal_c1:
            pal_1 = st.color_picker("Paleta 1", COLUMN_COLORS[0])
        with pal_c2:
            pal_2 = st.color_picker("Paleta 2", COLUMN_COLORS[1])
        with pal_c3:
            pal_3 = st.color_picker("Paleta 3", COLUMN_COLORS[2])
        with pal_c4:
            pal_4 = st.color_picker("Paleta 4", COLUMN_COLORS[3])
        with pal_c5:
            pal_5 = st.color_picker("Paleta 5", COLUMN_COLORS[4])
        custom_palette_colors = [pal_1, pal_2, pal_3, pal_4, pal_5]

    enable_custom_styles = st.toggle("Personalizar estilos CSS", value=False)
    css_c1, css_c2, css_c3, css_c4 = st.columns(4)
    with css_c1:
        color_panel_bg = st.color_picker("Fondo tarjeta", "#ffffff", disabled=not enable_custom_styles)
        color_bg = st.color_picker("Fondo contenedor", "#f0f2f5", disabled=not enable_custom_styles)
    with css_c2:
        color_text_main = st.color_picker("Texto principal", "#2d3436", disabled=not enable_custom_styles)
        color_text_light = st.color_picker("Texto secundario", "#636e72", disabled=not enable_custom_styles)
    with css_c3:
        color_inactive_gray = st.color_picker("Caminos inactivos", "#dfe6e9", disabled=not enable_custom_styles)
        color_inactive_node = st.color_picker("Nodos inactivos", "#b2bec3", disabled=not enable_custom_styles)
    with css_c4:
        color_group_bg = st.color_picker("Fondo grupo", "#f8f9fa", disabled=not enable_custom_styles)
        color_group_border = st.color_picker("Borde grupo", "#dcdde1", disabled=not enable_custom_styles)

    typo_c1, typo_c2, typo_c3, typo_c4 = st.columns(4)
    with typo_c1:
        custom_base_radius = st.slider("Base radius (rem)", 0.0, 2.0, 0.5, 0.1, disabled=not enable_custom_styles)
    with typo_c2:
        custom_button_radius = st.slider("Button radius (rem)", 0.0, 2.0, 0.5, 0.1, disabled=not enable_custom_styles)
    with typo_c3:
        custom_base_font_size = st.slider("Base font size (px)", 10, 28, 16, disabled=not enable_custom_styles)
    with typo_c4:
        custom_base_font_weight = st.slider("Base font weight", 100, 900, 400, 100, disabled=not enable_custom_styles)

    # typo_c5, typo_c6 = st.columns(2)
    # with typo_c5:
    #     custom_code_font_size = st.slider("Code font size (px)", 10, 24, 14, disabled=not enable_custom_styles)
    # with typo_c6:
    #     custom_code_font_weight = st.slider("Code font weight", 100, 900, 400, 100, disabled=not enable_custom_styles)

    label_c1, label_c2, label_c3 = st.columns(3)
    with label_c1:
        custom_node_label_font_size = st.slider("Etiqueta nodo (px)", 8, 24, 11, disabled=not enable_custom_styles)
    with label_c2:
        custom_group_title_font_size = st.slider("Titulo grupo (px)", 8, 24, 11, disabled=not enable_custom_styles)
    with label_c3:
        custom_group_item_font_size = st.slider("Item grupo (px)", 10, 30, 13, disabled=not enable_custom_styles)

    custom_card_padding = st.slider("Padding tarjeta (px)", 0, 80, 30, disabled=not enable_custom_styles)

st.divider()

app_cfg = {
    "useGradients": use_gradients,
    "showSuggestions": show_suggestions,
    "singlePath": single_path,
    "convergeGroup": converge_group,
    "opInactive": op_inactive,
    "opSuggest": op_suggest,
    "opPartial": op_partial,
    "opActive": op_active,
}

if enable_custom_palette:
    if palette_mode == "Categorical (Streamlit)":
        app_cfg["pallete"] = "categorical"
    elif palette_mode == "Sequential (Streamlit)":
        app_cfg["pallete"] = "sequential"
    elif palette_mode == "Diverging (Streamlit)":
        app_cfg["pallete"] = "diverging"
    else:
        app_cfg["pallete"] = custom_palette_colors or COLUMN_COLORS
else:
    app_cfg["pallete"] = "categorical"

style_cfg = {}
if enable_custom_styles:
    style_cfg = {
        "bgColor": color_bg,
        "panelBg": color_panel_bg,
        "textMain": color_text_main,
        "textLight": color_text_light,
        "inactiveGray": color_inactive_gray,
        "inactiveNode": color_inactive_node,
        "groupBg": color_group_bg,
        "groupBorder": color_group_border,
        "baseRadius": f"{custom_base_radius}rem",
        "buttonRadius": f"{custom_button_radius}rem",
        "baseFontSize": f"{custom_base_font_size}px",
        "baseFontWeight": str(custom_base_font_weight),
        # "codeFontSize": f"{custom_code_font_size}px",
        # "codeFontWeight": str(custom_code_font_weight),
        "nodeLabelFontSize": f"{custom_node_label_font_size}px",
        "groupTitleFontSize": f"{custom_group_title_font_size}px",
        "groupItemFontSize": f"{custom_group_item_font_size}px",
        "cardPadding": f"{custom_card_padding}px",
    }

card_width_px = int(card_width) if isinstance(card_width, (int, float)) and card_width > 0 else None
card_height_px = int(card_height) if isinstance(card_height, (int, float)) and card_height > 0 else None

result = sankey_input(
    config=active_config,
    app_config=app_cfg,
    initial_selections=st.session_state.sankey_selections,
    view_only=view_only,
    path_thickness=path_thickness,
    normal_node_width=normal_node_width,
    group_width=group_width,
    width=card_width_px,
    height=card_height_px,
    diagram_options={
        "columnSpacing": col_spacing,
        "minNodeGapY": min_node_gap,
        "marginTop": margin_top,
        "marginBottom": margin_bottom,
    },
    style_config=style_cfg,
    key="sankey_demo",
)

if result and result.selections is not None:
    st.session_state.sankey_selections = result.selections

if result and result.selections:
    col_titles = [col["title"] for col in active_config]
    st.subheader("Selecciones actuales")
    any_selected = False
    for i, sel in enumerate(result.selections):
        if sel:
            any_selected = True
            node_labels = [
                n["label"]
                for n in active_config[i]["nodes"]
                if n["id"] in sel
            ]
            st.write(f"**{col_titles[i]}**: {', '.join(node_labels)}")
    if not any_selected:
        st.info("Haz clic en los nodos del diagrama para seleccionarlos.")
