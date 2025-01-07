import sys

try:
    if '_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper' not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

import streamlit as st

from streamlit_plugins.components.theme_changer import st_theme_changer

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

st.title("Theme Changer Component")
st.caption("Just push the button to change the theme! On the client side, of course.")
# specify the primary menu definition
st_theme_changer()

st_theme_changer(key="", render_mode="pill")


