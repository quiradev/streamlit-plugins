import sys

import streamlit as st
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

try:
    if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

st.set_page_config(layout="wide")

from streamlit_plugins.components.selectbox_rich import st_selectbox_custom


if __name__ == "__main__":
    # Ejemplo de uso: usar los patrones/shortcodes que mostraste
    example_options = [
        "Tema 1 :orange-badge[Importante]",
        "Tema 2 :blue-badge[NUEVO] :material/book:",
        ":small[Opcional] Tema 3 :green-badge[OK]",
        "Tema 4 :orange-background[Revisar]"
    ]
    orig_result = st.selectbox("Selecciona una opción (Streamlit nativo):", example_options, key="st_selectbox")
    result = st_selectbox_custom("Selecciona una opción", example_options, key="mi_html_select")

    # Mostrar selección guardada en session_state (si existe)
    st.markdown(f"Seleccionado (Streamlit nativo): {orig_result}", unsafe_allow_html=True)
    st.markdown(f"Seleccionado (HTML): {result}", unsafe_allow_html=True)