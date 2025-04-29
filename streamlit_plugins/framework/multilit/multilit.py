import logging
from pathlib import Path
import traceback
from collections import defaultdict
from typing import Any, Callable, Dict, Literal

import streamlit as st
from streamlit.commands.page_config import Layout, InitialSideBarState
from streamlit.runtime.scriptrunner import RerunException, StopException, get_script_run_ctx
from streamlit.navigation.page import StreamlitPage

try:
    from streamlit.runtime.scriptrunner.script_requests import ScriptRequestType, RerunData
except ModuleNotFoundError:
    from streamlit.runtime.scriptrunner_utils.script_requests import ScriptRequestType, RerunData

from streamlit.commands.execution_control import _new_fragment_id_queue

from streamlit_plugins.components.loader import BaseLoader
from streamlit_plugins.components.navbar import (
    DEFAULT_THEMES,
    HEADER_HEIGHT,
    NavbarPositionType,
    init_navigation_transition, get_navigation_transition,
    set_default_page, set_force_next_page, set_navigation_transition,
    st_navigation, st_switch_page,
)
from .app_wrapper import STPageWrapper
from .loading_engine import LoadingEngine

logger = logging.getLogger(__name__)

major, minnor, bug = st.__version__.split('.')
major, minnor, bug = int(major), int(minnor), int(bug)
# minnor == 36, 37
DEFAULT_NAVBAR_PARENT_SELECTOR_FRAGMENT = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""
DEFAULT_NAVBAR_PARENT_SELECTOR = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""
if major == 1:
    if minnor == 36:
        st.fragment = st.experimental_fragment
    if 36 <= minnor <= 37:
        ...
    if minnor == 38:
        DEFAULT_NAVBAR_PARENT_SELECTOR = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""
        DEFAULT_NAVBAR_PARENT_SELECTOR_FRAGMENT = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""

    if minnor >= 39:
        DEFAULT_NAVBAR_PARENT_SELECTOR = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""
        DEFAULT_NAVBAR_PARENT_SELECTOR_FRAGMENT = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""

    if minnor >= 43:
        DEFAULT_NAVBAR_PARENT_SELECTOR = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""
        DEFAULT_NAVBAR_PARENT_SELECTOR_FRAGMENT = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""

class FNStreamlitPage(StreamlitPage):
    def __init__(
        self,
        page: Callable[[], None],
        *,
        title: str | None = None,
        icon: str | None = None,
        url_path: str | None = None,
        default: bool = False,
    ):
        # Must appear before the return so all pages, even if running in bare Python,
        # have a _default property. This way we can always tell which script needs to run.
        self._default: bool = default

        inferred_name = "Uknown"
        inferred_icon = ":material/uknown:"
        if hasattr(page, "__name__"):
            inferred_name = str(page.__name__)

        self._page: Callable[[], None] = page
        self._title: str = title or inferred_name.replace("_", " ")
        self._icon: str = icon or inferred_icon

        if self._title.strip() == "":
            raise ValueError(
                "The title of the page cannot be empty or consist of underscores/spaces only"
            )

        self._url_path: str = inferred_name
        if url_path is not None:
            if url_path.strip() == "" and not default:
                raise ValueError(
                    "The URL path cannot be an empty string unless the page is the default page."
                )

            self._url_path = url_path.strip("/")

        self._can_be_called: bool = True

    def run(self):
        self._page()

class SectionWithStatement:
    def __init__(self, name, exit_fn):
        self.name = name
        self.exit_fn = exit_fn

    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_fn()


