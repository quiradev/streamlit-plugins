import sys


try:
    if '_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper' not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

import streamlit as st

from streamlit_plugins.components.theme_changer import get_active_theme_key, st_theme_changer
from streamlit_plugins.components.theme_changer.entity import ThemeInfo, ThemeInput, ThemeBaseLight, ThemeBaseDark

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

st.title("Theme Changer Component")
st.caption("Just push the button to change the theme! On the client side, of course.")



init_theme_data = dict(
    soft_light=ThemeInput(
        name="Soft Sunrise",
        icon=":material/sunny_snowing:",
        order=0,
        themeInfo=ThemeInfo(
            base=ThemeBaseLight.base,
            primaryColor="#6100FF",
            backgroundColor="#EFF4FF",
            secondaryBackgroundColor="#E7EEF5",
            textColor="#000000",
            widgetBackgroundColor="#F3F5F7",
            widgetBorderColor="#9000FF",
            skeletonBackgroundColor="#E0E0E0",
            bodyFont=ThemeBaseLight.bodyFont,
            codeFont=ThemeBaseLight.codeFont,
            fontFaces=ThemeBaseLight.fontFaces,
        )
    ),
    soft_dark=ThemeInput(
        name="Dark Midnight",
        icon=":material/nights_stay:",
        order=1,
        themeInfo=ThemeInfo(
            base=ThemeBaseDark.base,
            primaryColor="#7AF8FF",
            backgroundColor="#000000",
            secondaryBackgroundColor="#045367",
            textColor="#f0f8ff",
            widgetBackgroundColor="#092927",
            widgetBorderColor="#75D9FF",
            skeletonBackgroundColor="#365252",
            bodyFont=ThemeBaseDark.bodyFont,
            codeFont=ThemeBaseDark.codeFont,
            fontFaces=ThemeBaseDark.fontFaces,
        )
    ),
    sepia=ThemeInput(
        name="Sepia",
        icon=":material/gradient:",
        order=2,
        themeInfo=ThemeInfo(
            base=ThemeBaseLight.base,
            primaryColor="#FF0004",
            backgroundColor="#F9F9E0",
            secondaryBackgroundColor="#EFEFB4",
            textColor="#000000",
            widgetBackgroundColor="#F5F5D7",
            widgetBorderColor="#E2DEAD",
            skeletonBackgroundColor="#F5F5DC",
            bodyFont=ThemeBaseLight.bodyFont,
            codeFont=ThemeBaseLight.codeFont,
            fontFaces=ThemeBaseLight.fontFaces,
        )
    )
)

if st.session_state.get("theme_data") is None:
    st.session_state["theme_data"] = init_theme_data

theme_data = st.session_state["theme_data"]

st_theme_changer(themes_data=theme_data, render_mode="init", default_init_theme_name="soft_dark")
st_theme_changer(themes_data=theme_data, rerun_whole_st=True)

