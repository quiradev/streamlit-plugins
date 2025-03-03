import sys

import streamlit as st

try:
    if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

st.set_page_config(layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "app_id" not in st.session_state:
    st.session_state.app_id = None

if "active_app_id" not in st.session_state:
    st.session_state.active_app_id = None

if "force_app_id" not in st.session_state:
    st.session_state.force_app_id = None

USER = "admin"
PASSWORD = "admin"

positions = ["top", "under", "side"]

def my_sidebar():
    with st.sidebar:
        st.write("Logged in:", st.session_state.logged_in)
        position_mode = st.radio(
            "Navbar position mode",
            positions,
            key="position_mode_input",
            index=positions.index(st.session_state.get("position_mode", "top")),
        )
        sticky_nav = st.checkbox(
            "Sticky navbar", value=st.session_state.get("sticky_nav", True),
            key="sticky_nav_input"
        )
        st.session_state["position_mode"] = position_mode
        st.session_state["sticky_nav"] = sticky_nav


def my_heading():
    st.title("Streamlit Multi-Page App")
    st.subheader("This is a multi-page app with a native Streamlit navbar.")
    st.markdown("> But only vizualize well with navbar on `top` position")


def login():
    _, col, _ = st.columns([2, 6, 2])
    with col:
        with st.form(key="login_form"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Submit")

        with st.expander("Psst! Here's the login info"):
            st.write(f"Username and Password is:")
            st.markdown(f"""
            ```bash
            {USER}
            ```
            """)

    if submitted:
        if user == USER and password == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.app_id = st.session_state["default_page_id"]
            st.rerun()
        else:
            st.toast("Invalid username or password", icon="❌")


def account():
    st.write("Account page")
    st.caption("This is a protected page. Only logged in users can view this.")


def settings():
    st.button("Theme")


def logout():
    st.session_state.logged_in = False
    st.session_state.app_id = None
    st.session_state.active_app_id = None
    st.rerun()

st.logo(
    image="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.svg",
    icon_image="https://streamlit.io/images/brand/streamlit-mark-color.png"
)

dashboard = st.Page("dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
login_page = st.Page(login, title="Log in", icon=":material/login:")
account_page = st.Page(account, title="Account", icon=":material/account_circle:")
settings_page = st.Page(settings, title="Settings", icon=":material/settings:")
bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
alerts = st.Page("reports/alerts.py", title="System alerts", icon=":material/notification_important:")
search = st.Page("tools/search.py", title="Search", icon=":material/search:")
history = st.Page("tools/history.py", title="History", icon=":material/history:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# HERE IS THE CHANGE
from streamlit_plugins.components.navbar import st_navbar, build_menu_from_st_pages, NavbarPositionType

menu_data, _, menu_account_data, app_map = build_menu_from_st_pages(
    dashboard,
    {
        "name": "Reports", "subpages": [alerts], "icon": ":material/assessment:", "ttip": "Reports"
    },
    {
        "name": "Tools", "subpages": [search, history, bugs], "icon": ":material/extension:"
    },
    login_page=login_page, account_page=account_page, settings_page=settings_page,
    logout_page=logout_page,
)
st.session_state["default_page_id"] = dashboard._script_hash
login_page_id = login_page._script_hash
st.session_state["login_page_id"] = login_page_id
logout_page_id = logout_page._script_hash
st.session_state["logout_page_id"] = logout_page_id

st.session_state["app_map"] = app_map

my_sidebar()

position_mode: NavbarPositionType = st.session_state.get("position_mode", "top")
sticky_nav = st.session_state.get("sticky_nav", True)


page_id = login_page_id
if st.session_state.logged_in:
    # SOME TEXT ABOVE THE NAVBAR
    if position_mode == "top":
        my_heading()
    if st.session_state["app_id"] is None:
        st.session_state["app_id"] = st.session_state["default_page_id"]
    page_id = st_navbar(
        menu_definition=menu_data if st.session_state.logged_in else [],
        login_definition=menu_account_data,
        hide_streamlit_markers=False,
        default_page_selected_id=st.session_state["app_id"] or st.session_state["default_page_id"],
        override_page_selected_id=st.session_state["force_app_id"],
        sticky_nav=sticky_nav,  # at the top or not
        position_mode=position_mode,  # top or subtop
    )
    st.session_state["force_app_id"] = None

    if position_mode != "top":
        my_heading()

if not st.session_state.logged_in and page_id != login_page_id:
    page_id = login_page_id


# Loads the selected app content
st.session_state.app_id = None  # Added to fix login/logout issue
st.session_state.active_app_id = page_id
# app_map[page_id]._can_be_called = True
# app_map[page_id].run()

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "": [dashboard],
            "Account": [account_page, settings_page, logout_page],
            "Reports": [bugs, alerts],
            "Tools": [search, history],
        },
        position="hidden"
    )

else:
    pg = st.navigation([login_page], position="hidden")

if pg._script_hash != page_id:
    st.session_state["app_id"] = page_id
    st.switch_page(app_map[page_id])

pg.run()


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
