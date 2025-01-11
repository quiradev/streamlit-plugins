import streamlit
from streamlit.elements.widgets.button_group import SingleOrMultiSelectSerde, V
from streamlit.errors import StreamlitAPIException
from streamlit.string_util import validate_material_icon
from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
from streamlit.proto.ButtonGroup_pb2 import ButtonGroup as ButtonGroupProto

from streamlit_plugins.extension.button_group import st_button_group

if "http://localhost:8501" not in _DEFAULT_ALLOWED_MESSAGE_ORIGINS:
    streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")

import time

import streamlit as st
from typing import Literal

from .inject_script import inject_crossorigin_interface, change_theme_coi
from .entity import ThemeInput, ThemeInfo

KEY = "ThemeChangerComponent"

DEFAULT_CUSTOM_THEMES = {
    "dark": ThemeInput(
        name="dark",
        order=1,
        icon="brightness_2",
        themeInfo=ThemeInfo(
            base=1,
            primaryColor="#079E5A",
            backgroundColor="#423E2E",
            secondaryBackgroundColor="#2D3419",
            textColor="#D7FF94",
            font=2,
            widgetBackgroundColor="#625625",
            widgetBorderColor="#079E5A",
            skeletonBackgroundColor="#545B3C",
            bodyFont='"Victor Mono Italic", Source Sans Pro, sans-serif',
            codeFont='"Victor Mono", Source Code Pro, monospace',
            fontFaces=[
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
            radii={
                "checkboxRadius": 3,
                "baseWidgetRadius": 6
            },
            fontSizes={
                "tinyFontSize": 10,
                "smallFontSize": 12,
                "baseFontSize": 14
            }
        )
    ),
    "light": ThemeInput(
        name="light",
        order=2,
        icon="wb_sunny",
        themeInfo=ThemeInfo(
            base=0,
            primaryColor="#00BD00",
            backgroundColor="#FDFEFE",
            secondaryBackgroundColor="#D2ECCD",
            textColor="#050505",
            font=0,
            widgetBackgroundColor="#FFFFFF",
            widgetBorderColor="#D3DAE8",
            skeletonBackgroundColor="#CCDDEE",
            bodyFont="Inter, Source Sans Pro, sans-serif",
            codeFont="Apercu Mono, Source Code Pro, monospace",
            fontFaces=[
                {
                    "family": "Inter",
                    "url": "https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
                    "weight": 400
                }
            ],
            radii={
                "checkboxRadius": 3,
                "baseWidgetRadius": 6
            },
            fontSizes={
                "tinyFontSize": 10,
                "smallFontSize": 12,
                "baseFontSize": 14
            }
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
    themes_data: dict[str, ThemeInput] = None,
    render_mode: Literal["button", "pills"] = "button",
    rerun_whole_st: bool = False,
    timeout_rendering_theme_change: float = 0.2
):
    """
    A Streamlit component to change the theme of the app.
    """
    # -------------------------
    # Verification key index (Is different o each instance)
    if KEY not in st.session_state:
        st.session_state[KEY] = True

    i = 0
    if f"{KEY}_{i}_{render_mode}_check" in st.session_state:
        # Exist a button with this value
        if st.session_state[f"{KEY}_{i}_{render_mode}_check"]:
            i += 1
            st.session_state[f"{KEY}_{i}_{render_mode}_check"] = False

    unique_key = f"{KEY}_{i}"
    # -------------------------

    if themes_data is None:
        themes_data = DEFAULT_THEMES.copy()

    # Sort themes by order
    theme_names = sorted(themes_data.keys(), key=lambda k: (themes_data[k].order, themes_data[k].name))

    # -------------------------
    # Theme changer logic (Is common to all instances)
    if f"{KEY}_theme_index" not in st.session_state:
        st.session_state[f"{KEY}_theme_index"] = theme_names[0]

    if "COI_injected" not in st.session_state:
        inject_crossorigin_interface()
        st.session_state["COI_injected"] = True
        change_theme_coi(KEY, themes_data[st.session_state[f"{KEY}_theme_index"]])
        time.sleep(0.1)  # Ensure enough time for client to load the script

    # -------------------------

    @st.fragment
    def button_mode():
        theme_index: str = st.session_state[f"{KEY}_theme_index"]
        change_theme = st.button(
            icon=themes_data[theme_index].icon, label="Change Theme",
            key=f"{unique_key}_button"
        )
        st.session_state[f"{unique_key}_{i}_button_check"] = True

        if change_theme:
            current_key = theme_names[theme_names.index(theme_index)]
            next_key = theme_names[(theme_names.index(current_key) + 1) % len(theme_names)]
            theme_index = next_key
            print(f"Changing theme to {themes_data[theme_index].name}")
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
            key=f"{unique_key}_pills",
        )
        st.session_state[f"{unique_key}_{i}_pills_check"] = True

        if new_theme_index:
            theme_index: str = st.session_state[f"{KEY}_theme_index"]
            # new_theme_index = st.session_state[f"{unique_key}_pills"]
            if theme_index != new_theme_index:
                st.session_state[f"{KEY}_theme_index"] = new_theme_index
                change_theme_coi(KEY, themes_data[new_theme_index])
                time.sleep(timeout_rendering_theme_change)
                if rerun_whole_st:
                    st.rerun()
                else:
                    st.rerun(scope="fragment")

    if render_mode == "button":
        button_mode()

    if render_mode == "pills":
        with st.sidebar:
            pills_mode()
