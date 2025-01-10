from typing import Literal, Callable

import streamlit as st
import streamlit.components.v1 as components
from streamlit.navigation.page import StreamlitPage
from streamlit.runtime.scriptrunner import get_script_run_ctx

from .config import dev_url, build_path, _RELEASE
from .inject_script import inject_crossorigin_interface, instantiate_crossorigin_interface

if _RELEASE:
    _component_func = components.declare_component("nav_bar", path=str(build_path))
else:
    _component_func = components.declare_component("nav_bar", url=dev_url)

GAP_BETWEEN_COMPS = 1

major, minnor, bug = st.__version__.split('.')
major, minnor, bug = int(major), int(minnor), int(bug)


TOP_SIDE_ELEMENTS_MARGIN = 1.05
TOP_SIDE_ELEMENTS_WIDTH = 4
TOP_LINE_HEIGHT = 0.125
MARGIN_SIDE_NARROW_DIFF = 2
MARGIN_SIDE_NAVBAR = 0.5
SCROLLBAR_WIDTH = 6  # px
HEADER_HEIGHT = 3.75

APP_VIEWER_SELECTOR = ".stAppViewContainer"
COLLAPSE_CONTROLL_CLASS = "collapsedControl"
if major == 1:
    if 36 < minnor <= 37:
        APP_VIEWER_SELECTOR = '[data-testid="stAppViewContainer"]'
        COLLAPSE_CONTROLL_CLASS = "collapsedControl"
    if minnor >= 38:
        APP_VIEWER_SELECTOR = ".stAppViewContainer"
        COLLAPSE_CONTROLL_CLASS = "stSidebarCollapsedControl"

NAV_TOP_UNDER_STYLE = f"""
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"] {{
    height: 3.75rem;
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
iframe[title="{_component_func.name}"] {{
    outline: 1px solid #c3c3c326;
    border-radius: 5px;
    width: 100%;
}}
div:has(> iframe[title="{_component_func.name}"]) {{
    position: sticky;
    opacity: 1 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0;
    margin-top: calc(-1 * {GAP_BETWEEN_COMPS}rem);
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
        border-bottom: 1px solid #c3c3c326;
    }}
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        position: relative;
        z-index: 1000;
        top: 0;
        background-color: var(--background-color);
        /* box-shadow: none !important; */
    }}
    div:has(> iframe[title="{_component_func.name}"]) {{
        z-index: 1000;
    }}
    @media (min-width: 576px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
        }}
    }}
    @media (max-width: 575.98px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
        }}
    }}
    @media (min-width: 768px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
        }}
    }}
"""

UNDER_NAV_STICKY_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) {{
        top: calc({HEADER_HEIGHT}rem + 1rem);
    }}
"""

UNDER_NAV_FIXED_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) {{
        top: calc({HEADER_HEIGHT}rem - 5px);
    }}
"""

NAV_TOP_STYLE = f"""
    #header {{
        background: transparent !important;
    }}
    div:has(> iframe[title="{_component_func.name}"]) {{
        top: {TOP_LINE_HEIGHT}rem;
        z-index: 999990;
        padding: 0;
    }}
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        position: relative;
        top: {TOP_LINE_HEIGHT}rem;
        border-top-right-radius: 0;
        border-top-left-radius: 0;
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"] {{
        border-right: solid 1px #c3c3c380;
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"]:has(> [data-testid="stLogoSpacer"]) {{
        flex-direction: row !important;
    }}
    div:has(> iframe[title="{_component_func.name}"]) + div {{
        margin-top: 2rem;
    }}
    
    /* AJUSTE DEL ANCHO */
    @media (min-width: 576px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - {MARGIN_SIDE_NAVBAR}rem + {SCROLLBAR_WIDTH}px);
        }}
        [data-layout="narrow"] div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - {MARGIN_SIDE_NAVBAR}rem + {SCROLLBAR_WIDTH}px - 2 * {MARGIN_SIDE_NARROW_DIFF}rem);
            left: calc({TOP_SIDE_ELEMENTS_MARGIN}rem + {TOP_SIDE_ELEMENTS_WIDTH}rem);
        }}
        [data-layout="narrow"]:has(> [data-testid="stSidebar"][aria-expanded="true"]) div:has(> iframe[title="{_component_func.name}"]) {{
            left: 0;
        }}
    }}
    @media(max-width: 575.98px) {{
        div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 2*({TOP_SIDE_ELEMENTS_WIDTH}rem + {MARGIN_SIDE_NAVBAR}rem));
            left: calc({TOP_SIDE_ELEMENTS_MARGIN}rem + {TOP_SIDE_ELEMENTS_WIDTH}rem + {MARGIN_SIDE_NAVBAR}rem);
        }}
        [data-layout="narrow"] div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - 2*({TOP_SIDE_ELEMENTS_WIDTH}rem + {MARGIN_SIDE_NAVBAR}rem - {MARGIN_SIDE_NARROW_DIFF}rem));
            left: calc({TOP_SIDE_ELEMENTS_MARGIN}rem + {TOP_SIDE_ELEMENTS_WIDTH}rem + {MARGIN_SIDE_NAVBAR}rem);
        }}
        [data-layout="wide"]:not(:has(> [data-testid="{COLLAPSE_CONTROLL_CLASS}"])) div:has(> iframe[title="{_component_func.name}"]) {{
            width: calc(100% - {TOP_SIDE_ELEMENTS_WIDTH}rem);
            left: 0;
        }}
        [data-layout="narrow"]:not(:has(> [data-testid="{COLLAPSE_CONTROLL_CLASS}"])) div:has(> iframe[title="{_component_func.name}"]) {{
            width: 100%;
            margin-left: calc(-1*({MARGIN_SIDE_NARROW_DIFF}rem));
            left: 0;
        }}
    }}
"""

