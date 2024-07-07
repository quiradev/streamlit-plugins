# streamlit-plugins
Components and Frameworks to give new features to streamlit

![Demo Multipage with Navbar](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/demo1.gif)

## Frameworks
### Multilit (Inherit from Hydralit)
This is a fork of [Hydralit](https://github.com/TangleSpace/hydralit).

In this version, I update all the code to be compatible with the last version of streamlit.
And it improves the interface to be more user-friendly. Also, it respects the strealit active theme and can be override by the user.
In a future is planned to incorporate the new multipage native of streamlit. Instead of the current implementation.

Can use built-in buttons to change the page, or use a function to change the page programmatically.
![Change Page with button](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/demo2.gif)

## Components
The Navbar and Loader component are inherited from Hydralit components, only to give support to the multilit framework.
But this version has improve the interface and loaders to be more user-friendly.

### Navbar (Inherit from Hydralit Components)
Component to use when you want to have a navbar in your streamlit app.
It can be used with native multipage streamlit, or use the multilit framework.

If you want to use the native multipage streamlit, you can use the `st_navbar` function to create the navbar.

This component it returns the id of the defined menu that has to run the page.

This is an example of multipage with native streamlit
```python
import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
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

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Reports": [dashboard, bugs, alerts],
            "Tools": [search, history],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()
```

And if you want to use streamlit Navbar, it has to be addapted to this code:
```python
import streamlit as st

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

app_id = st_navbar(
    menu_definition=menu_data if st.session_state.logged_in else [],
    login_name=logout_page.title if st.session_state.logged_in else login_page.title,
    hide_streamlit_markers=False,
    override_app_selected_id=st.session_state.app_id,
    sticky_nav=True,  # at the top or not
    sticky_mode='pinned',  # sticky or pinned
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
```

### Loader (Inherit from Hydralit Components)

### AnnotatedText (Inspired from SpaCy Anotated Text)

### LabelStudio (Developing)
LabelStudio adapter for NERs into streamlit

### SnakeViz
Interface in streamlit to measue bottlenecks in yout code