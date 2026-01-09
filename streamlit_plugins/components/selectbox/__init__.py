from pathlib import Path
from streamlit.elements.lib.utils import to_key
from streamlit.elements.lib.policies import maybe_raise_label_warnings
from streamlit.dataframe_util import convert_anything_to_list
from streamlit.type_util import check_python_comparable
from streamlit.errors import StreamlitAPIException
from streamlit.elements.lib.options_selector_utils import create_mappings
from streamlit.elements.lib.layout_utils import validate_width
from streamlit.components.v2 import component
from textwrap import dedent
from typing import Any, Callable, Literal, Sequence, TypeVar
from uuid import uuid4
import streamlit as st
import re

def _convert_shortcodes_to_html(s: str) -> str:
    """Convierte shortcodes tipo Streamlit a HTML con estilos inline.

    Soporta:
    - :color-badge[text]         -> span con estilo de badge (bg + color)
    - :color[text]               -> span con color de texto inline
    - :color-background[text]    -> span con background inline (padding + border-radius)
    - :small[text]               -> small
    - :material/icon_name:       -> span para icono (se puede estilizar con font en CSS)
    """
    if not isinstance(s, str):
        return str(s)

    # mapa de colores (bg, text). Ajustar valores si se desea otro look.
    COLORS = {
        "red": ("#e53935", "#fff"),
        "orange": ("#ffb74d", "#000"),
        "yellow": ("#ffd54f", "#000"),
        "green": ("#43a047", "#fff"),
        "blue": ("#1976d2", "#fff"),
        "violet": ("#8e24aa", "#fff"),
        "gray": ("#9e9e9e", "#fff"),
        "grey": ("#9e9e9e", "#fff"),
        "primary": ("#0f62fe", "#fff"),
        # rainbow will be a gradient
        "rainbow": ("linear-gradient(90deg,#ff5f6d,#ffc371)", "#fff"),
    }

    def _badge_repl(match):
        color = match.group(1).lower()
        text = match.group(2)
        bg, fg = COLORS.get(color, (None, None))
        if bg is None:
            # usar clase por defecto si color desconocido
            return f'<span class="badge">{text}</span>'
        if bg.startswith("linear-gradient"):
            style = f'background:{bg};color:{fg};padding:2px 8px;border-radius:999px;font-size:0.8rem;display:inline-block;'
        else:
            style = f'background:{bg};color:{fg};padding:2px 8px;border-radius:999px;font-size:0.8rem;display:inline-block;'
        return f'<span style="{style}">{text}</span>'

    def _bg_repl(match):
        color = match.group(1).lower()
        text = match.group(2)
        bg, fg = COLORS.get(color, (None, None))
        if bg is None:
            return f'<span class="bg-{color}">{text}</span>'
        if bg.startswith("linear-gradient"):
            style = f'background:{bg};color:{fg};padding:2px 6px;border-radius:6px;display:inline-block;'
        else:
            style = f'background:{bg};color:{fg};padding:2px 6px;border-radius:6px;display:inline-block;'
        return f'<span style="{style}">{text}</span>'

    def _color_repl(match):
        color = match.group(1).lower()
        text = match.group(2)
        # si existe en mapa usar el color de fondo como color de texto cuando tiene solo "color[]"
        bg, fg = COLORS.get(color, (None, None))
        css_color = bg if bg is not None else color
        # si bg es gradient, no tiene sentido como color de texto -> fallback a fg o black
        if css_color.startswith("linear-gradient") if isinstance(css_color, str) else False:
            css_color = fg or "#000"
        return f'<span style="color:{css_color}">{text}</span>'

    # procesar badges primero (evita colisiones con color[...] patterns)
    s = re.sub(r":([a-zA-Z]+)-badge\[(.*?)\]", _badge_repl, s)
    # color-background next
    s = re.sub(r":([a-zA-Z]+)-background\[(.*?)\]", _bg_repl, s)
    # color[text]
    s = re.sub(r":([a-zA-Z]+)\[(.*?)\]", _color_repl, s)
    # small
    s = re.sub(r":small\[(.*?)\]", r"<small>\1</small>", s)
    # material icons (keeps name, you can style .material-icon in CSS)
    s = re.sub(r":material/([a-z0-9_]+):",
               r'<span class="material-icon">\1</span>', s)

    return s


T = TypeVar("T")


ASSETS_PATH = Path(__file__).parent / "assets"
HTML_PATH = ASSETS_PATH / "part.html"
CSS_PATH = ASSETS_PATH / "style.css"
JS_PATH = ASSETS_PATH / "script.js"

HTML = st.session_state.get("__custom_selectbox_html", None)
if HTML is None:
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        HTML = f.read()
    st.session_state["__custom_selectbox_html"] = HTML

CSS = st.session_state.get("__custom_selectbox_css", None)
if CSS is None:
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        CSS = f.read()
    st.session_state["__custom_selectbox_css"] = CSS

JS = st.session_state.get("__custom_selectbox_js", None)
if JS is None:
    with open(JS_PATH, "r", encoding="utf-8") as f:
        JS = f.read()
    st.session_state["__custom_selectbox_js"] = JS

