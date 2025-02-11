import streamlit
from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
from streamlit.errors import StreamlitAPIException

from streamlit_plugins.extension.button_group import st_button_group

if "http://localhost:8501" not in _DEFAULT_ALLOWED_MESSAGE_ORIGINS:
    streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")

import time

import streamlit as st
from typing import Literal

from .inject_script import inject_crossorigin_interface, change_theme_coi
from .entity import ThemeInput, ThemeInfo, ThemeBaseLight, ThemeBaseDark

KEY = "ThemeChangerComponent"

DEFAULT_CUSTOM_THEMES = {
    "dark": ThemeInput(
        name="dark",
        order=1,
        icon="brightness_2",
        themeInfo=ThemeInfo(
            base=ThemeBaseLight.base,
            primaryColor=ThemeBaseLight.primaryColor,
            backgroundColor=ThemeBaseLight.backgroundColor,
            secondaryBackgroundColor=ThemeBaseLight.secondaryBackgroundColor,
            textColor=ThemeBaseLight.textColor,
            font=ThemeBaseLight.font,
            widgetBackgroundColor=ThemeBaseLight.widgetBackgroundColor,
            widgetBorderColor=ThemeBaseLight.widgetBorderColor,
            skeletonBackgroundColor=ThemeBaseLight.skeletonBackgroundColor,
            bodyFont=ThemeBaseLight.bodyFont,
            codeFont=ThemeBaseLight.codeFont,
            fontFaces=ThemeBaseLight.fontFaces,
            radii=ThemeBaseLight.radii,
            fontSizes=ThemeBaseLight.fontSizes
        )
    ),
    "light": ThemeInput(
        name="light",
        order=2,
        icon="wb_sunny",
        themeInfo=ThemeInfo(
            base=ThemeBaseDark.base,
            primaryColor=ThemeBaseDark.primaryColor,
            backgroundColor=ThemeBaseDark.backgroundColor,
            secondaryBackgroundColor=ThemeBaseDark.secondaryBackgroundColor,
            textColor=ThemeBaseDark.textColor,
            font=ThemeBaseDark.font,
            widgetBackgroundColor=ThemeBaseDark.widgetBackgroundColor,
            widgetBorderColor=ThemeBaseDark.widgetBorderColor,
            skeletonBackgroundColor=ThemeBaseDark.skeletonBackgroundColor,
            bodyFont=ThemeBaseDark.bodyFont,
            codeFont=ThemeBaseDark.codeFont,
            fontFaces=ThemeBaseDark.fontFaces,
            radii=ThemeBaseDark.radii,
            fontSizes=ThemeBaseDark.fontSizes
        )
    )
}
DEFAULT_THEMES = {
    "light": ThemeInput(
        name="light",
        order=0,
        icon=":material/wb_sunny:",
        themeInfo=ThemeInfo(
            base=0
        )
    ),
    "dark": ThemeInput(
        name="dark",
        order=1,
        icon=":material/brightness_2:",
        themeInfo=ThemeInfo(
            base=1
        )
    )
}