NAV_TOP_FIXED_STYLE = f"""
"""

NAV_TOP_STICKY_STYLE = f"""
"""

VERTICAL_ST_STYLE = f"""
    header {{
        position: static;
    }}
    @media(max-width: 575px) {{
        body:has( [data-testid="{COLLAPSE_CONTROLL_CLASS}"] > [data-testid="stLogo"]) [data-testid="stHeader"] {{
            height: 5.75rem;
        }}
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"], [data-testid="stToolbar"] {{
        max-width: {TOP_SIDE_ELEMENTS_WIDTH}rem;
        width: {TOP_SIDE_ELEMENTS_WIDTH}rem;
        backdrop-filter: blur(5px);
        max-height: 3rem;
    }}
    [data-testid="stToolbar"] {{
        display: flex;
        flex-direction: column-reverse;
        flex-wrap: nowrap;
        align-items: flex-end;
        border-left: solid 1px #c3c3c380;
        justify-content: flex-end;
        overflow: visible;
        
        /* AJUSTE DEL LATERAL */
        right: calc({TOP_SIDE_ELEMENTS_MARGIN}rem + {SCROLLBAR_WIDTH}px);
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"] {{
        flex-direction: column !important;
        justify-content: flex-start;
        
        /* AJUSTE DEL LATERAL */
        left: {TOP_SIDE_ELEMENTS_MARGIN}rem;
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"]:has([data-testid="stLogoSpacer"]) {{
        flex-direction: column-reverse !important;
    }}
    [data-testid="{COLLAPSE_CONTROLL_CLASS}"] [data-testid="stLogoSpacer"] {{
        display: none;
    }}
    [data-testid="stStatusWidget"] {{
        position: relative;
        right: 0;
        top: 100%;
        margin-top: 1rem;
        backdrop-filter: blur(5px);
        background: radial-gradient(transparent, #dcdcdc2e);
        padding: 0.5em;
        border: 1px solid #dcdcdc2e;
        border-radius: 5px;
    }}
    
    [data-testid="stToolbar"] > [data-testid="stToolbarActions"] {{
        display: flex;
        -webkit-box-align: center;
        align-items: flex-end;
        flex-direction: column;
        flex-wrap: nowrap;
    }}
"""

STICKY_NAV_STYLE = f"""
    div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"],
    iframe[title="{_component_func.name}"] {{
        box-shadow: 0 0px 10px 5px #00000012;
        border-radius: 5px;
    }}
"""