def st_selectbox_custom(
    label: str,
    options: Sequence[T],  # Type for empty or Never-inferred options
    index: int = 0,
    format_func: Callable[[Any], str] = str,
    key: str | None = None,
    help: str | None = None,
    on_change: Callable[..., None] | None = None,
    args: tuple[Any, ...] | list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    *,  # keyword-only arguments:
    placeholder: str | None = None,
    disabled: bool = False,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    # accept_new_options: Literal[False] = False,
    width: int | Literal["stretch"] = "stretch",
    unsafe_allow_html: bool = True,
):
    """
    Renderiza un selectbox en HTML que acepta opciones con HTML/shortcodes.
    Guarda el valor seleccionado en st.session_state[key].
    """
    if key is None:
        key = "selectbox_" + uuid4().hex

    key = to_key(key)
    # check_widget_policies(
    #     self.dg,
    #     key,
    #     on_change,
    #     default_value=None if index == 0 else index,
    # )
    maybe_raise_label_warnings(label, label_visibility)
    opt = convert_anything_to_list(options)
    check_python_comparable(opt)
    if unsafe_allow_html:
        opt = [_convert_shortcodes_to_html(opt) for opt in opt]

    if not isinstance(index, int) and index is not None:
        raise StreamlitAPIException(
            f"Selectbox Value has invalid type: {type(index).__name__}"
        )

    if index is not None and len(opt) > 0 and not 0 <= index < len(opt):
        raise StreamlitAPIException(
            "Selectbox index must be greater than or equal to 0 "
            "and less than the length of options."
        )
    # Convert empty string to single space to distinguish from None:
    # - None (default) → "" → Frontend shows contextual placeholders
    # - "" (explicit empty) → " " → Frontend shows empty placeholder
    # - "Custom" → "Custom" → Frontend shows custom placeholder
    if placeholder == "":
        placeholder = " "

    formatted_options, formatted_option_to_option_index = create_mappings(
        opt, format_func
    )

    # element_id = compute_and_register_element_id(
    #     "selectbox",
    #     user_key=key,
    #     # Treat the provided key as the main identity. Only include
    #     # the options and accept_new_options in the identity computation
    #     # as those can invalidate the current selection.
    #     # Changes to format_func also invalidate the current selection,
    #     # but this is already handled via the `options` parameter below:
    #     key_as_main_identity={"options", "accept_new_options"},
    #     dg=self.dg,
    #     label=label,
    #     options=formatted_options,
    #     index=index,
    #     help=help,
    #     placeholder=placeholder,
    #     accept_new_options=accept_new_options,
    #     width=width,
    # )

    # session_state = get_session_state().filtered_state
    # if key is not None and key in session_state and session_state[key] is None:
    #     index = None

    # selectbox_proto = SelectboxProto()
    # selectbox_proto.id = element_id
    # selectbox_proto.label = label
    # if index is not None:
    #     selectbox_proto.default = index
    # selectbox_proto.options[:] = formatted_options
    # selectbox_proto.form_id = current_form_id(self.dg)
    # selectbox_proto.placeholder = placeholder or ""
    # selectbox_proto.disabled = disabled
    # selectbox_proto.label_visibility.value = get_label_visibility_proto_value(
    #     label_visibility
    # )
    # selectbox_proto.accept_new_options = accept_new_options

    if help is not None:
        help = dedent(help)
    #     selectbox_proto.help = dedent(help)

    # serde = SelectboxSerde(
    #     opt,
    #     formatted_options=formatted_options,
    #     formatted_option_to_option_index=formatted_option_to_option_index,
    #     default_option_index=index,
    # )
    # widget_state = register_widget(
    #     selectbox_proto.id,
    #     on_change_handler=on_change,
    #     args=args,
    #     kwargs=kwargs,
    #     deserializer=serde.deserialize,
    #     serializer=serde.serialize,
    #     ctx=ctx,
    #     value_type="string_value",
    # )
    # widget_state = maybe_coerce_enum(widget_state, options, opt)

    # if widget_state.value_changed:
    #     serialized_value = serde.serialize(widget_state.value)
    #     if serialized_value is not None:
    #         selectbox_proto.raw_value = serialized_value
    #     selectbox_proto.set_value = True

    validate_width(width)
    # layout_config = LayoutConfig(width=width)

    # if ctx:
    #     save_for_app_testing(ctx, element_id, format_func)
    # self.dg._enqueue("selectbox", selectbox_proto, layout_config=layout_config)
    # return widget_state.value

    component_name = f"html_select_{key}"

    data = {
        "options": opt,
        "index": index,
        "placeholder": placeholder or "Selecciona una opción ▾",
        # "accept_new_options": bool(accept_new_options),
        "disabled": bool(disabled),
        "help": help or "",
        "theme": st.context.theme,
    }

    my_comp = component(component_name, html=HTML, css=CSS, js=JS)
    # El parámetro on_selected_change se invocará cuando el componente llame a setTriggerValue('selected', ...)
    # Actualizamos session_state con el HTML seleccionado (puedes almacenarlo como quieras)
    result = my_comp(
        key=key,
        data=data,
        width=width,
        isolate_styles=False,
        on_selected_change=lambda v=None: print(v)
    )
    selected = result.get("selected", None) if result else None

    if selected:
        # st.session_state[key] = options[int(selected)]
        return options[int(selected)]

    prev_val = st.session_state.get(key, None)
    return prev_val