class Multilit:
    """
    Class to create a host application for combining multiple streamlit applications.
    """

    def __init__(
        self,
        title='Multilit Apps',
        nav_container=None,
        nav_horizontal=True,
        layout: Layout = "wide",
        favicon="🤹‍♀️",
        use_st_navigation_navbar=False,
        navbar_theme=None,
        navbar_sticky=True,
        navbar_mode: NavbarPositionType = 'under',
        use_loader=True,
        use_cookie_cache=True,
        sidebar_state: InitialSideBarState = 'auto',
        allow_url_nav=False,
        hide_streamlit_markers=False,
        use_banner_images=None,
        banner_spacing=None,
        clear_cross_page_sessions=True,
        session_params=None,
        verbose=False,
        within_fragment=False,
        login_info_session_key="logged_in"
    ):
        """
        A class to create an Multi-app Streamlit application. This class will be the host application for multiple applications that are added after instancing.
        The secret saurce to making the different apps work together comes from the use of a global session store that is shared with any MultiHeadApp that is added to the parent MultiApp.
        The session store is created when this class is instanced, by default the store contains the following variables that are used across the child apps:
            - previous_page
            - queued_page
            - preserve_state
            - allow_access
            - current_user
        More global values can be added by passing in a Dict when instancing the class, the dict needs to provide a name and default value that will be added to the global session store.
        Parameters
        -----------
        title: str, 'Streamlit MultiApp'
            The title of the parent app, this name will be used as the application (web tab) name.
        nav_container: Streamlit.container, None
            A container in which to populate the navigation buttons for each attached MultiHeadApp. Default will be a horizontal aligned banner style over the child applications. If the Streamlit sidebar is the target container, the navigation items will appear at the top and the default state of the sidebar will be expanded.
        nav_horizontal: bool, True
            To align the navigation buttons horizonally within the navigation container, if False, the items will be aligned vertically.
        layout: str, 'wide'
            The layout format to be used for all app pages (MultiHeadApps), same as the layout variable used in `set_page_config <https://docs.streamlit.io/en/stable/api.html?highlight=set_page_config#streamlit.set_page_config>`.
        favicon: str
            An inline favicon image to be used as the application favicon.
        allow_url_nav: bool False
            Enable navigation using url parameters, this allows for bookmarking and using internal links for navigation
        use_navbar: bool, False
            Use the Multilit Navbar component or internal Streamlit components to create the nav menu. Currently Multilit Navbar doesn't support dropdown menus.
        navbar_theme: Dict, None
            Override the Multilit Navbar theme, you can overrider only the part you wish or the entire theme by only providing details of the changes.
                - txc_inactive: Inactive Menu Item Text color
                - menu_background: Menu Background Color
                - txc_active: Active Menu Item Text Color
                - option_active: Active Menu Item Color
            example, navbar_theme = {'txc_inactive': '#FFFFFF','menu_background':'red','txc_active':'yellow','option_active':'blue'}
        navbar_sticky: bool, True
            Set navbar to be sticky and fixed to the top of the window.
        use_loader: bool, True
            Set if to use the app loader with auto transition spinners or load directly.
        navbar_animation: bool, False
            Set navbar is menu transitions should be animated.
        sidebar_state: str, 'auto'
            The starting state of the sidebase, same as variable used in `set_page_config <https://docs.streamlit.io/en/stable/api.html?highlight=set_page_config#streamlit.set_page_config>`.
        hide_streamlit_markers: bool, False
            A flag to hide the default Streamlit menu hamburger button and the footer watermark.
        use_banner_images: str or Array, None
            A path to the image file to use as a banner above the menu or an array of paths to use multiple images spaced using the rations from the banner_spacing parameter.
        banner_spacing: Array, None
            An array to specify the alignment of the banner images, this is the same as the array spec used by Streamlit Columns, if you want centered with 20% padding either side -> banner_spacing =[20,60,20]
        clear_cross_app_sessions: bool, True
            A flag to indicate if the local session store values within individual apps should be cleared when moving to another app, if set to False, when loading sidebar controls, will be a difference between expected and selected.
        session_params: Dict
            A Dict of parameter name and default values that will be added to the global session store, these parameters will be available to all child applications and they can get/set values from the store during execution.
        """

        self._active_section = None
        self._active_section_icon = None
        self._verbose = verbose
        self._within_fragment = within_fragment

        self._pages: dict[str, STPageWrapper] = {}
        self.pages_map: dict[str, StreamlitPage] = {}
        self._navbar_pointers = {}
        self._login_page: STPageWrapper | None = None
        self._login_id = 'page_login'
        self._home_page: STPageWrapper | None = None
        self._home_label = ["Home", ":material/home:"]
        self._home_id = 'page_home'
        self._settings_page: STPageWrapper | None = None
        self._settings_label = ["Settings", ":material/settings:"]
        self._settings_id = 'page_settings'
        self._account_page: STPageWrapper | None = None
        self._account_label = ["Account", ":material/account_circle:"]
        self._account_id = 'page_account'
        self._logout_label = ["Logout", ":material/logout:"]
        self._logout_id = 'logic_page_logout'
        self._check_login_callback = self.default_check_login
        self._do_login = self.login_callback(lambda: None)
        self._do_logout = self.logout_callback(lambda: None)

        self._complex_nav: dict[str, dict | StreamlitPage] = dict()
        self._navbar_mode: NavbarPositionType = navbar_mode
        self._navbar_active_index = 0
        self._allow_url_nav = False  # allow_url_nav
        self._navbar_sticky = navbar_sticky
        self._nav_item_count = 0
        self._use_st_navigation_navbar = use_st_navigation_navbar
        self._hide_streamlit_markers = hide_streamlit_markers
        self._navbar_theme = navbar_theme or DEFAULT_THEMES

        self._banners = use_banner_images
        self._banner_spacing = banner_spacing

        self._user_loader = use_loader
        
        self._use_cookie_cache = use_cookie_cache
        self._cookie_manager = None
        
        self._session_attrs = {}
        # self._call_queue = []
        # self._other_nav = None
        # self._guest_name = 'guest'
        # self._guest_access = 1
        # self._multilit_url_hash = 'mULTILIT|-HaShing==seCr8t'
        self._no_access_level = -1

        self._user_session_params = session_params

        if within_fragment:
            self._st_navbar_parent_selector = DEFAULT_NAVBAR_PARENT_SELECTOR_FRAGMENT
        else:
            self._st_navbar_parent_selector = DEFAULT_NAVBAR_PARENT_SELECTOR

        try:
            st.set_page_config(
                page_title=title, page_icon=favicon,
                layout=layout, initial_sidebar_state=sidebar_state
            )
        except Exception as e:
            pass

        # Establecer el tema

        self._nav_horizontal = nav_horizontal

        # self._theme_change_container = st.container()

        if self._banners is not None:
            self._banner_container = st.container()

        if nav_container is None:
            self._nav_container = st.container()
        else:
            # hack to stop the beta containers from running set_page_config before MultiApp gets a chance to.
            # if we have a beta_columns container, the instance is delayed until the run() method is called, beta components, who knew!
            if nav_container.__name__ in ['container']:
                self._nav_container = nav_container()
            else:
                self._nav_container = nav_container

        page_view = st.empty()
        self._page_container = page_view.container()

        if self._user_loader:
            self._loader_container = st.container()
            self._loading_engine = LoadingEngine(self._loader_container, self._page_container)

        self.cross_session_clear = clear_cross_page_sessions

        if clear_cross_page_sessions:
            preserve_state = 0
        else:
            preserve_state = 1

        self.login_info_session_key = login_info_session_key
        self._session_attrs = {
            # 'previous_page': None, 'actual_page': None, 'queued_page': None,'force_nav_page': None,
            'url_nav_page': None,
            'preserve_state': preserve_state, 'allow_access': self._no_access_level,
            login_info_session_key: None, 'access_hash': None, 'uncaught_error': None
        }

        if isinstance(self._user_session_params, dict):
            self._session_attrs |= self._user_session_params

        for key, item in self._session_attrs.items():
            if not hasattr(st.session_state, key):
                st.session_state[key] = item

    # def _encode_hyauth(self):
    #     user_access_level, username = self.check_access()
    #     payload = {"exp": datetime.now(timezone.utc) + timedelta(days=1), "userid": username,"user_level":user_access_level}
    #     return jwt.encode(payload, self._multilit_url_hash, algorithm="HS256")

    # def _decode_hyauth(self,token):
    #     return jwt.decode(token, self._multilit_url_hash, algorithms=["HS256"])

    def get_page_id(self, page: StreamlitPage) -> str:
        return page._script_hash

    def change_page(self, page: StreamlitPage, scope: Literal["app", "fragment"] = "app"):
        page_id = self.get_page_id(page)
        if page_id not in self._pages and page_id != self._home_id:
            raise ValueError(f"Page id {page_id} not found in the list of pages")

        # st.session_state["queued_page"] = page_id
        # ctx = get_script_run_ctx()
        # if ctx is not None:
        #     if page_id != ctx.page_script_hash:
        #         ctx.pages_manager.set_current_page_script_hash(page_id)
        #         rerun_data = RerunData(
        #             query_string=ctx.query_string,
        #             page_script_hash=page_id,
        #             fragment_id_queue=_new_fragment_id_queue(ctx, scope),
        #             is_fragment_scoped_rerun=scope == "fragment",
        #         )
        #         raise RerunException(rerun_data)
        # else:
        #     st.rerun()
        st_switch_page(page_id, native_way=self._use_st_navigation_navbar)

    def change_page_button(self, page: StreamlitPage, label: str):
        if st.button(label):
            self.change_page(page)

    def add_loader(self, loader: BaseLoader):
        self._loading_engine = LoadingEngine(self._loader_container, self._page_container, loader=loader)
        self._user_loader = True

    def add_page(
        self,
        page: StreamlitPage, title=None, page_id=None, icon: str | None = None,
        page_type: Literal["normal", "home", "login", "settings", "account"] = "normal",
        access_level: int | None = None,
        page_loader: BaseLoader | None = None
    ):
        """
        Adds a new application to this MultiApp
        Parameters
        ----------
        title: str
            The title of the app. This is the name that will appear on the menu item for this app.
        app: :MultiHeadApp:`~Multilit.MultiHeadApp`
            The app class representing the app to include, it must implement inherit from MultiHeadApp classmethod.
        icon: str
            The icon to use on the navigation button, this will be appended to the title to be used on the navigation control.
        app_type: str, 'normal'
            The type of app, this will determine the behaviour of the app within the MultiApp.
        login_callback: callable, None
            A function to call when the login app is loaded, this function will be called with the session state and the parent MultiApp instance.
        logout_callback: callable, None
            A function to call when the logout app is loaded, this function will be called with the session state and the parent MultiApp instance.
        access_level: int | None, None
            The access level of the app.
        """

        title = title or page.title
        # page_id = f"page_{page_id or len(self._pages) + 1}"
        page_id = page._script_hash

        app_wrapper = STPageWrapper(
            page, with_loader=bool(page_loader),
            loading_engine=LoadingEngine(self._loader_container, self._page_container, page_loader)
        )
        app_wrapper.access_level = access_level
        app_wrapper.id = page_id
        app_wrapper.title = title
        if page_type == "normal":
            # section_id = self._active_section or page_id
            # self._complex_nav[section_id].append(page_id)
            if self._active_section:
                self._complex_nav[self._active_section]["subpages"].append(page)
            else:
                self._complex_nav[page_id] = page

            self._navbar_pointers[page_id] = [title, icon]

        elif page_type == "login":
            self._login_page = app_wrapper
            # self._logout_label = [title or self._logout_label[0], icon or self._logout_label[1]]
            self._login_id = page_id

        elif page_type == "home":
            self._home_page = app_wrapper
            self._home_label = [title or self._home_label[0], icon or self._home_label[1]]
            self._home_id = page_id
            page._default = True
            set_default_page(page_id)
            init_navigation_transition(page_id, page_id)

        elif page_type == "settings":
            self._settings_page = app_wrapper
            self._settings_label = [title or self._settings_label[0], icon or self._settings_label[1]]
            self._settings_id = page_id

        elif page_type == "account":
            self._account_page = app_wrapper
            self._account_label = [title or self._account_label[0], icon or self._account_label[1]]
            self._account_id = page_id

        self._pages[page_id] = app_wrapper

        # Posiblemente esto sobre de aqui
        self._nav_item_count = int(self._login_page is not None) + len(self._pages.keys())
        # app.assign_session(st.session_state, self)

    def page(self, title=None, icon=None, page_type: Literal["normal", "home", "login", "settings", "account"] = "normal"):
        """
        This is a decorator to quickly add a function as a child app in a style like a Flask route.
        You can do everything you can normally do when adding a class based MultiApp to the parent, except you can not add a login or unsecure app using this method, as
        those types of apps require functions provided from inheriting from MultiAppTemplate.
        Parameters
        ----------
        title: str
            The title of the app. This is the name that will appear on the menu item for this app.
        icon: str
            The icon to use on the navigation button, this will be appended to the title to be used on the navigation control.
        app_type: str, 'normal'
            The type of app, this will determine the behaviour of the app within the MultiApp.
        """

        def decorator(func):
            app_icon = icon
            page_title = title
            is_default = False
            if page_type == "home":
                page_title = page_title or title
                app_icon = app_icon or ":material/home:"
                is_default = True

            wrapped_app = st.Page(func, title=page_title, icon=app_icon, default=is_default)
            self.add_page(title=page_title, page=wrapped_app, icon=app_icon, page_type=page_type)

            return func

        return decorator

    def new_section(self, title, icon=None):
        def _exit_fn():
            self._active_section = None
            self._active_section_icon = None

        section_id = f"sect_{title}"
        self._navbar_pointers[section_id] = [title, icon]
        self._active_section = section_id
        self._active_section_icon = icon

        self._complex_nav[self._active_section] = {
            "name": title, "subpages": [], "icon": icon, "ttip": title
        }

        return SectionWithStatement(title, _exit_fn)

    def _build_run_nav_menu(self) -> StreamlitPage:
        # number_of_sections = int(self._login_page is not None) + len(self._complex_nav.keys())

        home_page = self._home_page.st_page if self._home_page is not None else None
        login_page = self._login_page.st_page if self._login_page is not None else None
        account_page = self._account_page.st_page if self._account_page is not None else None
        settings_page = self._settings_page.st_page if self._settings_page is not None else None
        logout_page = None
        if self._login_page is not None:
            logout_page = FNStreamlitPage(self._do_logout, title="Logout", icon=":material/logout:")
            self._logout_id = self.get_page_id(logout_page)
            self._pages[self._logout_id] = STPageWrapper(logout_page)
        
        # native_position = "sidebar" if self._use_st_navigation_navbar else "hidden"
        natives_page_data = self.build_native_pages_data_from(
            home_page, # login_page, account_page, settings_page, logout_page
        )
        # new_navigation_page = st.navigation(natives_page_data, position=native_position)
        # new_navigation_page_id = new_navigation_page._script_hash
        # prev, actual, queued = self.get_nav_transition()
        # updated_with_navigation = False
        # if new_navigation_page_id != actual:
        #     updated_with_navigation = True
        #     st.session_state["force_nav_page"] = new_navigation_page_id
        #     self.update_nav_transition(actual, new_navigation_page_id, None)

        # if not self._use_st_navigation_navbar:
            # menu_definition, home_definition, account_login_definition, pages_map = build_menu_from_st_pages(
            #     *list(self._complex_nav.values()),
            #     home_page=home_page,
            #     login_page=login_page, account_page=account_page, settings_page=settings_page,
            #     logout_page=logout_page,
            # )
            # self.pages_map = pages_map

        with self._nav_container:
            page = self._run_navbar(natives_page_data, login_page, account_page, settings_page, logout_page)
                # if new_navbar_page_id != st.session_state["actual_page"]:
                #     st.session_state["queued_page"] = new_navbar_page_id
                
                # if updated_with_navigation:
                #     self.update_nav_transition
                #     st.session_state["force_nav_page"] = None
                # st.session_state["queued_page"] = new_app_id
        
        return page

    def build_native_pages_data_from(self, home_page, login_page=None, account_page=None, settings_page=None, logout_page=None):
        native_pages_data = {}
        if home_page is not None:
            native_pages_data[""] = [home_page]
        
        for sect, data in self._complex_nav.items():
            if sect.startswith("sect_"):
                data_section: dict = data
                pages: list[StreamlitPage] = data_section.get("subpages", [])
                native_pages_data[sect[len("sect_"):]] = pages
            else:
                data_page: StreamlitPage = data
                if "" not in native_pages_data:
                    native_pages_data[""] = []
                native_pages_data[""].append(data_page)
        
        if any([login_page, account_page, settings_page]):
            native_pages_data["Account"] = []
            for page in [account_page, settings_page, logout_page]:
                if page is not None:
                    native_pages_data["Account"].append(page)
        
        return native_pages_data

    @st.fragment
    def _fragment_navbar(self, natives_page_data, login_page, account_page, settings_page, logout_page, styles: str | None = None):
        new_page_id = self._standalone_navbar(natives_page_data, login_page, account_page, settings_page, logout_page, styles=styles)

        # if new_page_id != st.session_state["queued_page"]:
        #     st.session_state["queued_page"] = new_page_id
        
        # ctx = get_script_run_ctx()
        # page_script_hash = ctx.active_script_hash
        # rerun_data = RerunData(
        #     query_string=ctx.query_string,
        #     page_script_hash=page_script_hash,
        # )
        # raise RerunException(rerun_data)

        return new_page_id

    def _standalone_navbar(self, natives_page_data, login_page, account_page, settings_page, logout_page, styles: str | None = None) -> StreamlitPage:
        # override_app_selected_id = None
        # if st.session_state["force_nav_page"]:
        #     override_app_selected_id = st.session_state["force_nav_page"]
        #     st.session_state["force_nav_page"] = None

        # new_app_id = st_navbar(
        #     menu_definition=menu_definition, key="mainMultilitNavbar", home_definition=home_definition,
        #     override_theme=self._navbar_theme, login_definition=account_login_definition,
        #     hide_streamlit_markers=self._hide_streamlit_markers,
        #     default_page_selected_id=override_app_selected_id or st.session_state["queued_page"],
        #     override_page_selected_id=override_app_selected_id,
        #     sticky_nav=self._navbar_sticky, position_mode=self._navbar_mode, reclick_load=True,
        #     input_styles=styles
        # )
        page = st_navigation(
            natives_page_data,
            section_info={
                "Reports": {"icon": ":material/assessment:"},
                "Tools": {"icon": ":material/extension:"}
            },
            position_mode=self._navbar_mode if self._check_login_callback() else "hidden", sticky_nav=self._navbar_sticky,
            login_page=login_page, logout_page=logout_page,
            account_page=account_page,
            settings_page=settings_page,
            native_way=self._use_st_navigation_navbar,
            input_styles=styles,
            themes_data=self._navbar_theme
        )
        if self.cross_session_clear and st.session_state["preserve_state"]:
            self._clear_session_values()

        return page

    def _run_navbar(self, natives_page_data, login_page, account_page, settings_page, logout_page) -> StreamlitPage:
        # TODO: Agregar estilos para cada modo de navbar
        styles = ""
        if self._st_navbar_parent_selector:
            if self._navbar_mode == "top" and self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: 0;
                    z-index: 999990;
                }}
                """
            if self._navbar_mode == "top" and not self._navbar_sticky:
                styles = f"""
                .stMainBlockContainer {{
                    padding-top: 0rem !important;
                }}
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: 0;
                    z-index: 999990;
                }}
                """
            if self._navbar_mode == "under" and self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: calc({HEADER_HEIGHT}rem + 1rem);
                    z-index: 10;
                }}
                """
            if self._navbar_mode == "under" and not self._navbar_sticky:
                styles = f"""
                .stMainBlockContainer {{
                    padding-top: 1rem !important;
                }}
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: calc({HEADER_HEIGHT}rem - 5px);
                    z-index: 10;
                    margin-bottom: 1rem;
                }}
                """
            if self._navbar_mode == "side":
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    /* position: sticky; */
                    top: 0;
                    z-index: 9999999;
                    height: 2rem;
                }}
                """
        if self._within_fragment:
            page = self._fragment_navbar(natives_page_data, login_page, account_page, settings_page, logout_page, styles=styles)
        else:
            page = self._standalone_navbar(natives_page_data, login_page, account_page, settings_page, logout_page, styles=styles)

            # TODO: Send COI message to the component to update properly if willUmounted
            # set_page_id_visual("mainMultilitNavbar", new_app_id)

            # Hack to force a rerun and component update correctly
            # ctx = get_script_run_ctx()
            # if ctx is not None:
            #     page_script_hash = ctx.active_script_hash
            #     rerun_data = RerunData(
            #         query_string=ctx.query_string,
            #         page_script_hash=page_script_hash,
            #     )
            #     raise RerunException(rerun_data)

        return page

    def _get_next_app_info(self):
        if st.session_state["queued_page"] is None:
            page_id = st.session_state["actual_page"]

        else:
            if st.session_state["force_nav_page"] is not None:
                st.session_state["previous_page"] = st.session_state["queued_page"]
                st.session_state["queued_page"] = st.session_state["force_nav_page"]
                st.session_state["force_nav_page"] = None

            elif st.session_state["url_nav_page"] is not None:
                st.session_state["previous_page"] = st.session_state["queued_page"]
                st.session_state["queued_page"] = st.session_state["url_nav_page"]
                st.session_state["url_nav_page"] = None

            page_id = st.session_state["queued_page"]

        app_label = page_id
        if page_id in self._navbar_pointers:
            app_label = self._navbar_pointers[page_id][0]
        if page_id == self._home_id:
            app_label = self._home_label[0]
        if page_id == self._logout_id:
            app_label = self._logout_label[0]

        return page_id, app_label

    def _raise_base_exception(self, e, app_label):
        if isinstance(e, RerunException):
            raise e

        if isinstance(e, StopException):
            while isinstance(e, StopException):
                if e.__context__ is None:
                    break
                e = e.__context__

        trace_err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        # trace_err = traceback.format_exc()

        if isinstance(e, StopException):
            raise e

        logger.error(trace_err)

        # TODO: Averiguar como parar un stop y poder enviar el error a la interfaz de streamlit
        run_ctx = get_script_run_ctx()
        if run_ctx is not None:
            script_requests = run_ctx.script_requests
            if script_requests is not None:
                with script_requests._lock:
                    script_requests._state = ScriptRequestType.CONTINUE

        st.session_state["uncaught_error"] = trace_err

        st.error(
            f'😭 Error triggered from page: **{app_label}**\n\n'
            f'Details:\n'
            f'```{trace_err}```',
            icon="🚨"
        )
        raise e

    def _run_selected(self, page: STPageWrapper):
        page_label = None
        try:
            # print("Running", app_label)
            if self._verbose and st.session_state["uncaught_error"]:
                st.error(
                    f'😭 Error triggered from page: **{st.session_state["queued_page"]}**\n\n'
                    f'Details:\n'
                    f'```{st.session_state["uncaught_error"]}```',
                    icon="🚨"
                )

            # with self._theme_change_container:
            #     self._run_change_theme()

            if self._allow_url_nav:
                st.query_params['page'] = page.id

            if self._user_loader and page.has_loading():
                loading_engine = self._loading_engine
                if page.loading_engine is not None:
                    loading_engine = page.loading_engine
                
                with loading_engine.loading(status_msg=page_label or ""):
                    with self._page_container:
                        page.run()
            else:
                with self._page_container:
                    page.run()

            st.session_state["uncaught_error"] = None
        except Exception as e:
            self._raise_base_exception(e, page_label)

    def _clear_session_values(self):
        for key in st.session_state:
            del st.session_state[key]

    def set_guest(self, guest_name):
        """
        Set the name to be used for guest access.
        Parameters
        -----------
        guest_name: str
            The value to use when allowing guest logins.
        """

        if guest_name is not None:
            self._guest_name = guest_name

    def set_noaccess_level(self, no_access_level: int):
        """
        Set the access level integer value to be used to indicate no access, default is zero.
        Parameters
        -----------
        no_access_level: int
            The value to use to block access, all other values will have some level of access
        """

        if no_access_level is not None:
            self._no_access_level = int(no_access_level)

    def set_access(self, allow_access=0, access_user='', cache_access=False):
        """
        Set the access permission and the assigned username for that access during the current session.
        Parameters
        -----------
        allow_access: int, 0
            Value indicating if access has been granted, can be used to create levels of permission.
        access_user: str, None
            The username the access has been granted to for this session.
        cache_access: bool, False
            Save these access details to a browser cookie so the user will auto login when they visit next time.
        """

        # Set the global access flag
        st.session_state["allow_access"] = allow_access

        # Also, who are we letting in..
        st.session_state["current_user"] = access_user

    def check_access(self):
        """
        Check the access permission and the assigned user for the running session.
        Returns
        ---------
        tuple: access_level, username
        """
        username = None

        if hasattr(st.session_state, 'current_user'):
            username = str(st.session_state["current_user"])

        return int(st.session_state["allow_access"]), username

    def get_nav_transition(self) -> tuple[None|str, None|str, None|str]:
        """
        Check the previous and current page names the user has navigated between
        Returns
        ---------
        tuple: previous_page, current_app
        """

        return st.session_state["previous_page"], st.session_state["actual_page"], st.session_state["queued_page"]

    def update_nav_transition(self, prev_page_id, actual_page_id, next_page_id):
        st.session_state["previous_page"] = actual_page_id if actual_page_id not in [self._login_id, self._logout_id, prev_page_id] else prev_page_id
        st.session_state["actual_page"] = actual_page_id
        st.session_state["queued_page"] = next_page_id

    def _do_url_params(self):
        if self._allow_url_nav:
            query_params = st.query_params
            if 'page' in query_params:
                # and (query_params['selected'])[0] != st.session_state["previous_page"]:
                if query_params['page'] != 'None' and query_params['page'] != st.session_state["queued_page"]:
                    st.session_state["url_nav_page"] = query_params['page']
                    del query_params['page']
                else:
                    st.session_state["url_nav_page"] = None

    def enable_guest_access(self, guest_access_level=1, guest_username='guest'):
        """
        This method will auto login a guest user when the page is secured with a login page, this will allow fora guest user to by-pass the login page and gain access to the other apps that the assigned access level will allow.
        ------------
        guest_access_level: int, 1
            Set the access level to assign to an auto logged in guest user.
        guest_username: str, guest
            Set the username to assign to an auto logged in guest user.
        """

        user_access_level, username = self.check_access()
        if user_access_level == 0 and username is None:
            self.set_access(guest_access_level, guest_username)

    # def get_cookie_manager(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         return self._cookie_manager
    #     else:
    #         return None

    # def _delete_cookie_cache(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         username_cache = self._cookie_manager.get('hyusername')
    #         accesslevel_cache = self._cookie_manager.get('hyaccesslevel')

    #         if username_cache is not None:
    #             self._cookie_manager.delete('hyusername')

    #         if accesslevel_cache is not None:
    #             self._cookie_manager.delete('hyaccesslevel')

    # def _write_cookie_cache(self,hyaccesslevel,hyusername):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         if hyaccesslevel is not None and hyusername is not None:
    #             self._cookie_manager.set('hyusername',hyusername)
    #             self._cookie_manager.set('hyaccesslevel',hyaccesslevel)

    # def _read_cookie_cache(self):
    #     if self._use_cookie_cache and self._cookie_manager is not None:
    #         username_cache = self._cookie_manager.get('hyusername')
    #         accesslevel_cache = self._cookie_manager.get('hyaccesslevel')

    #         if username_cache is not None and accesslevel_cache is not None:
    #             self.set_access(int(accesslevel_cache), str(username_cache))

    def run(self):
        """
        This method is the entry point for the MultiApp, just like a single Streamlit page, you simply setup the additional apps and then call this method to begin.
        """
        # process url navigation parameters
        self._do_url_params()

        if self._banners is not None:
            if isinstance(self._banners, str):
                self._banners = [self._banners]

            if self._banner_spacing is not None and len(self._banner_spacing) == len(self._banners):
                cols = self._banner_container.columns(self._banner_spacing)
                for idx, im in enumerate(self._banners):
                    if im is not None:
                        if isinstance(im, Dict):
                            cols[idx].markdown(
                                next(iter(im.values())), unsafe_allow_html=True)
                        else:
                            cols[idx].image(im)
            else:
                if self._banner_spacing is not None and len(self._banner_spacing) != len(self._banners):
                    logger.warning(
                        'Banner spacing spec is a different length to the number of banners supplied, using even spacing for each banner.'
                    )

                cols = self._banner_container.columns([1] * len(self._banners))
                for idx, im in enumerate(self._banners):
                    if im is not None:
                        if isinstance(im, Dict):
                            cols[idx].markdown(
                                next(iter(im.values())), unsafe_allow_html=True)
                        else:
                            cols[idx].image(im)

        # Verifico la autenticacion (self.login_info_session_key) y la autorizacion (allow_access)
        if self._check_login_callback():
            # prev_page_id, actual_page_id, next_page_id = self.get_nav_transition()
            prev_page_id, actual_page_id = get_navigation_transition()
            if actual_page_id == self._login_id:
                self._do_login()

            if self._nav_item_count == 0:
                self._default()
            else:
                page = self._build_run_nav_menu()
                page_id = self.get_page_id(page)
                if page_id == self._logout_id:
                    ctx = get_script_run_ctx()
                    # Se evita recargas innecesarias o paradas si esta pendiente cambiar al logout
                    if ctx.script_requests._state == ScriptRequestType.CONTINUE:
                        ctx.script_requests._state = ScriptRequestType.CONTINUE
                # La navegacion nativa de streamlit no necesita ejeuctar o especificar la pagina
                # if not self._use_st_navigation_navbar:
                #     page_id, page_label = self._get_next_app_info()
                # else:
                #     ctx = get_script_run_ctx()
                #     if ctx is not None:
                #         # prev_page_id, actual_page_id, next_page_id = self.get_nav_transition()
                #         prev_page_id, actual_page_id = get_page_transition()
                #         page_id = ctx.page_script_hash
                #         if page_id == self._logout_id and actual_page_id == self._login_id:
                #             page_id = prev_page_id or self._home_id
                
                page_wrapper = self._pages.get(page_id)
                if page_wrapper is None:
                    raise ValueError(f"App id {page_id} not found in the list of apps")

                # Aqui se verifica autorizacion
                # if page_id == self._logout_id:
                #     # Se devuelve porque 
                #     self._do_logout()
                #     return

                # _, actual_page_id, _ = self.get_nav_transition()
                # self.update_nav_transition(actual_page_id, page_id, None)

                # ctx = get_script_run_ctx()
                # if ctx is not None:
                #     if page_id != ctx.page_script_hash:
                #         ctx.pages_manager.set_current_page_script_hash(page_id)
                #         rerun_data = RerunData(
                #             query_string=ctx.query_string,
                #             page_script_hash=page_id,
                #         )
                #         raise RerunException(rerun_data)
                
                self._run_selected(page_wrapper)


        # elif st.session_state["allow_access"] < self._no_access_level:
        #     st.session_state["current_user"] = self._guest_name
        #     self._unsecure_app.run()
        else:
            page = self._build_run_nav_menu()
            page_id = self.get_page_id(page)
            if page_id != self._login_id:
                # Se transiciona a la pagina de login si no lo fuera
                ...

            st.session_state["current_user"] = None
            st.session_state["access_hash"] = None
            if self._login_page is not None:
                # st.session_state["queued_page"] = st.session_state['actual_page']
                # st.session_state['actual_page'] = self._login_id
                self._login_page.run()

    def default_home_dashboard(self):
        def default_home_wrapper():
            app_valids_map = {
                app_id: app
                for app_id, app in self._pages.items()
                if app_id not in [self._login_id, self._logout_id, self._home_id]
            }
            # Se contruye un grid de elementos para cambiar de apps
            col1, col2 = st.columns(2)
            # Calculo el total de aplicaciones y se asignan a cada columna y fila

            total_apps = len(app_valids_map)
            apps_per_col = total_apps // 2
            # Se recorren las aplicaciones y se asignan a cada columna
            for i, (page_id, page) in enumerate(app_valids_map.items()):
                if i < apps_per_col:
                    col = col1
                else:
                    col = col2

                with col:
                    with st.container(border=True):
                        st.markdown(f"### {page.title}")
                        self.change_page_button(page.st_page, page.title)

        return st.Page(default_home_wrapper, title="Dashboard", icon=":material/dashboard:")

    def _default(self):
        st.header('Welcome to Multilit')
        st.write(
            'Thank you for your enthusiasum and looking to run the MultiApp as quickly as possible, for maximum effect, please add a child page by one of the methods below.')

        st.write('Method 1 (easiest)')

        st.code("""
