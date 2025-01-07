import streamlit
from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")
import time

import streamlit as st
from typing import Literal

from .inject_script import inject_crossorigin_interface, change_theme_coi

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


def st_theme_changer(
    themes_data: list[dict] = None,
    render_mode: Literal["button"] = "button",
    key="ThemeChangerComponent",
):
    """
    A Streamlit component to change the theme of the app.
    """
    if themes_data is None:
        themes_data = DEFAULT_THEMES

    if f"{key}_theme_index" not in st.session_state:
        st.session_state[f"{key}_theme_index"] = 0
    # ctx = get_script_run_ctx()

    if "COI_injected" not in st.session_state:
        inject_crossorigin_interface()
        st.session_state["COI_injected"] = True
        change_theme_coi(key, themes_data, st.session_state[f"{key}_theme_index"])
        time.sleep(0.1)

    @st.fragment
    def button_mode():
        theme_index = st.session_state[f"{key}_theme_index"]
        change_theme = st.button(icon=f":material/{themes_data[theme_index].get('icon', 'format_paint')}:", label="Change Theme")

        if change_theme:
            theme_index = (theme_index + 1) % len(themes_data)
            print(f"Changing theme to {themes_data[theme_index]['name']}")
            st.session_state[f"{key}_theme_index"] = theme_index

            change_theme_coi(key, themes_data, theme_index)
            time.sleep(0.2)
            # TODO: How to prevent to make a rerun and change button icon without rerun?
            st.rerun(scope="fragment")

    # @st.fragment
    # def pills_mode():
    #     selection = st.pills(
    #         "Change Theme",
    #         options=themes_data,
    #         format_func=lambda option: f":material/{option['icon']}:",
    #         selection_mode="single",
    #     )
    #     if selection is None:
    #         return
    #
    #     theme_index = st.session_state[f"{key}_theme_index"]
    #     new_theme_index = themes_data.index(selection)
    #     if theme_index != new_theme_index:
    #         st.session_state[f"{key}_theme_index"] = theme_index
    #         change_theme_coi(key, themes_data, theme_index)

    if render_mode == "button":
        button_mode()

    # if render_mode == "pill":
    #     pills_mode()

