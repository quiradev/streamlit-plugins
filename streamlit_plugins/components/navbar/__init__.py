import os
from typing import Literal

import streamlit as st
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

GAP_BETWEEN_COMPS = "1rem"

NAV_STYLE = f"""
header[data-testid="stHeader"] {{
    margin-right: 6px;
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"] {{
    height: 3.75rem;
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
iframe[title="{_component_func.name}"] {{
    # box-sizing: content-box;
    # border: 1px solid #9e9e9e;
    outline: 1px solid #c3c3c380;
    border-radius: 5px;
    width: 100%;
}}
div:has(> iframe[title="{_component_func.name}"]) {{
    opacity: 1 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 2.5rem;
}}
"""

UNDER_NAV_STYLE = f"""
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
        border-bottom: 1px solid #c3c3c380;
    }}
    div:has(> iframe[title="{_component_func.name}"]) {{
        position: fixed;
        z-index: 1000;
        top: calc(3.75rem - 0.125rem);
        padding: 0;
        margin-top: calc((-1 * {GAP_BETWEEN_COMPS}));
    }}
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        position: relative;
        z-index: 1000;
        top: 0;
        background-color: var(--background-color);
        /* box-shadow: none !important; */
    }}
    @media (min-width: 576px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% + 10rem + 1rem - 1px);
            margin-left: -5.5rem;
            padding: 0 1.5rem;
        }}
    }}
    @media (max-width: 575px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100vw + 1rem - 7px);
            margin-left: -1.5rem;
            padding: 0 1.5rem;
        }}
    }}
    @media (min-width: 768px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            position: sticky !important;
            width: calc(100% + 8rem + 1rem - 1px);
            margin-top: calc(-3rem + (-1 * {GAP_BETWEEN_COMPS}));
            margin-left: -4.5rem;
            padding: 0 0.5rem;
        }}
    }}
"""

UNDER_NAV_STICKY_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) ~ div {{
        top: 2rem;
    }}
"""

UNDER_NAV_FIXED_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) ~ div {{
        top: 4rem;
    }}
"""

NAV_TOP_STYLE = f"""
    #header {{
        background: transparent !important;
    }}
    div:has(> iframe[title="{_component_func.name}"]) {{
        top: 0rem;
        z-index: 999990;
        padding: 0;
        margin-top: calc((-1 * {GAP_BETWEEN_COMPS}));
    }}
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        position: relative;
        top: 0.125rem;
        border-top-right-radius: 0;
        border-top-left-radius: 0;
    }}
    [data-testid="collapsedControl"] {{
        /* flex-direction: column !important; */
        border-right: solid 1px #c3c3c380;
    }}
    [data-testid="collapsedControl"]:has(> [data-testid="stLogoSpacer"]) {{
        flex-direction: row !important;
    }}
"""

NAV_TOP_FIXED_LOGO_MARGIN = "0.7125em"
NAV_TOP_FIXED_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) {{
        /* width: calc(100% - 6rem); */
        /* left: 4.25rem; */
    }}
    @media (max-width: 768px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 8rem);
            left: 4.5rem;
        }}
    }}
    @media(max-width: 575px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 5em);
            left: 0;
        }}
        body:has([data-testid="collapsedControl"] > img) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 11rem);
            left: 7.5rem;
        }}
        body:has([data-testid="collapsedControl"] > img:last-child) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 9rem);
            left: 5.125rem;
        }}
        body:has([data-testid="collapsedControl"] > [data-testid="stLogoSpacer"]) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 7.75rem);
            left: 4.125rem;
        }}
    }}
    @media (min-width: 576px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
            padding: 0;
            margin-left: calc(-0.5rem - 0.5em);
        }}
        body:has([data-testid="collapsedControl"] > img:last-child) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 1.25em);
            margin-left: calc(-0.5rem + 0.75em);
        }}
        body:has([data-testid="collapsedControl"] > img) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 3em);
            margin-left: calc(-0.5rem + 3em);
        }}
        body:has([data-testid="collapsedControl"] > [data-testid="stLogoSpacer"]) div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
            margin-left: calc(-0.5rem - 0.125em);
        }}
    }}
    div:has(> iframe[title="{_component_func.name}"]) ~ div {{
        top: 4rem;
    }}