FIXED_NAV_STYLE = f"""
.stMainBlockContainer {{
    padding-top: 3rem;
}}
div:has(> iframe[title="{_component_func.name}"]) {{
    margin-bottom: 1rem;
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

SIDE_NAV_STYLE = f"""
/* Inject COI */
{APP_VIEWER_SELECTOR}, [data-testid="{COLLAPSE_CONTROLL_CLASS}"] {{
    margin-left: 4rem;
    /* transition: margin-left 0.5s ease; */
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"] {{
    height: 100vh !important;
}}
div:has(> iframe[title="{_component_func.name}"]) [data-testid="stSkeleton"], iframe[title="{_component_func.name}"] {{
    outline: 1px solid #c3c3c326;
    border-radius: 5px;
    width: 100%;
    height: 100vh !important;
    box-shadow: 5px 0 10px -5px #00000012;
}}
div:has(> iframe[title="{_component_func.name}"]) {{
    position: sticky;
    opacity: 1 !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0;
    margin-top: calc(-1 * {GAP_BETWEEN_COMPS}rem);
}}
div:has(> iframe[title="{_component_func.name}"]) {{
    position: fixed;
    height: 100vh;
    top: 0;
    margin: 0;
    margin-top: 0.125rem;
    left: 0;
    width: 4rem;
    z-index: 999999;
}}
body.nav-open {APP_VIEWER_SELECTOR},
body.nav-open [data-testid="{COLLAPSE_CONTROLL_CLASS}"] {{
    margin-left: 10rem;
}}
body.nav-open div:has(> iframe[title="{_component_func.name}"]) {{
    width: 10rem;
}}
"""

# TODO: Hay que poner margenes en el iframe para que no ocupe el 100% de ancho si es menor la pantalla a 575

MATERIAL_ICON_HOME = ":material/home:"
MATERIAL_ICON_LOGIN = ":material/login:"
MATERIAL_ICON_LOGOUT = ":material/logout:"
MATERIAL_ICON_USER_CIRCLE = ":material/account_circle:"

DEFAULT_CUSTOM_THEMES = [
    {
        "name": "dark",
        "icon": "brightness_2",
        "themeInfo": {
            "base": 1,
            "primaryColor": "#079E5A",
            "backgroundColor": "#423E2E",
            "secondaryBackgroundColor": "#2D3419", 
            "textColor": "#D7FF94",
            "font": 2,
            # Nuevos parámetros
            "widgetBackgroundColor": "#625625",
            "widgetBorderColor": "#079E5A",
            "skeletonBackgroundColor": "#545B3C",
            "bodyFont": '"Victor Mono Italic", Source Sans Pro, sans-serif',
            "codeFont": '"Victor Mono", Source Code Pro, monospace',
            "fontFaces": [
                {
                    "family": "Inter",
                    "url": "https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
                    "weight": 400
                },
                # Victor Mono Regular (400)
                {
                    "family": "Victor Mono",
                    "url": "https://rubjo.github.io/victor-mono/fonts/VictorMono-Regular.80e21ec6.woff",
                    "weight": 400
                },
                # Victor Mono Italic (400)
                {
                    "family": "Victor Mono Italic", 
                    "url": "https://rubjo.github.io/victor-mono/fonts/VictorMono-Italic.ab9b5a67.woff",
                    "weight": 400,
                }
            ],
            "radii": {
                "checkboxRadius": 3,
                "baseWidgetRadius": 6
            },
            "fontSizes": {
                "tinyFontSize": 10,
                "smallFontSize": 12,
                "baseFontSize": 14
            }
        }
    },
    {
        "name": "light",
        "icon": "wb_sunny",
        "themeInfo": {
            "base": 0,
            "primaryColor": "#00BD00",
            "backgroundColor": "#FDFEFE",
            "secondaryBackgroundColor": "#D2ECCD",
            "textColor": "#050505",
            "font": 0,
            # Nuevos parámetros
            "widgetBackgroundColor": "#FFFFFF",
            "widgetBorderColor": "#D3DAE8",
            "skeletonBackgroundColor": "#CCDDEE",
            "bodyFont": "Inter, Source Sans Pro, sans-serif",
            "codeFont": "Apercu Mono, Source Code Pro, monospace",
            "fontFaces": [
                {
                    "family": "Inter",
                    "url": "https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
                    "weight": 400
                }
            ],
            "radii": {
                "checkboxRadius": 3,
                "baseWidgetRadius": 6
            },
            "fontSizes": {
                "tinyFontSize": 10,
                "smallFontSize": 12,
                "baseFontSize": 14
            }
        }
    }
]

DEFAULT_THEMES = [
    {
        "name": "light",
        "icon": "wb_sunny",
        "themeInfo": {
            "base": 0
        }
    },
    {
        "name": "dark",
        "icon": "brightness_2",
        "themeInfo": {
            "base": 1
        }
    }
]

def build_menu_from_st_pages(
    *pages: StreamlitPage | dict,
    login_app: StreamlitPage = None, logout_callback: Callable = None, account_app: StreamlitPage = None,
    settings_app: StreamlitPage = None
) -> tuple[list[dict], dict, dict[str, StreamlitPage]]:
    if login_app and not logout_callback:
        raise ValueError("You must provide a logout callback if you provide a login app")

    menu = []
    app_map = {}
    for page in pages:
        if isinstance(page, dict):
            name = page["name"]
            sub_pages = page["subpages"]
            icon = page.get("icon", None)
            ttip = page.get("ttip", name)
            submenu, _, sub_app_map = build_menu_from_st_pages(*sub_pages)
            menu.append({
                'id': name.lower().replace(" ", "_"),
                'label': name,
                'submenu': submenu,
                'icon': icon,
                'ttip': ttip,
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

    account_login_definition = {
        'id': "account_menu",
        'label': "Account",
        'icon': MATERIAL_ICON_USER_CIRCLE,
        'ttip': "Account", 'style': {},
        'submenu': []
    }
    if account_app and logout_callback:
        account_login_definition['submenu'].append(
            {'label': "Profile", 'id': "app_account_profile", 'icon': MATERIAL_ICON_USER_CIRCLE, 'ttip': "Profile"},
        )
        app_map["app_account_profile"] = account_app

        if settings_app:
            account_login_definition['submenu'].append(
                {'label': "Settings", 'id': "app_account_settings", 'icon': ":material/settings:", 'ttip': "Settings"}
            )
            app_map["app_account_settings"] = settings_app

    if logout_callback:
        account_login_definition['submenu'].append(
            {'label': "Logout", 'id': "app_logout", 'icon': MATERIAL_ICON_LOGOUT, 'ttip': "Logout"}
        )
        app_map["app_logout"] = st.Page(logout_callback, title="Log out", icon=MATERIAL_ICON_LOGOUT)

    return menu, account_login_definition, app_map


def st_navbar(
    menu_definition: list[dict], first_select=0, home_name=None, login_name=None,
    override_theme=None, sticky_nav=True, hide_streamlit_markers=True,
    position_mode: Literal["top", "under", "side"] = 'under',
    force_value=None,
    option_menu=False,
    default_app_selected_id=None,
    override_app_selected_id=None,
    reclick_load=True,
    input_styles: str = None,
    themes_data: list[dict] = None,
    key="NavBarComponent",
):
    if themes_data is None:
        themes_data = DEFAULT_THEMES

    # https://github.com/SnpM/streamlit-scroll-navigation
    inject_crossorigin_interface()
    instantiate_crossorigin_interface(key)

    ctx = get_script_run_ctx(suppress_warning=True)

    # first_select = math.floor(first_select / 10)

    override_theme = override_theme or {
        "menu_background": "var(--background-color)",
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
    style = NAV_TOP_UNDER_STYLE

    if position_mode == 'under':
        style += UNDER_NAV_STYLE
        if sticky_nav:
            style += UNDER_NAV_STICKY_STYLE
        else:
            style += UNDER_NAV_FIXED_STYLE
    elif position_mode == 'top':
        style += NAV_TOP_STYLE
        style += VERTICAL_ST_STYLE
        if sticky_nav:
            style += NAV_TOP_STICKY_STYLE
        else:
            style += NAV_TOP_FIXED_STYLE
    elif position_mode == 'side':
        style += SIDE_NAV_STYLE

    if position_mode in ['top', 'under']:
        if sticky_nav:
            style += STICKY_NAV_STYLE
            if position_mode == 'top':
                style += NAV_TOP_STICKY_STYLE
        else:
            style += FIXED_NAV_STYLE

    if hide_streamlit_markers:
        style += HIDE_ST_STYLE

    input_styles = input_styles or ""
    st.markdown(f"<style>\n{input_styles}\n{style}\n<style>", unsafe_allow_html=True)
    component_value = _component_func(
        menu_definition=menu_definition, home=home_data, login=login_data,
        override_theme=override_theme,
        position_mode=position_mode,
        default_app_selected_id=default_app_selected_id,
        override_app_selected_id=override_app_selected_id,
        reclick_load=reclick_load,
        key=key, fvalue=force_value,
        themes_data=themes_data,
        default=default_app_selected_id,
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
