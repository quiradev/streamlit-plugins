import inspect
import logging
import warnings
from pathlib import Path
from typing import Literal, Optional, cast
from urllib.parse import urlparse

import streamlit as st
from streamlit.components import v2
from streamlit.components.v2.types import ComponentRenderer
from streamlit.navigation.page import StreamlitPage

from streamlit_plugins.components.navbar.v2.utils import add_trusted_url

# ---------------------------------------------------------------------------
# CSS: se leen los archivos y se pasan al componente vía parámetro `css`
# ---------------------------------------------------------------------------
_CSS_DIR = Path(__file__).parent / "frontend" / "public"

def _load_css() -> str:
    # Solo cargar CSS específico del componente (no bootstrap ni material-fonts,
    # que se importan como paquetes npm en index.tsx)
    css_parts = []
    for css_file in ["style.css", "st-styles.css"]:
        path = _CSS_DIR / css_file
        if path.exists():
            css_parts.append(path.read_text())
    return "\n".join(css_parts)

_component: ComponentRenderer = st.components.v2.component(
    "streamlit-component-navbar.nav_bar",
    js="index-*.js",
    html='<div class="react-root"></div>',
    css=_load_css(),
    isolate_styles=False
)

logger = logging.getLogger(__name__)

NavbarPositionType = Literal["top", "under", "side", "static", "hidden"]

NAVIGATION_KEY_PREFIX = "__navigation"
NAVBAR_KEY_PREFIX = "__navbar"
NAVIGATION_COMPONENT_KEY = "navigation-component"

add_trusted_url("http://localhost")


MATERIAL_ICON_HOME = ":material/home:"
MATERIAL_ICON_LOGIN = ":material/login:"
MATERIAL_ICON_LOGOUT = ":material/logout:"
MATERIAL_ICON_SETTINGS = ":material/settings:"
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
                {
                    "family": "Victor Mono",
                    "url": "https://rubjo.github.io/victor-mono/fonts/VictorMono-Regular.80e21ec6.woff",
                    "weight": 400
                },
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
    home_page: StreamlitPage | None = None,
    login_page: StreamlitPage | None = None, logout_page: StreamlitPage | None = None,
    account_page: StreamlitPage | None = None,
    settings_page: StreamlitPage | None = None
) -> tuple[list[dict], dict, dict, dict[str, StreamlitPage]]:
    if login_page and not logout_page:
        raise ValueError("You must provide a logout page if you provide a login page")

    menu = []
    page_map = {}
    home_definition = {}
    account_login_definition = {}
    for page in pages:
        if isinstance(page, dict):
            section = page["name"]
            sub_pages = page["subpages"]
            icon = page.get("icon", None)
            ttip = page.get("ttip", section)
            submenu, sub_home_def, _, sub_app_map = build_menu_from_st_pages(*sub_pages)
            menu.append({
                'id': section.lower().replace(" ", "_"),
                'label': section,
                'submenu': submenu,
                'icon': icon,
                'ttip': ttip
            })
            page_map.update(sub_app_map)
            # home_definition = sub_home_def

        elif isinstance(page, StreamlitPage):
            page_id = page._script_hash
            menu.append({
                'label': page.title, 'id': page_id,
                'icon': page.icon, 'ttip': page.title, 'style': {},
                'url': page._url_path,
                'is_page': True
            })
            page_map[page_id] = page
        else:
            raise ValueError(f"Invalid page type: {type(page)}")

    if home_page:
        home_definition = {
            'id': home_page._script_hash,
            'label': home_page.title or "Home",
            'icon': home_page.icon or MATERIAL_ICON_HOME,
            'ttip': home_page.title or "Home",
            'url': home_page._url_path
        }
        page_map[home_page._script_hash] = home_page

    if login_page:
        page_map[login_page._script_hash] = login_page

    if settings_page or account_page or logout_page:
        account_login_definition = {
            'id': "account_menu",
            'label': "Account",
            'icon': MATERIAL_ICON_USER_CIRCLE,
            'ttip': "Account", 'style': {},
            'submenu': []
        }
        if account_page:
            account_login_definition['submenu'].append(
                {
                    'id': account_page._script_hash,
                    'label': account_page.title or "Profile",
                    'icon': account_page.icon or MATERIAL_ICON_USER_CIRCLE,
                    'ttip': account_page.title or "Profile",
                    'url': account_page._url_path
                },
            )
            page_map[account_page._script_hash] = account_page

        if settings_page:
            account_login_definition['submenu'].append(
                {
                    'id': settings_page._script_hash,
                    'label': settings_page.title or "Settings",
                    'icon': settings_page.icon or MATERIAL_ICON_SETTINGS,
                    'ttip': settings_page.title or "Settings",
                    'url': settings_page._url_path
                }
            )
            page_map[settings_page._script_hash] = settings_page

        if logout_page:
            account_login_definition['submenu'].append(
                {
                    'id': logout_page._script_hash,
                    'label': logout_page.title or "Logout",
                    'icon': logout_page.icon or MATERIAL_ICON_LOGOUT,
                    'ttip': logout_page.title or"Logout",
                    'url': logout_page._url_path
                }
            )
            page_map[logout_page._script_hash] = logout_page

    return menu, home_definition, account_login_definition, page_map