#when we import multilit, we automatically get all of Streamlit
import multilit
multi_app = multilit.MultiApp(title='Simple Multi-Page App')
@multi_app.addapp()
def my_cool_function():
    hy.info('Hello from page 1')
        """
                )

        st.write('Method 2 (more fun)')

        st.code("""
    from multilit import MultiHeadApp
    import streamlit as st
    #create a child page wrapped in a class with all your code inside the run() method.
    class CoolApp(MultiHeadApp):
        def run(self):
            st.info('Hello from cool page 1')
    #when we import multilit, we automatically get all of Streamlit
    import multilit
    multi_app = multilit.MultiApp(title='Simple Multi-Page App')
    multi_app.add_page("My Cool App", icon="📚", app=CoolApp(title="Cool App"))
            """
                )

        st.write(
            'Once we have added atleast one child application, we just run the parent page!')

        st.code("""
    multi_app.run()
            """)

        st.write(
            'For example you get can going super quick with a couple of functions and a call to Multilit App run().')

        st.code("""
        #when we import multilit, we automatically get all of Streamlit
        import multilit
        multi_app = multilit.MultiApp(title='Simple Multi-Page App')
        @app.addapp(is_home=True)
        def my_home():
        hy.info('Hello from Home!')
        @app.addapp()
        def app2():
        hy.info('Hello from app 2')
        @app.addapp(title='The Best', icon="🥰")
        def app3():
        hy.info('Hello from app 3, A.K.A, The Best 🥰')
        #Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
        app.run()
            """)

    def login_callback(self, func):
        """
        This is a decorate to add a function to be run when a user is first logged in.
        """

        def wrapper(*args, **kwargs):
            st.session_state[self.login_info_session_key] = True
            prev_page_id, page_id = get_navigation_transition()
            # prev_page_id, actual_page_id, next_page_id = self.get_nav_transition()
            # st.session_state['actual_page_id'] = next_page_id
            # st.session_state['queued_page'] = None
            # st.session_state['previous_page'] = prev_page_id
            set_navigation_transition(prev_page_id, prev_page_id)
            set_force_next_page(prev_page_id)
            func(*args, **kwargs)
            # st.rerun()
            if prev_page_id is None:
                prev_page_id = self._home_id
            
            st_switch_page(prev_page_id)

        self._do_login = wrapper
        return wrapper

    def default_check_login(self) -> Any:
        """
        Check if the user is logged in.

        :return: True if the user is logged in, False otherwise.
        """
        if self._login_page is None:
            # No hay login
            return True

        if self.login_info_session_key in st.session_state:
            return st.session_state[self.login_info_session_key]

        return False

    def logout_callback(self, func):
        """
        This is a decorate to add a function to be run when a user is logged out.
        """

        def logout_wrapper(*args, **kwargs):
            st.session_state[self.login_info_session_key] = None
            st.session_state['allow_access'] = self._no_access_level
            # st.session_state['previous_page'] = st.session_state["url_nav_page"] or st.session_state["queued_page"]
            # st.session_state['queued_page'] = self._login_id
            # st.session_state["queued_page"] = None
            prev_page_id, actual_page_id = get_navigation_transition()
            set_navigation_transition(prev_page_id, self._login_id)
            func(*args, **kwargs)
            # st.rerun()
            st_switch_page(self._login_id)

        self._do_logout = logout_wrapper
        return logout_wrapper