def st_theme_changer(
    themes_data: dict[str, ThemeInput] | None = None,
    render_mode: Literal["init", "change", "next", "button", "pills"] = "button",
    default_init_theme_name: str | None = None,
    rerun_whole_st: bool = False,
    timeout_rendering_theme_change: float = 0.2,
    key: str = "default",
):
    """
    A Streamlit component to change the theme of the app.
    """
    # -------------------------
    # Verification key index (Is different o each instance)
    if KEY not in st.session_state:
        st.session_state[KEY] = True

    # i = 0
    # if render_mode != "none":
    #     if f"{KEY}_{i}_{render_mode}_check" in st.session_state:
    #         # Exist a button with this value
    #         if st.session_state[f"{KEY}_{i}_{render_mode}_check"]:
    #             i += 1
    #             st.session_state[f"{KEY}_{i}_{render_mode}_check"] = False

    unique_key = f"{KEY}_{key}"
    # -------------------------

    if themes_data is None:
        themes_data = DEFAULT_THEMES.copy()

    # Sort themes by order
    theme_names = sorted(themes_data.keys(), key=lambda k: (themes_data[k].order, themes_data[k].name))

    # -------------------------
    # Theme changer logic (Is common to all instances)
    if f"{KEY}_theme_index" not in st.session_state:
        st.session_state[f"{KEY}_theme_index"] = theme_names[0]

    if f"{KEY}_COI_injected" not in st.session_state:
        inject_crossorigin_interface()
        st.session_state[f"{KEY}_COI_injected"] = True

        st_void = st.empty()
        with st_void:
            change_theme_coi(KEY, themes_data[st.session_state[f"{KEY}_theme_index"]])
        time.sleep(0.1)  # Ensure enough time for client to load the script
        st_void.empty()

    render_init_condition = (render_mode == "init" and not st.session_state.get(f"{KEY}_init", False))

    if render_init_condition or render_mode == "change":
        st.session_state[f"{KEY}_init"] = True
        default_init_theme_name = default_init_theme_name or st.session_state[f"{KEY}_theme_index"]
        if default_init_theme_name not in theme_names:
            raise StreamlitAPIException(f"change_none_theme_index must be in {theme_names}")

        st.session_state[f"{KEY}_theme_index"] = default_init_theme_name
    
    elif render_mode == "next":
        next_theme_index = theme_names[(theme_names.index(st.session_state[f"{KEY}_theme_index"]) + 1) % len(theme_names)]
        st.session_state[f"{KEY}_theme_index"] = next_theme_index
    
    if render_mode in ["change", "next"] or render_init_condition:
        st_void = st.empty()
        with st_void:
            change_theme_coi(KEY, themes_data[st.session_state[f"{KEY}_theme_index"]])

            if render_mode == "next" or render_mode == "change":
                if rerun_whole_st:
                    st.rerun()
        
        time.sleep(0.1)  # Ensure enough time for client to load the script
        st_void.empty()

    # -------------------------
    
    @st.fragment
    def button_mode():
        theme_index: str = st.session_state[f"{KEY}_theme_index"]
        change_theme = st.button(
            icon=themes_data[theme_index].icon, label="Change Theme",
            key=f"{unique_key}_{render_mode}"
        )
        # st.session_state[f"{unique_key}_{render_mode}_check"] = True

        if change_theme:
            current_key = theme_names[theme_names.index(theme_index)]
            next_key = theme_names[(theme_names.index(current_key) + 1) % len(theme_names)]
            theme_index = next_key
            # print(f"Changing theme to {themes_data[theme_index].name}")
            st.session_state[f"{KEY}_theme_index"] = theme_index

            change_theme_coi(KEY, themes_data[theme_index])
            time.sleep(timeout_rendering_theme_change)
            # TODO: How to prevent to make a rerun and change button icon without rerun?
            if rerun_whole_st:
                st.rerun()
            else:
                st.rerun(scope="fragment")

    @st.fragment
    def pills_mode():
        # view = st.empty()
        # if st.session_state.get(f"{unique_key}_pills") is None:
        #     st.session_state[f"{unique_key}_pills"] = st.session_state[f"{KEY}_theme_index"]
        # with view:
        new_theme_index = st_button_group(
            theme_names,
            label="Change Theme",
            default=st.session_state[f"{KEY}_theme_index"],
            format_func=lambda option: themes_data[option].icon,
            style="pills", selection_visualization="only_selected",
            keep_selection="always_visible",
            selection_mode="single",
            key=f"{unique_key}_{render_mode}",
        )
        # st.session_state[f"{unique_key}_{render_mode}_check"] = True

        if new_theme_index:
            theme_index: str = st.session_state[f"{KEY}_theme_index"]
            if theme_index != new_theme_index:
                st.session_state[f"{KEY}_theme_index"] = new_theme_index
                change_theme_coi(KEY, themes_data[new_theme_index])
                time.sleep(timeout_rendering_theme_change)
                if rerun_whole_st:
                    st.rerun()
                else:
                    st.rerun(scope="fragment")

    # ctx = get_script_run_ctx()
    # Una vez creado el fragment_id, almacenarlo, y despues recuperarlo con el fragment_storage
    # ctx.fragment_storage.get
    # Despues, si se quiere hacer un rerun del mismo fragment y de otros, recuperar los fragment_id y lanzar el RerunData

    # ctx.script_requests.request_rerun(
    #     RerunData(
    #         query_string=query_string,
    #         page_script_hash=page_script_hash,
    #         fragment_id_queue=_new_fragment_id_queue(ctx, scope),
    #         is_fragment_scoped_rerun=scope == "fragment",
    #     )
    # )
    # # Force a yield point so the runner can do the rerun
    # st.empty()

    # -------------------------

    if render_mode == "button":
        button_mode()

    elif render_mode == "pills":
        pills_mode()


def get_active_theme_key() -> str | None:
    return st.session_state.get(f"{KEY}_theme_index", None)