def get_page_id_by_url_path(pages_map: dict[str, StreamlitPage], url: str, prefix_url: str = "") -> str | None:
    # Elimina el prefijo si existe
    url_path = urlparse(url).path
    url_path = url_path.strip("/")
    prefix_url = prefix_url.strip("/")
    if prefix_url and url_path.startswith(prefix_url):
        url_path = url_path[len(prefix_url):]

    for page_id, page in pages_map.items():
        if getattr(page, "_default", False) and url_path == "":
            return page_id
        if getattr(page, "url_path", None) == url_path:
            return page_id
    return None

def st_navbar(
    menu_definition: list[dict], first_select=0, home_definition: dict | None = None, login_definition: dict | None = None,
    override_theme=None, hide_streamlit_markers=True,
    position_mode: NavbarPositionType = 'static', sticky_nav=False,
    force_value=None,
    option_menu=False,
    default_page_selected_id=None,
    override_page_selected_id=None,
    override_first_page_load_id=None,
    reclick_load=True,
    themes_data: list[dict]| None = None,
    theme_changer: bool = False,
    hide_skeleton: bool = False,
    collapsible: bool = True,
    prefix_url: str = "",
    # url_navigation: bool = False,
    key="NavBarComponent",
) -> str:
    if home_definition is None:
        home_definition = menu_definition.pop(0)

    is_navigation = False
    # se recupera del callstack si se ha llamado desde la anterior funcion desde st_navigation
    inspect_stack = inspect.stack()
    if len(inspect_stack) > 2:
        caller = inspect_stack[1]
        if caller.function == 'st_navigation' and caller.filename == __file__:
            is_navigation = True
    
    if not is_navigation:
        if position_mode != "static":
            raise ValueError("The position_mode parameter can only be 'static' when calling st_navbar directly")
        if sticky_nav:
            # Mostrar un warning de python de que no tendra efecto
            warnings.warn("The sticky_nav parameter will have no effect when calling st_navbar directly")

    if is_navigation:
        if themes_data is None and theme_changer:
            themes_data = DEFAULT_THEMES
        elif not theme_changer:
            themes_data = []
    else:
        theme_changer = False

    navbar_view = st.container(key=f"{NAVBAR_KEY_PREFIX}_{key}_container_navbar")

    override_theme = override_theme or {
        "menu_background": "var(--background-color)",
        "txc_inactive": "var(--text-color)",
        "txc_active": "var(--text-color)",
        "option_active": "var(--primary-color)",
    }

    home_data = None
    if home_definition and home_definition is not None:
        home_data = home_definition
        home_data['icon'] = home_definition.get('icon', MATERIAL_ICON_HOME)

    login_data = None
    if login_definition and login_definition is not None:
        login_data = login_definition
        login_data['icon'] = login_definition.get('icon', MATERIAL_ICON_USER_CIRCLE)

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

    if default_page_selected_id is None:
        items = menu_definition
        if home_definition is not None:
            items = [home_data] + items
        if login_definition is not None:
            items = items + [login_data]
        
        first_select_item = items[first_select] or {}
        default_page_selected_id = first_select_item.get('id', None)
        if first_select_item.get('submenu', []):
            default_page_selected_id = first_select_item['submenu'][0].get('id', None)

    if override_page_selected_id:
        default_page_selected_id = override_page_selected_id

    with navbar_view:
        component_result = _component(
            key=key,
            data=dict(
                menu_definition=menu_definition, home=home_data or None, login=login_data or None,
                override_theme=override_theme,
                position_mode=position_mode, is_sticky=sticky_nav,
                default_page_selected_id=default_page_selected_id,
                override_page_selected_id=override_page_selected_id,
                override_first_page_load_id=override_first_page_load_id,
                reclick_load=reclick_load,
                is_navigation=is_navigation,
                themes_data=themes_data,
                theme_changer=theme_changer,
                collapsible=collapsible,
                prefix_url=prefix_url,
                # url_navigation=url_navigation and is_navigation,
                is_visible=True,
                fvalue=force_value,

            ),
        )
        print(component_result)
        component_value = component_result.get('value', None) if component_result else None

    if component_value is None:
        if not is_navigation:
            component_value = default_page_selected_id
        else:
            component_value = override_first_page_load_id or default_page_selected_id

    if override_page_selected_id:
        component_value = override_page_selected_id

    return cast(str, component_value)

