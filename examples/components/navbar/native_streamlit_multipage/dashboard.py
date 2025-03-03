import streamlit as st
from streamlit.navigation.page import StreamlitPage

st.title("Dashboard")
st.subheader("Welcome to the dashboard!")

app_map: dict[str, StreamlitPage] = st.session_state["app_map"]
page_login_id = st.session_state["login_page_id"]
page_logout_id = st.session_state["logout_page_id"]
app_valids_map = {app_id: app for app_id, app in app_map.items() if not app._default and app_id not in [page_login_id, page_logout_id]}
# Se contruye un grid de elementos para cambiar de apps
col1, col2 = st.columns(2)
# Calculo el total de aplicaciones y se asignan a cada columna y fila

total_apps = len(app_valids_map)
apps_per_col = total_apps // 2
# Se recorren las aplicaciones y se asignan a cada columna
for i, (app_id, app) in enumerate(app_valids_map.items()):
    if i < apps_per_col:
        col = col1
    else:
        col = col2

    with col:
        with st.container(border=True):
            st.markdown(f"### {app.title}")
            if st.button(app.title, type="primary"):
                st.session_state["navigation_force_app_id"] = app_id
                st.rerun()
