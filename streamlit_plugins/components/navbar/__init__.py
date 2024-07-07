import os
import streamlit as st
import math
import streamlit.components.v1 as components
from streamlit.navigation.page import StreamlitPage

# _RELEASE = os.getenv("RELEASE", "").upper() != "DEV"
_RELEASE = True
# _RELEASE = False

if _RELEASE:
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(absolute_path, "frontend", "build")
    _component_func = components.declare_component("nav_bar", path=build_path)
else:
    _component_func = components.declare_component("nav_bar", url="http://localhost:3000")

PINNED_NAV_STYLE = f"""
                    <style>
                    .reportview-container .sidebar-content {{
                        padding-top: 0rem;
                    }}
                    .reportview-container .main .block-container {{
                        padding-top: 0rem;
                        padding-right: 4rem;
                        padding-left: 4rem;
                        padding-bottom: 4rem;
                    }}
                    .stApp > header {{
                        border-bottom: 1px solid #9e9e9e;
                    }}
                    iframe[title="{_component_func.name}"] {{
                        position: fixed;
                        z-index: 1000;
                        box-sizing: content-box;
                        top: calc(3.75rem - 0.75rem);
                        border: 2px solid #ff4b56;
                        border: 1px solid #9e9e9e;
                        border-radius: 5px;
                    }}
                    </style>
                """

STICKY_NAV_STYLE = f"""
                    <style>
                    div[data-stale="false"] > iframe[title="{_component_func.name}"] {{
                        position: fixed;
                        z-index: 99;
                        box-sizing: border-box;
                        top: 0;
                    }}
                    </style>
                """

HIDE_ST_STYLE = """
                    <style>
                    div[data-testid="stToolbar"] {
                    display: none;
                    position: none;
                    }

                    div[data-testid="stDecoration"] {
                    display: none;
                    position: none;
                    }

                    div[data-testid="stStatusWidget"] {
                    display: none;
                    position: none;
                    }

                    #MainMenu {
                    display: none;
                    }
                    header {
                    display: none;
                    }

                    </style>
                """


def build_menu_from_st_pages(*pages: StreamlitPage | dict, login_app: StreamlitPage = None,
                             logout_app: StreamlitPage = None) -> tuple[list[dict], dict[str, StreamlitPage]]:
    menu = []
    app_map = {}
    for page in pages:
        if isinstance(page, dict):
            for label, sub_pages in page.items():
                submenu, sub_app_map = build_menu_from_st_pages(*sub_pages)
                menu.append({'id': label.lower().replace(" ", "_"), 'label': label, 'submenu': submenu})
                app_map.update(sub_app_map)
        elif isinstance(page, StreamlitPage):
            app_id = page.url_path
            if not app_id:
                app_id = "app_default"
            menu.append({'label': page.title, 'id': app_id})
            app_map[app_id] = page
        else:
            raise ValueError(f"Invalid page type: {type(page)}")

    if login_app:
        app_map["app_login"] = login_app

    if logout_app:
        app_map["app_logout"] = logout_app

    return menu, app_map


def st_navbar(menu_definition: list[dict], first_select=0, key="NavBarComponent", home_name=None, login_name=None,
              override_theme=None, sticky_nav=True, force_value=None, use_animation=True,
              hide_streamlit_markers=True, sticky_mode='pinned', option_menu=False, override_app_selected_id=None,
              reclick_load=True):
    # if key not in st.session_state:
    #     st.session_state[key] = None

    # first_select = math.floor(first_select / 10)

    if type(home_name) is str:
        home_data = {'id': "app_home", 'label': home_name, 'icon': "fa fa-home", 'ttip': home_name}
    else:
        home_data = home_name
        if home_name is not None:
            if home_name.get('icon', None) is None:
                home_data['icon'] = "fa fa-home"

    if type(login_name) is str:
        login_data = {'id': "app_login", 'label': login_name, 'icon': "fa fa-user-circle", 'ttip': login_name}
    else:
        login_data = login_name
        if login_name is not None:
            if login_name.get('icon', None) is None:
                login_data['icon'] = "fa fa-user-circle"

    if option_menu:
        max_len = 0
        for mitem in menu_definition:
            label_len = len(mitem.get('label', ''))
            if label_len > max_len:
                max_len = label_len

        for i, mitem in enumerate(menu_definition):
            menu_definition[i]['label'] = f"{mitem.get('label', ''):^{max_len + 10}}"

    for i, mitem in enumerate(menu_definition):
        menu_definition[i]['label'] = menu_definition[i].get('label', f'Label_{i}')
        menu_definition[i]['id'] = menu_definition[i].get('id', f"app_{menu_definition[i]['label']}")
        if 'submenu' in menu_definition[i]:
            for _i, _msubitem in enumerate(menu_definition[i]['submenu']):
                menu_definition[i]['submenu'][_i]['label'] = menu_definition[i]['submenu'][_i].get('label',
                                                                                                   f'{i}_Label_{_i}')
                menu_definition[i]['submenu'][_i]['id'] = menu_definition[i]['submenu'][_i].get('id',
                                                                                                f"app_{menu_definition[i]['submenu'][_i]['label']}")

    items = menu_definition
    if home_name is not None:
        items = [home_data] + items
    if login_name is not None:
        items = items + [login_data]
    first_select_item = items[first_select]
    default_app_selected_id = first_select_item.get('id', None)
    if first_select_item.get('submenu', []):
        default_app_selected_id = first_select_item['submenu'][0].get('id', None)

    if key not in st.session_state:
        override_app_selected_id = default_app_selected_id
    elif st.session_state[key] is None:
        override_app_selected_id = default_app_selected_id

    # print()
    # print(f"FROM Multi: {override_app_selected_id}")
    component_value = _component_func(
        menu_definition=menu_definition, key=key, home=home_data, fvalue=force_value,
        login=login_data, override_theme=override_theme, use_animation=use_animation,
        override_app_selected_id=override_app_selected_id,
        default=default_app_selected_id, default_app_selected_id=default_app_selected_id,
        reclick_load=reclick_load
    )
    # print(f"FROM Navbar: {component_value}")

    if sticky_nav:
        if sticky_mode == 'pinned':
            st.markdown(PINNED_NAV_STYLE, unsafe_allow_html=True)
        else:
            st.markdown(STICKY_NAV_STYLE, unsafe_allow_html=True)

    if hide_streamlit_markers:
        st.markdown(HIDE_ST_STYLE, unsafe_allow_html=True)

    if component_value is None:
        component_value = default_app_selected_id
        # from streamlit.runtime.state import get_session_state
        # session_state = get_session_state()
        # widget_key = session_state._state._key_id_mapping[key]
        # session_state._state[widget_key] = component_value
        # session_state._state._old_state[widget_key] = component_value

    if override_app_selected_id:
        component_value = override_app_selected_id
        # from streamlit.runtime.state import get_session_state
        # session_state = get_session_state()
        # widget_key = session_state._state._key_id_mapping[key]
        # session_state._state[widget_key] = component_value
        # session_state._state._old_state[widget_key] = component_value

    # print(f"FROM Navbar FINAL: {component_value}")
    # print()
    return component_value