with st.expander("Theme Editor", expanded=False):
    with st.container(border=False):
        theme_keys = list(theme_data.keys())
        tabs = st.tabs(theme_keys)
        for i, tab in enumerate(tabs):
            theme_key = theme_keys[i]
            with tab:
                with st.form(key=f"{theme_key}_form", border=False):
                    col1, col2, col3 = st.columns(3)
                    name = col1.text_input("Theme Label", value=theme_data[theme_key].name, key=f"{theme_key}_text_input")
                    icon = col2.text_input("Theme Icon", value=theme_data[theme_key].icon, key=f"{theme_key}_icon_input")
                    order = col3.number_input("Order", value=theme_data[theme_key].order, key=f"{theme_key}_order_input")
                    
                    col1, col2, col3 = st.columns(3)
                    primaryColor = col1.color_picker("Primary Color", value=theme_data[theme_key].themeInfo.primaryColor, key=f"{theme_key}_primary_color_input")
                    textColor = col2.color_picker("Text Color", value=theme_data[theme_key].themeInfo.textColor, key=f"{theme_key}_text_color_input")
                    
                    col1, col2, col3 = st.columns(3)
                    backgroundColor = col1.color_picker("Background Color", value=theme_data[theme_key].themeInfo.backgroundColor, key=f"{theme_key}_background_color_input")
                    secondaryBackgroundColor = col2.color_picker("Secondary Background Color", value=theme_data[theme_key].themeInfo.secondaryBackgroundColor, key=f"{theme_key}_secondary_background_color_input")
                    skeletonBackgroundColor = col3.color_picker("Skeleton Background Color", value=theme_data[theme_key].themeInfo.skeletonBackgroundColor, key=f"{theme_key}_skeleton_background_color_input")
                    
                    col1, col2, col3 = st.columns(3)
                    widgetBackgroundColor = col1.color_picker("Widget Background Color", value=theme_data[theme_key].themeInfo.widgetBackgroundColor, key=f"{theme_key}_widget_background_color_input")
                    widgetBorderColor = col2.color_picker("Widget Border Color", value=theme_data[theme_key].themeInfo.widgetBorderColor, key=f"{theme_key}_widget_border_color_input")
                    baseWidgetRadius = col3.number_input("Base Widget Radius", value=theme_data[theme_key].themeInfo.radii["baseWidgetRadius"], key=f"{theme_key}_base_widget_radius_input")

                    col1, col2, col3 = st.columns(3)
                    checkbox_radius = col1.number_input("Checkbox Radius", value=theme_data[theme_key].themeInfo.radii["checkboxRadius"], key=f"{theme_key}_checkbox_radius_input")
                    col2.checkbox("Example Checkbox", key=f"{theme_key}_example_checkbox")
                    
                    col1, col2, col3 = st.columns(3)
                    tiny_font_size = col1.number_input("Tiny Font Size", value=theme_data[theme_key].themeInfo.fontSizes["tinyFontSize"], key=f"{theme_key}_tiny_font_size_input")
                    small_font_size = col2.number_input("Small Font Size", value=theme_data[theme_key].themeInfo.fontSizes["smallFontSize"], key=f"{theme_key}_small_font_size_input")
                    base_font_size = col3.number_input("Base Font Size", value=theme_data[theme_key].themeInfo.fontSizes["baseFontSize"], key=f"{theme_key}_base_font_size_input")

                    col1, col2 = st.columns(2)
                    bodyFont = col1.text_input("Body Font", value=theme_data[theme_key].themeInfo.bodyFont, key=f"{theme_key}_body_font_input")
                    codeFont = col2.text_input("Code Font", value=theme_data[theme_key].themeInfo.codeFont, key=f"{theme_key}_code_font_input")
                    # fontFaces = col3.text_area("Font Faces", value=str(theme_data[theme_key].themeInfo.fontFaces), key=f"{theme_key}_font_faces_input")


                    theme_data[theme_key].name = name
                    theme_data[theme_key].icon = icon
                    theme_data[theme_key].order = order
                    theme_data[theme_key].themeInfo.primaryColor = primaryColor
                    theme_data[theme_key].themeInfo.backgroundColor = backgroundColor
                    theme_data[theme_key].themeInfo.secondaryBackgroundColor = secondaryBackgroundColor
                    theme_data[theme_key].themeInfo.textColor = textColor
                    theme_data[theme_key].themeInfo.widgetBackgroundColor = widgetBackgroundColor
                    theme_data[theme_key].themeInfo.widgetBorderColor = widgetBorderColor
                    theme_data[theme_key].themeInfo.skeletonBackgroundColor = skeletonBackgroundColor
                    theme_data[theme_key].themeInfo.bodyFont = bodyFont
                    theme_data[theme_key].themeInfo.codeFont = codeFont
                    theme_data[theme_key].themeInfo.radii["baseWidgetRadius"] = baseWidgetRadius
                    theme_data[theme_key].themeInfo.fontSizes["tinyFontSize"] = tiny_font_size
                    theme_data[theme_key].themeInfo.fontSizes["smallFontSize"] = small_font_size
                    theme_data[theme_key].themeInfo.fontSizes["baseFontSize"] = base_font_size
                    
                    update_theme = st.form_submit_button("Save")
                    if update_theme:
                        st.session_state["theme_data"] = theme_data
                        if get_active_theme_key() == theme_key:
                            st_theme_changer(themes_data=theme_data, render_mode="change", default_init_theme_name=theme_key)
                            st.rerun()

with st.sidebar:
    st_theme_changer(
        themes_data=theme_data, render_mode="pills",
        rerun_whole_st=True, key="first_pills"
    )

