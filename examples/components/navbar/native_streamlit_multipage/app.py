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

USER = "admin"
PASSWORD = "admin"

positions = ["top", "under", "side"]

def my_sidebar():
    with st.sidebar:
        st.write("Logged in:", st.session_state.logged_in)
        position_mode = st.radio(
            "Navbar position mode",
            positions,
            index=positions.index(st.session_state.get("position_mode", "top")),
            key="position_mode_input",
        )
        sticky_nav = st.checkbox(
            "Sticky navbar",
            value=st.session_state.get("sticky_nav", True),
            key="sticky_nav_input"
        )
        native_way = st.checkbox(
            "Use native way",
            value=st.session_state.get("native_way", False),
            key="native_way_input"
        )
        st.session_state["position_mode"] = position_mode
        st.session_state["sticky_nav"] = sticky_nav
        st.session_state["native_way"] = native_way


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
            st_switch_home()
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

dashboard = st.Page("dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True, url_path="dashboard")
login_page = st.Page(login, title="Log in", icon=":material/login:", url_path="login")
account_page = st.Page(account, title="Account", icon=":material/account_circle:", url_path="account")
settings_page = st.Page(settings, title="Settings", icon=":material/settings:", url_path="settings")
bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:", url_path="bugs")
bugs2 = st.Page("reports/bugs.py", title="Bug reports2", icon=":material/bug_report:", url_path="bugs2")
bugs3 = st.Page("reports/bugs.py", title="Bug reports3", icon=":material/bug_report:", url_path="bugs3")
alerts = st.Page("reports/alerts.py", title="System alerts", icon=":material/notification_important:", url_path="alerts")
search = st.Page("tools/search.py", title="Search", icon=":material/search:", url_path="search")
history = st.Page("tools/history.py", title="History", icon=":material/history:", url_path="history")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:", url_path="logout")

# HERE IS THE CHANGE
from streamlit_plugins.components.navbar import st_navbar, build_menu_from_st_pages, NavbarPositionType, st_navigation, st_switch_home

my_sidebar()

position_mode: NavbarPositionType = st.session_state.get("position_mode", "top")
sticky_nav = st.session_state.get("sticky_nav", True)
native_way = st.session_state.get("native_way", False)

if st.session_state.logged_in:
    if position_mode == "top":
            my_heading()
    
page = st_navigation(
    {
        "": [dashboard],
        "Reports": [alerts],
        "Tools": [search, history, bugs, bugs2, bugs3]
    },
    section_info={
        "Reports": {"icon": ":material/assessment:"},
        "Tools": {"icon": ":material/extension:"}
    },
    position_mode=position_mode if st.session_state.logged_in else "hidden", sticky_nav=sticky_nav,
    login_page=login_page, logout_page=logout_page,
    account_page=account_page,
    settings_page=settings_page,
    native_way=native_way
)

if st.session_state.logged_in:
    # SOME TEXT ABOVE THE NAVBAR
    page.run()

else:
    login_page._can_be_called = True
    login_page.run()