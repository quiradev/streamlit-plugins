import streamlit as st


st.title("Dashboard")
st.subheader("Welcome to the dashboard!")

app_map = st.session_state["app_map"]
app_valids_map = {app_id: app for app_id, app in app_map.items() if app_id not in ["app_login", "app_logout", "app_default"]}
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
                st.session_state.app_id = app_id
                st.rerun()