def st_which_page() -> str:
    return st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_id"]

def st_navigation(
    pages: list[StreamlitPage] | dict[str, list[StreamlitPage]],
    section_info: dict[str, dict[str, str]] | None = None,
    position_mode: NavbarPositionType = 'side', sticky_nav=True,
    login_page: StreamlitPage | None = None,
    logout_page: StreamlitPage | None = None,
    account_page: StreamlitPage | None = None,
    settings_page: StreamlitPage | None = None,
    native_way=False, # url_navigation=False,
    themes_data: list[dict]| None = None,
    theme_changer: bool = True,
    prefix_url: str = ""
) -> StreamlitPage:
    prev_url_page_id_key = f"{NAVIGATION_KEY_PREFIX}_prev_url_page_id"
    prev_page_id_key = f"{NAVIGATION_KEY_PREFIX}_prev_page_id"
    page_id_key = f"{NAVIGATION_KEY_PREFIX}_page_id"
    force_page_id_key = f"{NAVIGATION_KEY_PREFIX}_force_page_id"
    history_key = f"{NAVIGATION_KEY_PREFIX}_history"
    default_page_id_key = f"{NAVIGATION_KEY_PREFIX}_default_page_id"

    first_load = False

    if prev_url_page_id_key not in st.session_state:
        st.session_state[prev_url_page_id_key] = None

    if prev_page_id_key not in st.session_state:
        st.session_state[prev_page_id_key] = None

    if page_id_key not in st.session_state:
        st.session_state[page_id_key] = None
        first_load = True

    if force_page_id_key not in st.session_state:
        st.session_state[force_page_id_key] = None

    if history_key not in st.session_state:
        st.session_state[history_key] = []

    if section_info is None:
        section_info = {}
    

    default_page = None
    if isinstance(pages, dict):
        st_pages = {**pages}
        if account_page or settings_page or logout_page or login_page:
            st_pages["Account"] = []
        if account_page:
            st_pages["Account"].append(account_page)
        if settings_page:
            st_pages["Account"].append(settings_page)
        if logout_page:
            st_pages["Account"].append(logout_page)
        if login_page:
            st_pages["Account"].append(login_page)
        
        organized_pages = []
        for section, sub_pages in pages.items():
            no_default_pages = []
            for sub_page in sub_pages:
                if sub_page._default:
                    if default_page is None:
                        default_page = sub_page
                    else:
                        raise ValueError("You can only have one default page")
                else:
                    no_default_pages.append(sub_page)

            if section == "":
                organized_pages.extend(no_default_pages)
            else:
                organized_pages.append(
                    {
                        "name": section,
                        "subpages": no_default_pages,
                        "icon": section_info.get(section, {}).get("icon", None),
                        "ttip": section_info.get(section, {}).get("ttip", section)
                    }
                )
    else:
        organized_pages = []
        for page in pages:
            if page._default:
                if default_page is None:
                    default_page = page
                else:
                    raise ValueError("You can only have one default page")
            else:
                organized_pages.append(page)
        st_pages = {
            "": [*pages]
        }
        if account_page:
            st_pages[""].append(account_page)
        if settings_page:
            st_pages[""].append(settings_page)
        if logout_page:
            st_pages[""].append(logout_page)
        if login_page:
            st_pages[""].append(login_page)

    if default_page is None:
        raise ValueError("You must provide a default page")

    menu_pages, home_definition, menu_account_pages, pages_map = build_menu_from_st_pages(
        *organized_pages,
        home_page=default_page,  # Default page is the home page
        login_page=login_page, account_page=account_page, settings_page=settings_page,
        logout_page=logout_page,
    )

    st.session_state[f"{NAVIGATION_KEY_PREFIX}_menu_pages"] = menu_pages
    st.session_state[f"{NAVIGATION_KEY_PREFIX}_menu_account_pages"] = menu_account_pages
    st.session_state[default_page_id_key] = default_page._script_hash

    logout_page_id, login_page_id = None, None
    if login_page:
        login_page_id = login_page._script_hash
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_login_page_id"] = login_page_id

    if logout_page:
        logout_page_id = logout_page._script_hash
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_logout_page_id"] = logout_page_id

    if account_page:
        account_page_id = account_page._script_hash
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_account_page_id"] = account_page_id

    if settings_page:
        settings_page_id = settings_page._script_hash
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_settings_page_id"] = settings_page_id


    st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_map"] = pages_map


    if st.session_state[page_id_key] is None:
        st.session_state[page_id_key] = st.session_state[default_page_id_key]

    initial_force_page_id = st.session_state[force_page_id_key]

    if native_way:
        url_page_id = get_page_id_by_url_path(
            pages_map, st.context.url, prefix_url=prefix_url
        )
        if url_page_id != st.session_state[prev_url_page_id_key]:
            st.session_state[prev_url_page_id_key] = url_page_id
            if first_load:
                initial_force_page_id = url_page_id

    navbar_page_id = st_navbar(
        menu_definition=menu_pages,  # if st.session_state.logged_in else [],
        home_definition=home_definition,
        login_definition=menu_account_pages,
        hide_streamlit_markers=False,
        default_page_selected_id=st.session_state[page_id_key] or st.session_state[default_page_id_key],
        override_page_selected_id=st.session_state[force_page_id_key],
        override_first_page_load_id=initial_force_page_id,
        position_mode=position_mode,
        sticky_nav=sticky_nav,
        themes_data=themes_data,
        theme_changer=theme_changer,
        prefix_url=prefix_url,
        # url_navigation=native_way,  # and url_navigation,
        key=NAVIGATION_COMPONENT_KEY,
        hide_skeleton=True,
    )
    st.session_state[force_page_id_key] = None
    streamlit_page_id = st.session_state[page_id_key]
    st.session_state[page_id_key] = navbar_page_id or initial_force_page_id # Added to fix login/logout issue
    if native_way:
        url_page_id = get_page_id_by_url_path(
            pages_map, st.context.url, prefix_url=prefix_url
        )
        if url_page_id != st.session_state[prev_url_page_id_key]:
            st.session_state[prev_url_page_id_key] = url_page_id
            navbar_page_id = url_page_id

        page = st.navigation(
            st_pages,
            position="hidden"
        )
        streamlit_page_id = page._script_hash
    else:
        page = pages_map.get(navbar_page_id, default_page)

    if streamlit_page_id != navbar_page_id:
        st.session_state[page_id_key] = navbar_page_id
        if streamlit_page_id not in [logout_page_id, login_page_id]:
            st.session_state[prev_page_id_key] = streamlit_page_id
        st_switch_page(navbar_page_id, native_way=native_way)

    page._can_be_called = True
    add_page_to_history(page._script_hash)
    return page

