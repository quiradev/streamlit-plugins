import logging
import traceback
from collections import defaultdict
from typing import Dict, Literal

import streamlit as st
from streamlit.runtime.scriptrunner import RerunException, StopException, get_script_run_ctx
from streamlit.runtime.scriptrunner.script_requests import ScriptRequestType, RerunData
import streamlit.components.v1 as components

from streamlit_plugins.components.navbar import st_navbar
from streamlit_plugins.framework.multilit.wrapper_class import Templateapp
from .app_template import MultiHeadApp
from .loading_app import LoadingApp

logger = logging.getLogger(__name__)


DEFAULT_NAVBAR_PARENT_SELECTOR = """[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] > iframe[title="streamlit_plugins.components.navbar.nav_bar"])"""


class SectionWithStatement:
    def __init__(self, name, exit_fn):
        self.name = name
        self.exit_fn = exit_fn

    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_fn()


class MultiApp(object):
    """
    Class to create a host application for combining multiple streamlit applications.
    """

    def __init__(
        self,
        title='Multilit Apps',
        nav_container=None,
        nav_horizontal=True,
        layout='wide',
        favicon="🤹‍♀️",
        use_navbar=True,
        navbar_theme=None,
        navbar_sticky=True,
        navbar_mode: Literal["top", "under"] = 'under',
        use_loader=True,
        use_cookie_cache=True,
        sidebar_state='auto',
        navbar_animation=True,
        allow_url_nav=False,
        hide_streamlit_markers=False,
        use_banner_images=None,
        banner_spacing=None,
        clear_cross_app_sessions=True,
        session_params=None,
        verbose=False,
        within_fragment=False,
        st_navbar_parent_selector=DEFAULT_NAVBAR_PARENT_SELECTOR,
    ):
        """
        A class to create an Multi-app Streamlit application. This class will be the host application for multiple applications that are added after instancing.
        The secret saurce to making the different apps work together comes from the use of a global session store that is shared with any MultiHeadApp that is added to the parent MultiApp.
        The session store is created when this class is instanced, by default the store contains the following variables that are used across the child apps:
         - previous_app
         - selected_app
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

        self._apps = {}
        self._navbar_pointers = {}
        self._login_app = None
        self._unsecure_app = None
        self._home_app = None
        self._home_label = ["Home", ":material/home:"]
        self._home_id = 'app_home'
        self._complex_nav = defaultdict(list)
        self._navbar_mode = navbar_mode
        self._navbar_active_index = 0
        self._allow_url_nav = allow_url_nav
        self._navbar_animation = navbar_animation
        self._navbar_sticky = navbar_sticky
        self._nav_item_count = 0
        self._use_navbar = use_navbar
        self._navbar_theme = navbar_theme or {
            "menu_background": "var(--background-color)",
            # "menu_background": "transparent",
            "txc_inactive": "var(--text-color)",
            "txc_active": "var(--text-color)",
            "option_active": "var(--primary-color)",
        }
        self._banners = use_banner_images
        self._banner_spacing = banner_spacing
        self._hide_streamlit_markers = hide_streamlit_markers
        self._user_loader = use_loader
        self._use_cookie_cache = use_cookie_cache
        self._cookie_manager = None
        self._logout_label = ["Logout", ":material/account_circle:"]
        self._logout_id = 'app_logout'
        self._logout_callback = None
        self._login_callback = None
        self._session_attrs = {}
        self._call_queue = []
        self._other_nav = None
        self._guest_name = 'guest'
        self._guest_access = 1
        self._multilit_url_hash = 'mULTILIT|-HaShing==seCr8t'
        self._no_access_level = 0

        self._user_session_params = session_params

        self._st_navbar_parent_selector = st_navbar_parent_selector

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

        self._app_container = st.container()

        if self._user_loader:
            self._loader_container = st.container()
            self._loader_app = LoadingApp(loader_container=self._loader_container, app_container=self._app_container)

        self.cross_session_clear = clear_cross_app_sessions

        if clear_cross_app_sessions:
            preserve_state = 0
        else:
            preserve_state = 1

        self._session_attrs = {
            'previous_app': None, 'selected_app': None, 'other_nav_app': None,
            'preserve_state': preserve_state, 'allow_access': self._no_access_level,
            'logged_in': False, 'access_hash': None, 'uncaught_error': None
        }
        self.session_state = st.session_state

        if isinstance(self._user_session_params, Dict):
            self._session_attrs |= self._user_session_params

        for key, item in self._session_attrs.items():
            if not hasattr(self.session_state, key):
                self.session_state[key] = item

    # def _encode_hyauth(self):
    #     user_access_level, username = self.check_access()
    #     payload = {"exp": datetime.now(timezone.utc) + timedelta(days=1), "userid": username,"user_level":user_access_level}
    #     return jwt.encode(payload, self._multilit_url_hash, algorithm="HS256")

    # def _decode_hyauth(self,token):
    #     return jwt.decode(token, self._multilit_url_hash, algorithms=["HS256"])

    def change_app(self, app_id: str):
        if app_id not in self._apps and app_id != self._home_id:
            raise ValueError(f"App id {app_id} not found in the list of apps")

        self.session_state.other_nav_app = app_id
        st.rerun()

    def change_app_button(self, app_id: str, label: str):
        if st.button(label):
            self.change_app(app_id)

    def add_loader_app(self, loader_app):
        """
        To improve the transition between MultiHeadApps, a loader app is used to quickly clear the window during loading, you can supply a custom loader app, if your include an app that loads a long time to initalise, that is when this app will be seen by the user.
        NOTE: make sure any items displayed are removed once the target app loading is complete, or the items from this app will remain on top of the target app display.
        Parameters
        ------------
        loader_app: MultiHeadApp:`~Multilit.MultiHeadApp`
            The loader app, this app must implement a modified run method that will receive the target app to be loaded, within the loader run method, the run() method of the target app must be called, or nothing will happen and it will stay in the loader app.
        """

        if loader_app:
            self._loader_app = loader_app
            self._user_loader = True
        else:
            self._loader_app = None
            self._user_loader = False

    def add_app(self, title, app: MultiHeadApp, id: str = None, icon: str = None, is_login=False, is_home=False,
                logout_label: str = None, is_unsecure=False):
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
        is_login: bool, False
            Is this app used to login to the family of apps, this app will provide request response to gateway access to the other apps within the MultiApp.
        is_home: bool, False
            Is this the first 'page' that will be loaded, if a login app is provided, this is the page that will be kicked to upon successful login.
        is_unsecure: bool, False
            An app that can be run other than the login if using security, this is typically a sign-up app that can be run and then kick back to the login.
        """

        app_id = f"app_{id or len(self._apps) + 1}"

        app._id = app_id

        if not is_login and not is_home:
            section_id = self._active_section or app_id
            self._complex_nav[section_id].append(app_id)

        # don't add special apps to list
        if not is_login and not is_home:
            self._navbar_pointers[app_id] = [title, icon]

        if is_unsecure:
            self._unsecure_app = app

        if is_login:
            self._login_app = app
            self._logout_label = [title or self._logout_label[0], icon or self._logout_label[1]]

        elif is_home:
            self._home_app = app
            self._home_label = [title or self._home_label[0], icon or self._home_label[1]]
        else:
            self._apps[app_id] = app

        self._nav_item_count = int(self._login_app is not None) + len(self._apps.keys())
        app.assign_session(self.session_state, self)

    def addapp(self, id=None, title=None, icon=None, is_home=False):
        """
        This is a decorator to quickly add a function as a child app in a style like a Flask route.
        You can do everything you can normally do when adding a class based MultiApp to the parent, except you can not add a login or unsecure app using this method, as
        those types of apps require functions provided from inheriting from MultiAppTemplate.
        Parameters
        ----------
        id: str
            The id of the app.
        title: str
            The title of the app. This is the name that will appear on the menu item for this app.
        icon: str
            The icon to use on the navigation button, this will be appended to the title to be used on the navigation control.
        is_home: bool, False
            Is this the first 'page' that will be loaded, if a login app is provided, this is the page that will be kicked to upon successful login.
        """

        def decorator(func):
            wrapped_app = Templateapp(mtitle=title, run_method=func)
            app_title = wrapped_app.title
            app_icon = icon

            if is_home and title is None and icon is None:
                app_title = None
                app_icon = ":material/home:"

            self.add_app(title=app_title, app=wrapped_app, icon=app_icon, is_home=is_home)

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

        return SectionWithStatement(title, _exit_fn)

    def _build_nav_menu(self):
        number_of_sections = int(self._login_app is not None) + len(self._complex_nav.keys())

        if self._use_navbar:
            menu_data = []
            for i, nav_section_id in enumerate(self._complex_nav):
                menu_item = None
                if nav_section_id not in [self._home_label[0], self._logout_label[0]]:
                    submenu_items = []
                    for app_item_id in self._complex_nav[nav_section_id]:
                        menu_item = {
                            'id': app_item_id,
                            'label': self._navbar_pointers[app_item_id][0],
                            'icon': self._navbar_pointers[app_item_id][1]
                        }
                        if len(self._complex_nav[nav_section_id]) > 1:
                            submenu_items.append(menu_item)

                    if len(submenu_items) > 0:
                        menu_item = {
                            'id': nav_section_id,
                            'label': self._navbar_pointers[nav_section_id][0],
                            'icon': self._navbar_pointers[nav_section_id][1],
                            'submenu': submenu_items
                        }

                    if menu_item is not None:
                        menu_data.append(menu_item)

            # Add logout button and kick to login action
            if self._login_app is not None:
                # if self.session_state.current_user is not None:
                #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                with self._nav_container:
                    self._run_navbar(menu_data)

                # user clicked logout
                if self.session_state.selected_app == self._logout_id:
                    self._do_logout()
            else:
                # self.session_state.previous_app = self.session_state.selected_app
                with self._nav_container:
                    new_app_id = self._run_navbar(menu_data)
                    self.session_state.selected_app = new_app_id

        else:
            if self._nav_horizontal:
                if hasattr(self._nav_container, 'columns'):
                    nav_slots = self._nav_container.columns(number_of_sections)
                elif self._nav_container.__name__ in ['columns']:
                    nav_slots = self._nav_container(number_of_sections)
                else:
                    nav_slots = self._nav_container
            else:
                if self._nav_container.__name__ in ['columns']:
                    # columns within columns currently not supported
                    nav_slots = st
                else:
                    nav_slots = self._nav_container

            for i, nav_section_id in enumerate(self._complex_nav):
                if nav_section_id not in [self._home_id, self._logout_id]:
                    if self._nav_horizontal:
                        nav_section_root = nav_slots[i]
                    else:
                        nav_section_root = nav_slots

                    if len(self._complex_nav[nav_section_id]) == 1:
                        nav_section = nav_section_root.container()
                    else:
                        sect_label = f"{self._navbar_pointers[nav_section_id][1]} {self._navbar_pointers[nav_section_id][1]}"
                        nav_section = nav_section_root.expander(label=sect_label, expanded=False)

                    for app_item_id in self._complex_nav[nav_section_id]:
                        btn_type = "primary" if self.session_state.selected_app == app_item_id else "secondary"
                        if nav_section.button(label=self._navbar_pointers[app_item_id][0], type=btn_type):
                            self.session_state.previous_app = self.session_state.selected_app
                            self.session_state.selected_app = app_item_id

            if self.cross_session_clear and self.session_state.previous_app != self.session_state.selected_app and not self.session_state.preserve_state:
                self._clear_session_values()

            # Add logout button and kick to login action
            if self._login_app is not None:
                # if self.session_state.current_user is not None:
                #    self._logout_label = '{} : {}'.format(self.session_state.current_user.capitalize(),self._logout_label)

                if self._nav_horizontal:
                    if nav_slots[-1].button(label=self._logout_label[0]):
                        self._do_logout()
                else:
                    if nav_slots.button(label=self._logout_label[0]):
                        self._do_logout()

    @st.experimental_fragment
    def _fragment_navbar(self, menu_data):
        new_app_id = self._standalone_navbar(menu_data)
        # if new_app_id != self.session_state.selected_app:
        #     self.session_state.selected_app = new_app_id

        # ctx = get_script_run_ctx()
        # page_script_hash = ctx.active_script_hash
        # rerun_data = RerunData(
        #     query_string=ctx.query_string,
        #     page_script_hash=page_script_hash,
        # )
        # raise RerunException(rerun_data)

        return new_app_id

    def _standalone_navbar(self, menu_data):
        login_nav = None
        home_nav = None
        if self._login_app:
            login_nav = {
                'id': self._logout_id, 'label': self._logout_label[0], 'icon': self._logout_label[1], 'ttip': 'Logout'
            }

        if self._home_app:
            home_nav = {
                'id': self._home_id, 'label': self._home_label[0], 'icon': self._home_label[1], 'ttip': 'Home'
            }

        # menu_index = [self._home_id] + [d['id'] for d in menu_data] + [self._logout_id]

        override_app_selected_id = None
        if self.session_state.other_nav_app:
            override_app_selected_id = self.session_state.other_nav_app

        new_app_id = st_navbar(
            menu_definition=menu_data, key="mainMultilitMenuComplex", home_name=home_nav,
            override_theme=self._navbar_theme, login_name=login_nav,
            use_animation=self._navbar_animation, hide_streamlit_markers=self._hide_streamlit_markers,
            default_app_selected_id=override_app_selected_id or self.session_state.selected_app,
            override_app_selected_id=override_app_selected_id,
            sticky_nav=self._navbar_sticky, position_mode=self._navbar_mode, reclick_load=True
        )
        if self.cross_session_clear and self.session_state.preserve_state:
            self._clear_session_values()

        return new_app_id

    def _run_change_theme(self):
        # Configure theme
        base_theme = st._config.get_option("theme.base") or "light"
        self.session_state["theme"] = base_theme
        if base_theme == "light":
            change_theme = st.button("dark", key="theme-button")
        else:
            change_theme = st.button("light", key="theme-button")

        # if change_theme:
        #     if base_theme == "light":
        #         st._config._set_option("theme.base", "dark", "<streamlit>")
        #     else:
        #         st._config._set_option("theme.base", "light", "<streamlit>")
        #
        #     st.rerun()

        # Función para inyectar CSS
        def inject_css():
            style = """
            body.default-theme {
                background-color: white !important;
                color: black !important;
            }

            body.dark-theme {
                background-color: black !important;
                color: white !important;
            }
            """
            st.markdown(f'<style>{style}</style>', unsafe_allow_html=True)

        inject_css()

        if base_theme == "light":
            components.html("<script>window.parent.document.body.className = 'dark-theme';</script>", height=0)
            self.session_state["theme"] = "dark"
        else:
            components.html("<script>window.parent.document.body.className = 'default-theme';</script>", height=0)
            self.session_state["theme"] = "light"

    def _run_navbar(self, menu_data):
        # TODO: Agregar estilos para cada modo de navbar
        styles = ""
        if self._st_navbar_parent_selector:
            if self._navbar_mode == "top" and self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: -1.25em;
                    z-index: 999990;
                }}
                """
            if self._navbar_mode == "top" and not self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    z-index: 999990;
                    top: 5em;
                    margin-top: -1em;
                }}
                """
            if self._navbar_mode == "under" and self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    top: 6em;
                    z-index: 1;
                }}
                """
            if self._navbar_mode == "under" and not self._navbar_sticky:
                styles = f"""
                {self._st_navbar_parent_selector} {{
                    position: sticky;
                    z-index: 1;
                    top: 8.625em;
                    margin-top: 1em;
                }}
                """

        st.markdown(f'<style>{styles}</style>', unsafe_allow_html=True)
        if self._within_fragment:
            new_app_id = self._fragment_navbar(menu_data)
        else:
            new_app_id = self._standalone_navbar(menu_data)

        if new_app_id != self.session_state.selected_app:
            self.session_state.selected_app = new_app_id

            # Hack to force a rerun and component update correctly
            # because
            ctx = get_script_run_ctx()
            page_script_hash = ctx.active_script_hash
            rerun_data = RerunData(
                query_string=ctx.query_string,
                page_script_hash=page_script_hash,
            )
            raise RerunException(rerun_data)

        return new_app_id

    def _run_selected(self):
        app_label = None
        try:
            if self.session_state.selected_app is None:
                self.session_state.other_nav_app = None
                self.session_state.previous_app = None
                self.session_state.selected_app = self._home_id

                app = self._home_app
                app_id = self._home_id

            else:
                if self.session_state.other_nav_app is not None:
                    self.session_state.previous_app = self.session_state.selected_app
                    self.session_state.selected_app = self.session_state.other_nav_app
                    self.session_state.other_nav_app = None

                if self.session_state.selected_app == self._home_id:
                    app = self._home_app
                    app_id = self._home_id
                else:
                    app = self._apps[self.session_state.selected_app]
                    app_id = self.session_state.selected_app

            app_label = app_id
            if app_id in self._navbar_pointers:
                app_label = self._navbar_pointers[app_id][0]
            if app_id == self._home_id:
                app_label = self._home_label[0]
            if app_id == self._logout_id:
                app_label = self._logout_label[0]

            # print("Running", app_label)
            if self._verbose and self.session_state.uncaught_error:
                st.error(
                    f'😭 Error triggered from app: **{self.session_state.selected_app}**\n\n'
                    f'Details:\n'
                    f'```{self.session_state.uncaught_error}```',
                    icon="🚨"
                )

            # with self._theme_change_container:
            #     self._run_change_theme()

            if self._user_loader and app.has_loading():
                self._loader_app.run(app, status_msg=app_label)
            else:
                with self._app_container:
                    app.run()

            self.session_state.uncaught_error = None
        except BaseException as e:
            if isinstance(e, RerunException):
                raise e

            if isinstance(e, StopException):
                while isinstance(e, StopException):
                    if e.__context__ is None:
                        break
                    e = e.__context__

            trace_err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            # trace_err = traceback.format_exc()

            logger.error(trace_err)

            if isinstance(e, StopException):
                raise e

            # TODO: Averiguar como parar un stop y poder enviar el error a la interfaz de streamlit
            run_ctx = get_script_run_ctx()
            with run_ctx.script_requests._lock:
                run_ctx.script_requests._state = ScriptRequestType.CONTINUE

            self.session_state.uncaught_error = trace_err

            st.error(
                f'😭 Error triggered from app: **{app_label}**\n\n'
                f'Details:\n'
                f'```{trace_err}```',
                icon="🚨"
            )
            raise e

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
        self.session_state.allow_access = allow_access

        # Also, who are we letting in..
        self.session_state.current_user = access_user

    def check_access(self):
        """
        Check the access permission and the assigned user for the running session.
        Returns
        ---------
        tuple: access_level, username
        """
        username = None

        if hasattr(self.session_state, 'current_user'):
            username = str(self.session_state.current_user)

        return int(self.session_state.allow_access), username

    def get_nav_transition(self):
        """
        Check the previous and current app names the user has navigated between
        Returns
        ---------
        tuple: previous_app, current_app
        """

        return str(self.session_state.previous_app), str(self.session_state.selected_app)

    def get_user_session_params(self):
        """
        Return a dictionary of the keys and current values of the user defined session parameters.
        Returns
        ---------
        dict
        """
        user_session_params = {}

        if self._user_session_params is not None:
            for k in self._user_session_params.keys():
                if hasattr(self.session_state, k):
                    user_session_params[k] = getattr(self.session_state, k)

        return user_session_params

    def _do_logout(self):
        self.session_state.allow_access = self._no_access_level
        self._logged_in = False
        # self._delete_cookie_cache()
        if callable(self._logout_callback):
            self._logout_callback()

        st.rerun()

    def _do_url_params(self):
        if self._allow_url_nav:

            query_params = st.query_params
            if 'selected' in query_params:
                # and (query_params['selected'])[0] != self.session_state.previous_app:
                if query_params['selected'] != 'None' and query_params['selected'] != self.session_state.selected_app:
                    self.session_state.other_nav_app = query_params['selected']
                    del query_params['selected']

    def enable_guest_access(self, guest_access_level=1, guest_username='guest'):
        """
        This method will auto login a guest user when the app is secured with a login app, this will allow fora guest user to by-pass the login app and gain access to the other apps that the assigned access level will allow.
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
        This method is the entry point for the MultiApp, just like a single Streamlit app, you simply setup the additional apps and then call this method to begin.
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

        if self.session_state.allow_access > self._no_access_level or self._login_app is None:
            if callable(self._login_callback):
                if not self.session_state.logged_in:
                    self.session_state.logged_in = True
                    self._login_callback()

            if self._nav_item_count == 0:
                self._default()
            else:
                self._build_nav_menu()
                self._run_selected()
        elif self.session_state.allow_access < self._no_access_level:
            self.session_state.current_user = self._guest_name
            self._unsecure_app.run()
        else:
            self.session_state.logged_in = False
            self.session_state.current_user = None
            self.session_state.access_hash = None
            self._login_app.run()

    def _default(self):
        st.header('Welcome to Multilit')
        st.write(
            'Thank you for your enthusiasum and looking to run the MultiApp as quickly as possible, for maximum effect, please add a child app by one of the methods below.')

        st.write('Method 1 (easiest)')

        st.code("""
#when we import multilit, we automatically get all of Streamlit
import multilit
app = multilit.MultiApp(title='Simple Multi-Page App')
@app.addapp()
def my_cool_function():
  hy.info('Hello from app 1')
        """
                )

        st.write('Method 2 (more fun)')

        st.code("""
    from multilit import MultiHeadApp
    import streamlit as st
    #create a child app wrapped in a class with all your code inside the run() method.
    class CoolApp(MultiHeadApp):
        def run(self):
            st.info('Hello from cool app 1')
    #when we import multilit, we automatically get all of Streamlit
    import multilit
    app = multilit.MultiApp(title='Simple Multi-Page App')
    app.add_app("My Cool App", icon="📚", app=CoolApp(title="Cool App"))
            """
                )

        st.write(
            'Once we have added atleast one child application, we just run the parent app!')

        st.code("""
    app.run()
            """)

        st.write(
            'For example you get can going super quick with a couple of functions and a call to Multilit App run().')

        st.code("""
        #when we import multilit, we automatically get all of Streamlit
        import multilit
        app = multilit.MultiApp(title='Simple Multi-Page App')
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

    def logout_callback(self, func):
        """
        This is a decorate to add a function to be run when a user is logged out.
        """

        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._logout_callback = my_wrap
        return my_wrap

    def login_callback(self, func):
        """
        This is a decorate to add a function to be run when a user is first logged in.
        """

        def my_wrap(*args, **kwargs):
            return func(*args, **kwargs)

        self._login_callback = my_wrap
        return my_wrap