"""

NAV_TOP_STICKY_LOGO_MARGIN = "1.25em"
NAV_TOP_STICKY_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) {{
        width: calc(100% - 8.5rem);
        left: calc(4.25rem + {NAV_TOP_STICKY_LOGO_MARGIN});
    }}
    @media (min-width: 576px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - {NAV_TOP_STICKY_LOGO_MARGIN});
            margin-left: -4.25rem;
            padding: 0;
        }}
        body:has([data-testid="collapsedControl"] > img:last-child) div:has(> iframe[title="{_component_func.name}"]) {{
           width: calc(100% - 2em);
           left: 4.25em;
        }}
        body:has([data-testid="collapsedControl"] > img) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 3.5em);
            left: 7.5em;
        }}
        body:has([data-testid="collapsedControl"] > [data-testid="stLogoSpacer"]) div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
            left: 4.25rem;
        }}
    }}
    @media(max-width: 575px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 5rem);
            left: 0;
        }}
        body:has([data-testid="collapsedControl"] > img:last-child) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 9.215em);
            left: 5.25rem;
        }}
        body:has([data-testid="collapsedControl"] > img) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 11em);
            left: 7.5rem;
        }}
        body:has([data-testid="collapsedControl"] > [data-testid="stLogoSpacer"]) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 8rem);
            left: 4.25rem;
        }}
    }}
    div:has(> iframe[title="{_component_func.name}"]) ~ div {{
        top: 2rem;
    }}
"""

VERTICAL_ST_STYLE = """
    header {
        position: static;
    }
    
    [data-testid="stToolbar"] {
        display: flex;
        flex-direction: column-reverse;
        flex-wrap: nowrap;
        align-items: flex-end;
        border-left: solid 1px #c3c3c380;
    }
    
    [data-testid="stStatusWidget"] {
        position: absolute;
        right: 0;
        top: 100%;
        margin-top: 1rem;
        backdrop-filter: blur(5px);
        background: radial-gradient(transparent, #dcdcdc2e);
        padding: 0.5em;
        border: 1px solid #dcdcdc2e;
        border-radius: 5px;
    }
    
    [data-testid="stToolbar"] > [data-testid="stToolbarActions"] {
        display: flex;
        -webkit-box-align: center;
        align-items: flex-end;
        flex-direction: column;
        flex-wrap: nowrap;
    }
"""

STICKY_NAV_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) {{
        position: sticky;
        padding-top: 0.5rem !important;
    }}
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        box-shadow: 0 0px 10px 5px #00000012;
        border-radius: 5px;
    }}