def add_page_to_history(page_id: str):
    history_key = f"{NAVIGATION_KEY_PREFIX}_history"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    if len(st.session_state[history_key]) > 0:
        last_page_id, runs = st.session_state[history_key][-1].split("::")
        if page_id == last_page_id:
            st.session_state[history_key][-1] = f"{page_id}::{int(runs) + 1}"
            return

    st.session_state[history_key].append(f"{page_id}::1")

def has_changed_page() -> bool:
    history = st.session_state.get(f"{NAVIGATION_KEY_PREFIX}_history", [])
    if not history or len(history) < 2:
        return False

    try:
        actual_page_id, last_runs = history[-1].split("::")
        prev_page_id, _ = history[-2].split("::")
        return actual_page_id != prev_page_id and int(last_runs) <= 2
    except Exception:
        return False

def set_default_page(page_id: str):
    st.session_state[f"{NAVIGATION_KEY_PREFIX}_default_page_id"] = page_id

def init_navigation_transition(prev_page_id: str, page_id: str):
    prev_page_key = f"{NAVIGATION_KEY_PREFIX}_prev_page_id"
    page_key = f"{NAVIGATION_KEY_PREFIX}_page_id"
    if prev_page_key not in st.session_state:
        st.session_state[prev_page_key] = prev_page_id
    if page_key not in st.session_state:
        st.session_state[page_key] = page_id

