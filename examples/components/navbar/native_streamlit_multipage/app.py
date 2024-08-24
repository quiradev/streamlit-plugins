import sys

import streamlit as st

try:
    if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

st.set_page_config(layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "app_id" not in st.session_state:
    st.session_state.app_id = None


def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.session_state.app_id = "app_default"
        st.rerun()


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.app_id = None
        st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "reports/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)
bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
alerts = st.Page(
    "reports/alerts.py", title="System alerts", icon=":material/notification_important:"
)

search = st.Page("tools/search.py", title="Search", icon=":material/search:")
history = st.Page("tools/history.py", title="History", icon=":material/history:")

# HERE IS THE CHANGE
from streamlit_plugins.components.navbar import st_navbar, build_menu_from_st_pages

menu_data, app_map = build_menu_from_st_pages(
    {"Reports": [dashboard, bugs, alerts]}, {"Tools": [search, history]},
    login_app=login_page,
    logout_app=logout_page,
)

with st.sidebar:
    st.write("Logged in:", st.session_state.logged_in)
    position_mode = st.radio(
        "Navbar position mode",
        ["top", "under"],
    )
    sticky_nav = st.checkbox("Sticky navbar", value=True)


app_id = st_navbar(
    menu_definition=menu_data if st.session_state.logged_in else [],
    login_name=logout_page.title if st.session_state.logged_in else login_page.title,
    hide_streamlit_markers=False,
    override_app_selected_id=st.session_state.app_id,
    sticky_nav=sticky_nav,  # at the top or not
    position_mode=position_mode,  # top or subtop
)
if app_id == "app_login":
    if st.session_state.logged_in:
        app_id = "app_logout"

st.session_state.app_id = None  # Added to fix login/logout issue
app_map[app_id]._can_be_called = True
app_map[app_id].run()


# if st.session_state.logged_in:
#     pg = st.navigation(
#         {
#             "Account": [logout_page],
#             "Reports": [dashboard, bugs, alerts],
#             "Tools": [search, history],
#         },
#         position="hidden"
#     )
#
# else:
#     pg = st.navigation([login_page], position="hidden")
#
#
# pg.run()
