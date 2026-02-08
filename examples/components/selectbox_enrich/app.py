import sys

import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

try:
    if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

st.set_page_config(layout="wide")

from streamlit_plugins.components.selectbox_enrich import st_selectbox_custom


if __name__ == "__main__":
    label_visibility = st.segmented_control(
        "Label visibility",
        ["visible", "hidden", "collapsed"],
        default="visible",
    )
    help_text = st.text_input("Help text (supports HTML)", value="Selecciona una opción del menú desplegable.")
    accept_new_options = st.checkbox("Permitir nuevas opciones (no implementado)", disabled=True)
    # Ejemplo de uso: usar los patrones/shortcodes que mostraste
    example_options = [
        "*Tema 1* :orange-badge[Importante]",
        "**Tema 2** :blue-badge[NUEVO] :material/book:",
        ":small[Opcional] Tema 3 :green-badge[OK]",
        "***Tema 4*** :orange-background[Revisar]"
    ]
    with st.container(horizontal=True):
        with st.container():
            orig_result = st.selectbox(
                "Selecciona una opción (Streamlit nativo):", example_options,
                help=help_text,
                label_visibility=label_visibility or "visible",
                accept_new_options=accept_new_options,
                key="st_selectbox",
            )
            st.markdown(f"Seleccionado (Streamlit nativo): {orig_result}", unsafe_allow_html=True)
        
        with st.container():
            result = st_selectbox_custom(
                "Selecciona una opción", example_options,
                help=help_text,
                label_visibility=label_visibility or "visible",
                accept_new_options=accept_new_options,
                key="mi_html_select",
            )
            st.markdown(f"Seleccionado (HTML): {result}", unsafe_allow_html=True)