"""
FIXED_NAV_STYLE = f"""
div:has(> iframe[title="{_component_func.name}"]) {{
    position: sticky; /* Fixed with custom width */
    margin-top: calc(-6rem + (-1 * {GAP_BETWEEN_COMPS}));
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
iframe[title="{_component_func.name}"] {{
    border-top-right-radius: 0;
    border-top-left-radius: 0;
}}
"""

HIDE_ST_STYLE = """
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
"""

# TODO: Hay que poner margenes en el iframe para que no ocupe el 100% de ancho si es menor la pantalla a 575

MATERIAL_ICON_HOME = ":material/home:"
MATERIAL_ICON_LOGIN = ":material/login:"
MATERIAL_ICON_LOGOUT = ":material/logout:"
MATERIAL_ICON_USER_CIRCLE = ":material/account_circle:"


def build_menu_from_st_pages(*pages: StreamlitPage | dict, login_app: StreamlitPage = None,
                             logout_app: StreamlitPage = None) -> tuple[list[dict], dict[str, StreamlitPage]]:
    menu = []
    app_map = {}
    for page in pages:
        if isinstance(page, dict):
            for label, sub_pages in page.items():
                submenu, sub_app_map = build_menu_from_st_pages(*sub_pages)
                menu.append({
                    'id': label.lower().replace(" ", "_"),
                    'label': label,
                    'submenu': submenu
                })
                app_map.update(sub_app_map)
        elif isinstance(page, StreamlitPage):
            app_id = page.url_path
            if not app_id:
                app_id = "app_default"
            menu.append({'label': page.title, 'id': app_id, 'icon': page.icon, 'ttip': page.title, 'style': {}})
            app_map[app_id] = page
        else:
            raise ValueError(f"Invalid page type: {type(page)}")

    if login_app:
        app_map["app_login"] = login_app

    if logout_app:
        app_map["app_logout"] = logout_app

    return menu, app_map


def st_navbar(
    menu_definition: list[dict], first_select=0, key="NavBarComponent", home_name=None, login_name=None,
    override_theme=None, sticky_nav=True, hide_streamlit_markers=True,
    position_mode: Literal["top", "under"] = 'under',
    force_value=None, use_animation=True,
    option_menu=False,
    default_app_selected_id=None,
    override_app_selected_id=None,
    reclick_load=True
):
    # if key not in st.session_state:
    #     st.session_state[key] = None

    # first_select = math.floor(first_select / 10)

    override_theme = override_theme or {
        "menu_background": "var(--background-color)",
        # "menu_background": "transparent",
        "txc_inactive": "var(--text-color)",
        "txc_active": "var(--text-color)",
        "option_active": "var(--primary-color)",
    }

    if type(home_name) is str:
        home_data = {'id': "app_home", 'label': home_name, 'icon': MATERIAL_ICON_HOME, 'ttip': home_name}
    else:
        home_data = home_name
        if home_name is not None:
            if home_name.get('icon', None) is None:
                home_data['icon'] = MATERIAL_ICON_HOME

    if type(login_name) is str:
        login_data = {'id': "app_login", 'label': login_name, 'icon': MATERIAL_ICON_USER_CIRCLE, 'ttip': login_name}
    else:
        login_data = login_name
        if login_name is not None:
            if login_name.get('icon', None) is None:
                login_data['icon'] = MATERIAL_ICON_USER_CIRCLE

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
                menu_definition[i]['submenu'][_i]['label'] = menu_definition[i]['submenu'][_i].get(
                    'label', f'{i}_Label_{_i}'
                )
                menu_definition[i]['submenu'][_i]['id'] = menu_definition[i]['submenu'][_i].get(
                    'id', f"app_{menu_definition[i]['submenu'][_i]['label']}"
                )

    if default_app_selected_id is None:
        items = menu_definition
        if home_name is not None:
            items = [home_data] + items
        if login_name is not None:
            items = items + [login_data]
        first_select_item = items[first_select]
        default_app_selected_id = first_select_item.get('id', None)
        if first_select_item.get('submenu', []):
            default_app_selected_id = first_select_item['submenu'][0].get('id', None)

    if override_app_selected_id:
        default_app_selected_id = override_app_selected_id

    # if key not in st.session_state:
    #     override_app_selected_id = default_app_selected_id
    # elif st.session_state[key] is None:
    #     override_app_selected_id = default_app_selected_id

    # print()
    # print(f"FROM Override Multi: {override_app_selected_id}")
    style = NAV_STYLE

    if position_mode == 'under':
        style += UNDER_NAV_STYLE
        if sticky_nav:
            style += UNDER_NAV_STICKY_STYLE
        else:
            style += UNDER_NAV_FIXED_STYLE
    else:
        style += NAV_TOP_STYLE
        style += VERTICAL_ST_STYLE
        if sticky_nav:
            style += NAV_TOP_STICKY_STYLE
        else:
            style += NAV_TOP_FIXED_STYLE

    if sticky_nav:
        style += STICKY_NAV_STYLE
        if position_mode == 'top':
            style += NAV_TOP_STICKY_STYLE
    else:
        style += FIXED_NAV_STYLE

    if hide_streamlit_markers:
        style += HIDE_ST_STYLE

    st.markdown(f"<style>\n{style}\n<style>", unsafe_allow_html=True)
    component_value = _component_func(
        menu_definition=menu_definition, key=key, home=home_data, fvalue=force_value,
        login=login_data, override_theme=override_theme, use_animation=use_animation,
        override_app_selected_id=override_app_selected_id,
        default=default_app_selected_id, default_app_selected_id=default_app_selected_id,
        reclick_load=reclick_load
    )
    # print(f"FROM Navbar: {component_value}")

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