def set_navigation_transition(prev_page_id: str, page_id: str):
    st.session_state[f"{NAVIGATION_KEY_PREFIX}_prev_page_id"] = prev_page_id
    st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_id"] = page_id

def set_force_next_page(page_id: str):
    st.session_state[f"{NAVIGATION_KEY_PREFIX}_force_page_id"] = page_id

def get_navigation_transition() -> tuple[str, str]:
    return (
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_prev_page_id"],
        st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_id"],
    )

def st_switch_home(native_way: bool = False):
    st_switch_page(st.session_state[f"{NAVIGATION_KEY_PREFIX}_default_page_id"], native_way=native_way)

def st_switch_page(page_id: str, native_way: bool = False):
    pages = st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_map"]
    page = pages.get(page_id, None)
    if page is None:
        raise ValueError(f"Page with id {page_id} not found")

    st.session_state[f"{NAVIGATION_KEY_PREFIX}_force_page_id"] = page_id
    if native_way:
        st.switch_page(page, query_params=dict(st.query_params))
    else:
        st.rerun()

def get_pages_info() -> tuple[dict[str, str], str, list[dict], list[dict], str | None, str | None, str | None, str | None]:
    pages = st.session_state[f"{NAVIGATION_KEY_PREFIX}_page_map"]

    default_page = next(filter(lambda p: p._default, pages.values()), None)
    if default_page is None:
        raise ValueError("You must provide a default page")

    default_page_id = default_page._script_hash
    
    login_page_id = st.session_state.get(f"{NAVIGATION_KEY_PREFIX}_login_page_id", None)
    logout_page_id = st.session_state.get(f"{NAVIGATION_KEY_PREFIX}_logout_page_id", None)
    account_page_id = st.session_state.get(f"{NAVIGATION_KEY_PREFIX}_account_page_id", None)
    settings_page_id = st.session_state.get(f"{NAVIGATION_KEY_PREFIX}_settings_page_id", None)

    menu_pages = st.session_state[f"{NAVIGATION_KEY_PREFIX}_menu_pages"]
    menu_account_pages = st.session_state[f"{NAVIGATION_KEY_PREFIX}_menu_account_pages"]

    return pages, default_page_id, menu_pages, menu_account_pages, login_page_id, logout_page_id, account_page_id, settings_page_id
