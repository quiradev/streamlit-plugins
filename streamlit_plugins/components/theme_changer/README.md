# Change Theme (on the Client Side!)

## Code example
```python
import streamlit as st

from streamlit_plugins.components.theme_changer import st_theme_changer

st.title("Theme Changer Component")
st.caption("Just push the button to change the theme! On the client side, of course.")
# specify the primary menu definition
st_theme_changer()

st_theme_changer(render_mode="pills")
```

## Custom Config

The theme name can’t be "Dark" or "Light" since those are reserved for the default Streamlit themes.

### Editable custom theme app

![Customize Theme App](https://raw.githubusercontent.com/quiradev/streamlit-plugins/main/resources/theme_changer_customizable_small.gif)

```python
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

```

## All Theme Configurations (CSS Properties)

### Theme Configuration Table

Here’s an overview of the theme configuration options and what they do:

| **Key**                     | **Value**                                                                      | **Description**                                                                                   |
|-----------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `primaryColor`              | `"#1A6CE7"`                                                                    | The main accent color used throughout your app. For example, widgets like `st.checkbox`, `st.slider`, and `st.text_input` (when focused) use this color.                   |
| `backgroundColor`           | `"#FFFFFF"`                                                                    | The main background color of your app.                                                           |
| `secondaryBackgroundColor`  | `"#F5F5F5"`                                                                    | Used as a secondary background color, like for the sidebar or interactive widgets.               |
| `textColor`                 | `"#1A1D21"`                                                                    | Controls the text color for most elements in your app.                                            |
| `font`                      | `0` `1` `2` [`"sans serif" ` `"serif"` `"monospace"`]                          | Sets the font used in your app. Options are `"sans serif"`, `"serif"`, or `"monospace"`. Defaults to `"sans serif"` if unset.                             |
| `base`                      | `0` `1` [`light` `dark`]                                                       | Lets you create custom themes by slightly modifying one of the preset Streamlit themes.          |
| *`widgetBackgroundColor`     | `"#FFFFFF"`                                                                    | Background color for widgets like inputs or sliders.                                              |
| *`widgetBorderColor`         | `"#D3DAE8"`                                                                    | Border color for widgets and interactive elements.                                                |
| *`skeletonBackgroundColor`   | `"#CCDDEE"`                                                                    | Background color for loading placeholders (skeletons).                                            |
| *`bodyFont`                  | `"Inter", "Source Sans Pro", sans-serif`                                       | Default font for body text.                                                                       |
| *`codeFont`                  | `"Apercu Mono", "Source Code Pro", monospace`                                  | Font used for code or monospaced text.                                                            |
| *`fontFaces`                 | [Array of font families with URLs and weights](#font-faces-details-fontfaces-) | Custom fonts, including font-family, URL, and weight (e.g., Inter, Apercu Mono).                  |
| *`radii.checkboxRadius`      | `3`                                                                            | Border radius for checkboxes.                                                                     |
| *`radii.baseWidgetRadius`    | `6`                                                                            | Border radius for widgets like buttons or inputs.                                                 |
| *`fontSizes.tinyFontSize`    | `10`                                                                           | Font size for tiny text (e.g., labels).                                                           |
| *`fontSizes.smallFontSize`   | `12`                                                                           | Font size for small text, like secondary descriptions.                                             |
| *`fontSizes.baseFontSize`    | `14`                                                                           | Base font size for regular text.                                                                  |

> The parameters marked with a * are new in Streamlit’s configuration. You can tweak them to adjust fonts and font sizes.  
> Properties with a `.` in their names are part of nested objects. Details about these nested objects are provided below.

### Font Faces Details `"fontFaces": [...]`

| **`"family"`**       | **`"url"`**                                                                                        | **`"weight"`** | **Description**                         |
|------------------|------------------------------------------------------------------------------------------------|------------|-----------------------------------------|
| `Inter`          | `https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19`                                  | 400        | Regular weight of the Inter font.       |
| `Inter`          | `https://rsms.me/inter/font-files/Inter-SemiBold.woff2?v=3.19`                                 | 600        | Semi-bold weight of the Inter font.     |
| `Inter`          | `https://rsms.me/inter/font-files/Inter-Bold.woff2?v=3.19`                                     | 700        | Bold weight of the Inter font.          |
| `Apercu Mono`    | `https://app.snowflake.com/static/2c4863733dec5a69523e.woff2`                                  | 400        | Regular weight of the Apercu Mono font. |
| `Apercu Mono`    | `https://app.snowflake.com/static/e903ae189d31a97e231e.woff2`                                  | 500        | Medium weight of the Apercu Mono font.  |
| `Apercu Mono`    | `https://app.snowflake.com/static/32447307374154c88bc0.woff2`                                  | 700        | Bold weight of the Apercu Mono font.    |

### Theme Configuration: Properties and Data Types

### Enum Descriptions

#### Font Family (`font`)
- `0` (SANS_SERIF): Standard sans-serif font family.  
- `1` (SERIF): Standard serif font family.  
- `2` (MONOSPACE): Monospaced font family, often for code.  

#### Base Theme (`base`)
- `0` (LIGHT): Light base theme.  
- `1` (DARK): Dark base theme.  

### Nested Object Details

#### `radii`
| **Sub-Property**      | **Type** | **Description**                                      |
|-----------------------|----------|------------------------------------------------------|
| `checkboxRadius`      | `number` | Radius for checkboxes.                               |
| `baseWidgetRadius`    | `number` | Radius for widgets like buttons or inputs.           |

#### `fontSizes`
| **Sub-Property**      | **Type** | **Description**                                      |
|-----------------------|----------|------------------------------------------------------|
| `tinyFontSize`        | `number` | Font size for tiny text.                             |
| `smallFontSize`       | `number` | Font size for small text.                            |
| `baseFontSize`        | `number` | Default font size for regular text.                  |

---

### Workaround for Switching Themes Without Custom Components

You can use query parameters in the URL to switch between light and dark themes. However, this requires a page reload and won’t allow custom themes. Examples:

- `?embed_options=light_theme`  
- `?embed_options=dark_theme`  

---

### Override Base "Dark" or "Light" Themes (Maybe in future 🤞0)

Currently, you can’t override the default "Dark" or "Light" themes directly in Streamlit. Until the Streamlit team releases support for the `SET_CUSTOM_THEME_CONFIG` event, you’re limited to modifying the available properties listed above. But for your understanding, here's the all properties that streamlit team can configurate the frontend styles for Dark and Light themes.

```json
{
    "name": "Dark",
    "emotion": {
        "inSidebar": false,
        "breakpoints": {
            "hideWidgetDetails": 180,
            "hideNumberInputControls": 120,
            "sm": "576px",
            "columns": "640px",
            "md": "768px"
        },
        "colors": {
            "transparent": "transparent",
            "black": "#000000",
            "white": "#ffffff",
            "gray10": "#fafafa",
            "gray20": "#f0f2f6",
            "gray30": "#e6eaf1",
            "gray40": "#d5dae5",
            "gray50": "#bfc5d3",
            "gray60": "#a3a8b8",
            "gray70": "#808495",
            "gray80": "#555867",
            "gray85": "#31333F",
            "gray90": "#262730",
            "gray100": "#0e1117",
            "red10": "#fff0f0",
            "red20": "#ffdede",
            "red30": "#ffc7c7",
            "red40": "#ffabab",
            "red50": "#ff8c8c",
            "red60": "#ff6c6c",
            "red70": "#ff4b4b",
            "red80": "#ff2b2b",
            "red90": "#bd4043",
            "red100": "#7d353b",
            "orange10": "#fffae8",
            "orange20": "#fff6d0",
            "orange30": "#ffecb0",
            "orange40": "#ffe08e",
            "orange50": "#ffd16a",
            "orange60": "#ffbd45",
            "orange70": "#ffa421",
            "orange80": "#ff8700",
            "orange90": "#ed6f13",
            "orange100": "#d95a00",
            "yellow10": "#ffffe1",
            "yellow20": "#ffffc2",
            "yellow30": "#ffffa0",
            "yellow40": "#ffff7d",
            "yellow50": "#ffff59",
            "yellow60": "#fff835",
            "yellow70": "#ffe312",
            "yellow80": "#faca2b",
            "yellow90": "#edbb16",
            "yellow100": "#dea816",
            "yellow110": "#916e10",
            "green10": "#dffde9",
            "green20": "#c0fcd3",
            "green30": "#9ef6bb",
            "green40": "#7defa1",
            "green50": "#5ce488",
            "green60": "#3dd56d",
            "green70": "#21c354",
            "green80": "#09ab3b",
            "green90": "#158237",
            "green100": "#177233",
            "blueGreen10": "#dcfffb",
            "blueGreen20": "#bafff7",
            "blueGreen30": "#93ffee",
            "blueGreen40": "#6bfde3",
            "blueGreen50": "#45f4d5",
            "blueGreen60": "#20e7c5",
            "blueGreen70": "#00d4b1",
            "blueGreen80": "#29b09d",
            "blueGreen90": "#2c867c",
            "blueGreen100": "#246e69",
            "lightBlue10": "#e0feff",
            "lightBlue20": "#bffdff",
            "lightBlue30": "#9af8ff",
            "lightBlue40": "#73efff",
            "lightBlue50": "#4be4ff",
            "lightBlue60": "#24d4ff",
            "lightBlue70": "#00c0f2",
            "lightBlue80": "#00a4d4",
            "lightBlue90": "#0d8cb5",
            "lightBlue100": "#15799e",
            "blue10": "#e4f5ff",
            "blue20": "#c7ebff",
            "blue30": "#a6dcff",
            "blue40": "#83c9ff",
            "blue50": "#60b4ff",
            "blue60": "#3d9df3",
            "blue70": "#1c83e1",
            "blue80": "#0068c9",
            "blue90": "#0054a3",
            "blue100": "#004280",
            "purple10": "#f5ebff",
            "purple20": "#ebd6ff",
            "purple30": "#dbbbff",
            "purple40": "#c89dff",
            "purple50": "#b27eff",
            "purple60": "#9a5dff",
            "purple70": "#803df5",
            "purple80": "#6d3fc0",
            "purple90": "#583f84",
            "purple100": "#3f3163",
            "bgColor": "#0e1117",
            "secondaryBg": "#262730",
            "bodyText": "#fafafa",
            "warning": "#ffffc2",
            "warningBg": "rgba(255, 227, 18, 0.2)",
            "success": "#dffde9",
            "successBg": "rgba(61, 213, 109, 0.2)",
            "infoBg": "rgba(61, 157, 243, 0.2)",
            "info": "#c7ebff",
            "danger": "#ffdede",
            "dangerBg": "rgba(255, 108, 108, 0.2)",
            "primary": "#ff4b4b",
            "disabled": "#808495",
            "lightestGray": "#f0f2f6",
            "lightGray": "#e6eaf1",
            "gray": "#a3a8b8",
            "darkGray": "#808495",
            "red": "#ff2b2b",
            "blue": "#0068c9",
            "green": "#09ab3b",
            "yellow": "#faca2b",
            "linkText": "hsla(209, 100%, 59%, 1)",
            "fadedText05": "rgba(250, 250, 250, 0.1)",
            "fadedText10": "rgba(250, 250, 250, 0.2)",
            "fadedText20": "rgba(250, 250, 250, 0.3)",
            "fadedText40": "rgba(250, 250, 250, 0.4)",
            "fadedText60": "rgba(250, 250, 250, 0.6)",
            "bgMix": "rgba(26, 28, 36, 1)",
            "darkenedBgMix100": "hsla(228, 16%, 72%, 1)",
            "darkenedBgMix25": "rgba(172, 177, 195, 0.25)",
            "darkenedBgMix15": "rgba(172, 177, 195, 0.15)",
            "lightenedBg05": "hsla(220, 24%, 10%, 1)",
            "borderColor": "rgba(250, 250, 250, 0.2)",
            "borderColorLight": "rgba(250, 250, 250, 0.1)",
            "codeTextColor": "#09ab3b",
            "codeHighlightColor": "rgba(26, 28, 36, 1)",
            "metricPositiveDeltaColor": "#09ab3b",
            "metricNegativeDeltaColor": "#ff2b2b",
            "metricNeutralDeltaColor": "rgba(250, 250, 250, 0.6)",
            "docStringModuleText": "#fafafa",
            "docStringTypeText": "#21c354",
            "docStringContainerBackground": "rgba(38, 39, 48, 0.4)",
            "headingColor": "#fafafa",
            "navTextColor": "#bfc5d3",
            "navActiveTextColor": "#fafafa",
            "navIconColor": "#808495",
            "sidebarControlColor": "#fafafa"
        },
        "fonts": {
            "sansSerif": "\"Source Sans Pro\", sans-serif",
            "monospace": "\"Source Code Pro\", monospace",
            "serif": "\"Source Serif Pro\", serif",
            "materialIcons": "Material Symbols Rounded"
        },
        "fontSizes": {
            "twoSm": "12px",
            "sm": "14px",
            "md": "1rem",
            "mdLg": "1.125rem",
            "lg": "1.25rem",
            "xl": "1.5rem",
            "twoXL": "1.75rem",
            "threeXL": "2.25rem",
            "fourXL": "2.75rem",
            "twoSmPx": 12,
            "smPx": 14,
            "mdPx": 16
        },
        "fontWeights": {
            "normal": 400,
            "bold": 600,
            "extrabold": 700
        },
        "genericFonts": {
            "bodyFont": "\"Source Sans Pro\", sans-serif",
            "codeFont": "\"Source Code Pro\", monospace",
            "headingFont": "\"Source Sans Pro\", sans-serif",
            "iconFont": "Material Symbols Rounded"
        },
        "iconSizes": {
            "xs": "0.5rem",
            "sm": "0.75rem",
            "md": "0.9rem",
            "base": "1rem",
            "lg": "1.25rem",
            "xl": "1.5rem",
            "twoXL": "1.8rem",
            "threeXL": "2.3rem"
        },
        "lineHeights": {
            "none": 1,
            "headings": 1.2,
            "tight": 1.25,
            "inputWidget": 1.4,
            "small": 1.5,
            "base": 1.6,
            "menuItem": 2
        },
        "radii": {
            "md": "0.25rem",
            "default": "0.5rem",
            "xl": "0.75rem",
            "xxl": "1rem",
            "full": "9999px"
        },
        "sizes": {
            "full": "100%",
            "headerHeight": "3.75rem",
            "fullScreenHeaderHeight": "2.875rem",
            "sidebarTopSpace": "6rem",
            "toastWidth": "21rem",
            "contentMaxWidth": "46rem",
            "maxChartTooltipWidth": "30rem",
            "checkbox": "1rem",
            "borderWidth": "1px",
            "smallElementHeight": "1.5rem",
            "minElementHeight": "2.5rem",
            "largestElementHeight": "4.25rem",
            "smallLogoHeight": "1.25rem",
            "defaultLogoHeight": "1.5rem",
            "largeLogoHeight": "2rem",
            "sliderThumb": "0.75rem",
            "wideSidePadding": "5rem",
            "headerDecorationHeight": "0.125rem",
            "appRunningMen": "1.6rem",
            "appStatusMaxWidth": "20rem",
            "spinnerSize": "1.375rem",
            "spinnerThickness": "0.2rem",
            "tabHeight": "2.5rem",
            "minPopupWidth": "20rem",
            "maxTooltipHeight": "18.75rem",
            "chatAvatarSize": "2rem",
            "clearIconSize": "1.5em",
            "numberInputControlsWidth": "2rem",
            "emptyDropdownHeight": "5.625rem",
            "dropdownItemHeight": "2.5rem",
            "maxDropdownHeight": "18.75rem",
            "appDefaultBottomPadding": "3.5rem"
        },
        "spacing": {
            "px": "1px",
            "none": "0",
            "threeXS": "0.125rem",
            "twoXS": "0.25rem",
            "xs": "0.375rem",
            "sm": "0.5rem",
            "md": "0.75rem",
            "lg": "1rem",
            "xl": "1.25rem",
            "twoXL": "1.5rem",
            "threeXL": "2rem",
            "fourXL": "4rem"
        },
        "zIndices": {
            "hide": -1,
            "auto": "auto",
            "base": 0,
            "priority": 1,
            "sidebar": 100,
            "menuButton": 110,
            "balloons": 1000000,
            "header": 999990,
            "sidebarMobile": 999995,
            "popupMenu": 1000040,
            "fullscreenWrapper": 1000050,
            "tablePortal": 1000110,
            "bottom": 99,
            "cacheSpinner": 101,
            "toast": 100,
            "vegaTooltips": 1000060
        }
    },
    "basewebTheme": {
        "animation": {
            "timing100": "100ms",
            "timing200": "200ms",
            "timing300": "300ms",
            "timing400": "400ms",
            "timing500": "500ms",
            "timing600": "600ms",
            "timing700": "700ms",
            "timing800": "800ms",
            "timing900": "900ms",
            "timing1000": "1000ms",
            "easeInCurve": "cubic-bezier(.8, .2, .6, 1)",
            "easeOutCurve": "cubic-bezier(.2, .8, .4, 1)",
            "easeInOutCurve": "cubic-bezier(0.4, 0, 0.2, 1)",
            "easeInQuinticCurve": "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
            "easeOutQuinticCurve": "cubic-bezier(0.23, 1, 0.32, 1)",
            "easeInOutQuinticCurve": "cubic-bezier(0.86, 0, 0.07, 1)",
            "linearCurve": "cubic-bezier(0, 0, 1, 1)"
        },
        "borders": {
            "border100": {
                "borderColor": "hsla(0, 0%, 0%, 0.04)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border200": {
                "borderColor": "hsla(0, 0%, 0%, 0.08)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border300": {
                "borderColor": "hsla(0, 0%, 0%, 0.12)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border400": {
                "borderColor": "hsla(0, 0%, 0%, 0.16)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border500": {
                "borderColor": "hsla(0, 0%, 0%, 0.2)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border600": {
                "borderColor": "hsla(0, 0%, 0%, 0.24)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "radius100": "0.5rem",
            "radius200": "0.5rem",
            "radius300": "0.5rem",
            "radius400": "0.5rem",
            "radius500": "0.5rem",
            "useRoundedCorners": true,
            "buttonBorderRadiusMini": "0.25rem",
            "buttonBorderRadius": "0.5rem",
            "checkboxBorderRadius": "0.25rem",
            "inputBorderRadiusMini": "0.25rem",
            "inputBorderRadius": "0.5rem",
            "popoverBorderRadius": "0.5rem",
            "surfaceBorderRadius": "0.5rem",
            "tagBorderRadius": "0.25rem"
        },
        "breakpoints": {
            "small": 320,
            "medium": 600,
            "large": 1136
        },
        "colors": {
            "primaryA": "#ff4b4b",
            "primaryB": "#141414",
            "primary": "#ff4b4b",
            "primary50": "#F6F6F6",
            "primary100": "#ff4b4b",
            "primary200": "#ff4b4b",
            "primary300": "#ff4b4b",
            "primary400": "#ff4b4b",
            "primary500": "#ff4b4b",
            "primary600": "#ff4b4b",
            "primary700": "#ff4b4b",
            "accent": "rgba(255, 75, 75, 0.5)",
            "accent50": "#EFF3FE",
            "accent100": "#D4E2FC",
            "accent200": "#A0BFF8",
            "accent300": "#5B91F5",
            "accent400": "#276EF1",
            "accent500": "#1E54B7",
            "accent600": "#174291",
            "accent700": "#102C60",
            "negative": "#AB1300",
            "negative50": "#FFEFED",
            "negative100": "#FED7D2",
            "negative200": "#F1998E",
            "negative300": "#E85C4A",
            "negative400": "#E11900",
            "negative500": "#AB1300",
            "negative600": "#870F00",
            "negative700": "#5A0A00",
            "warning": "#BC8B2C",
            "warning50": "#FFFAF0",
            "warning100": "#FFF2D9",
            "warning200": "#FFE3AC",
            "warning300": "#FFCF70",
            "warning400": "#FFC043",
            "warning500": "#BC8B2C",
            "warning600": "#996F00",
            "warning700": "#674D1B",
            "positive": "#048848",
            "positive50": "#E6F2ED",
            "positive100": "#ADDEC9",
            "positive200": "#66D19E",
            "positive300": "#06C167",
            "positive400": "#048848",
            "positive500": "#03703C",
            "positive600": "#03582F",
            "positive700": "#10462D",
            "white": "#ffffff",
            "black": "#000000",
            "mono100": "#0e1117",
            "mono200": "#262730",
            "mono300": "#e6eaf1",
            "mono400": "#e6eaf1",
            "mono500": "#a3a8b8",
            "mono600": "rgba(250, 250, 250, 0.4)",
            "mono700": "#a3a8b8",
            "mono800": "#fafafa",
            "mono900": "#fafafa",
            "mono1000": "#000000",
            "ratingInactiveFill": "#6B6B6B",
            "ratingStroke": "#333333",
            "bannerActionLowInfo": "#D4E2FC",
            "bannerActionLowNegative": "#FED7D2",
            "bannerActionLowPositive": "#ADDEC9",
            "bannerActionLowWarning": "#FFE3AC",
            "bannerActionHighInfo": "#1E54B7",
            "bannerActionHighNegative": "#AB1300",
            "bannerActionHighPositive": "#03703C",
            "bannerActionHighWarning": "#FFE3AC",
            "buttonPrimaryFill": "#FFFFFF",
            "buttonPrimaryText": "#FFFFFF",
            "buttonPrimaryHover": "#ff4b4b",
            "buttonPrimaryActive": "#ff4b4b",
            "buttonPrimarySelectedFill": "#ff4b4b",
            "buttonPrimarySelectedText": "#FFFFFF",
            "buttonPrimarySpinnerForeground": "#276EF1",
            "buttonPrimarySpinnerBackground": "#141414",
            "buttonSecondaryFill": "#ff4b4b",
            "buttonSecondaryText": "#FFFFFF",
            "buttonSecondaryHover": "#ff4b4b",
            "buttonSecondaryActive": "#ff4b4b",
            "buttonSecondarySelectedFill": "#ff4b4b",
            "buttonSecondarySelectedText": "#FFFFFF",
            "buttonSecondarySpinnerForeground": "#276EF1",
            "buttonSecondarySpinnerBackground": "#141414",
            "buttonTertiaryFill": "transparent",
            "buttonTertiaryText": "#FFFFFF",
            "buttonTertiaryHover": "#F6F6F6",
            "buttonTertiaryActive": "#ff4b4b",
            "buttonTertiarySelectedFill": "#ff4b4b",
            "buttonTertiarySelectedText": "#FFFFFF",
            "buttonTertiaryDisabledActiveFill": "#F6F6F6",
            "buttonTertiaryDisabledActiveText": "rgba(250, 250, 250, 0.4)",
            "buttonTertiarySpinnerForeground": "#276EF1",
            "buttonTertiarySpinnerBackground": "#ff4b4b",
            "buttonDisabledFill": "hsla(220, 24%, 10%, 1)",
            "buttonDisabledText": "rgba(250, 250, 250, 0.4)",
            "buttonDisabledActiveFill": "#a3a8b8",
            "buttonDisabledActiveText": "#0e1117",
            "buttonDisabledSpinnerForeground": "rgba(250, 250, 250, 0.4)",
            "buttonDisabledSpinnerBackground": "#d5dae5",
            "breadcrumbsText": "#000000",
            "breadcrumbsSeparatorFill": "#a3a8b8",
            "calendarBackground": "#0e1117",
            "calendarForeground": "#fafafa",
            "calendarForegroundDisabled": "#a3a8b8",
            "calendarHeaderBackground": "#262730",
            "calendarHeaderForeground": "#fafafa",
            "calendarHeaderBackgroundActive": "#262730",
            "calendarHeaderForegroundDisabled": "#d5dae5",
            "calendarDayForegroundPseudoSelected": "#fafafa",
            "calendarDayBackgroundPseudoSelectedHighlighted": "#ff4b4b",
            "calendarDayForegroundPseudoSelectedHighlighted": "#fafafa",
            "calendarDayBackgroundSelected": "#ff4b4b",
            "calendarDayForegroundSelected": "#ffffff",
            "calendarDayBackgroundSelectedHighlighted": "#ff4b4b",
            "calendarDayForegroundSelectedHighlighted": "#ffffff",
            "comboboxListItemFocus": "#262730",
            "comboboxListItemHover": "#e6eaf1",
            "fileUploaderBackgroundColor": "#262730",
            "fileUploaderBackgroundColorActive": "#F6F6F6",
            "fileUploaderBorderColorActive": "#FFFFFF",
            "fileUploaderBorderColorDefault": "#a3a8b8",
            "fileUploaderMessageColor": "#fafafa",
            "linkText": "#FFFFFF",
            "linkVisited": "#ff4b4b",
            "linkHover": "#ff4b4b",
            "linkActive": "#ff4b4b",
            "listHeaderFill": "#FFFFFF",
            "listBodyFill": "#FFFFFF",
            "progressStepsCompletedText": "#FFFFFF",
            "progressStepsCompletedFill": "#FFFFFF",
            "progressStepsActiveText": "#FFFFFF",
            "progressStepsActiveFill": "#FFFFFF",
            "toggleFill": "#FFFFFF",
            "toggleFillChecked": "#FFFFFF",
            "toggleFillDisabled": "rgba(250, 250, 250, 0.4)",
            "toggleTrackFill": "#d5dae5",
            "toggleTrackFillDisabled": "#262730",
            "tickFill": "hsla(220, 24%, 10%, 1)",
            "tickFillHover": "#262730",
            "tickFillActive": "#262730",
            "tickFillSelected": "#ff4b4b",
            "tickFillSelectedHover": "#ff4b4b",
            "tickFillSelectedHoverActive": "#ff4b4b",
            "tickFillError": "#FFEFED",
            "tickFillErrorHover": "#FED7D2",
            "tickFillErrorHoverActive": "#F1998E",
            "tickFillErrorSelected": "#E11900",
            "tickFillErrorSelectedHover": "#AB1300",
            "tickFillErrorSelectedHoverActive": "#870F00",
            "tickFillDisabled": "rgba(250, 250, 250, 0.4)",
            "tickBorder": "#a3a8b8",
            "tickBorderError": "#E11900",
            "tickMarkFill": "#f0f2f6",
            "tickMarkFillError": "#FFFFFF",
            "tickMarkFillDisabled": "hsla(220, 24%, 10%, 1)",
            "sliderTrackFill": "#d5dae5",
            "sliderHandleFill": "#E2E2E2",
            "sliderHandleFillDisabled": "#ff4b4b",
            "sliderHandleInnerFill": "#d5dae5",
            "sliderTrackFillHover": "#a3a8b8",
            "sliderTrackFillActive": "rgba(250, 250, 250, 0.4)",
            "sliderTrackFillDisabled": "#262730",
            "sliderHandleInnerFillDisabled": "#d5dae5",
            "sliderHandleInnerFillSelectedHover": "#FFFFFF",
            "sliderHandleInnerFillSelectedActive": "#ff4b4b",
            "inputBorder": "#262730",
            "inputFill": "#262730",
            "inputFillError": "#FFEFED",
            "inputFillDisabled": "#262730",
            "inputFillActive": "#262730",
            "inputFillPositive": "#E6F2ED",
            "inputTextDisabled": "rgba(250, 250, 250, 0.4)",
            "inputBorderError": "#F1998E",
            "inputBorderPositive": "#66D19E",
            "inputEnhancerFill": "#e6eaf1",
            "inputEnhancerFillDisabled": "#262730",
            "inputEnhancerTextDisabled": "rgba(250, 250, 250, 0.4)",
            "inputPlaceholder": "rgba(250, 250, 250, 0.6)",
            "inputPlaceholderDisabled": "rgba(250, 250, 250, 0.4)",
            "menuFill": "#0e1117",
            "menuFillHover": "#262730",
            "menuFontDefault": "#fafafa",
            "menuFontDisabled": "#a3a8b8",
            "menuFontHighlighted": "#fafafa",
            "menuFontSelected": "#fafafa",
            "modalCloseColor": "#fafafa",
            "modalCloseColorHover": "#fafafa",
            "modalCloseColorFocus": "#fafafa",
            "tabBarFill": "#262730",
            "tabColor": "#fafafa",
            "notificationInfoBackground": "rgba(61, 157, 243, 0.2)",
            "notificationInfoText": "#c7ebff",
            "notificationPositiveBackground": "rgba(61, 213, 109, 0.2)",
            "notificationPositiveText": "#dffde9",
            "notificationWarningBackground": "rgba(255, 227, 18, 0.2)",
            "notificationWarningText": "#ffffc2",
            "notificationNegativeBackground": "rgba(255, 108, 108, 0.2)",
            "notificationNegativeText": "#ffdede",
            "tagFontDisabledRampUnit": "100",
            "tagSolidFontRampUnit": "0",
            "tagSolidRampUnit": "400",
            "tagOutlinedFontRampUnit": "400",
            "tagOutlinedRampUnit": "200",
            "tagSolidHoverRampUnit": "50",
            "tagSolidActiveRampUnit": "100",
            "tagSolidDisabledRampUnit": "50",
            "tagSolidFontHoverRampUnit": "500",
            "tagLightRampUnit": "50",
            "tagLightHoverRampUnit": "100",
            "tagLightActiveRampUnit": "100",
            "tagLightFontRampUnit": "500",
            "tagLightFontHoverRampUnit": "500",
            "tagOutlinedHoverRampUnit": "50",
            "tagOutlinedActiveRampUnit": "0",
            "tagOutlinedFontHoverRampUnit": "400",
            "tagNeutralFontDisabled": "rgba(250, 250, 250, 0.4)",
            "tagNeutralOutlinedDisabled": "#e6eaf1",
            "tagNeutralSolidFont": "#FFFFFF",
            "tagNeutralSolidBackground": "#000000",
            "tagNeutralOutlinedBackground": "rgba(250, 250, 250, 0.4)",
            "tagNeutralOutlinedFont": "#000000",
            "tagNeutralSolidHover": "#e6eaf1",
            "tagNeutralSolidActive": "#e6eaf1",
            "tagNeutralSolidDisabled": "#262730",
            "tagNeutralSolidFontHover": "#fafafa",
            "tagNeutralLightBackground": "#e6eaf1",
            "tagNeutralLightHover": "#e6eaf1",
            "tagNeutralLightActive": "#e6eaf1",
            "tagNeutralLightDisabled": "#262730",
            "tagNeutralLightFont": "#fafafa",
            "tagNeutralLightFontHover": "#fafafa",
            "tagNeutralOutlinedActive": "#fafafa",
            "tagNeutralOutlinedFontHover": "#fafafa",
            "tagNeutralOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPrimaryFontDisabled": "rgba(250, 250, 250, 0.4)",
            "tagPrimaryOutlinedDisabled": "transparent",
            "tagPrimarySolidFont": "#FFFFFF",
            "tagPrimarySolidBackground": "#ff4b4b",
            "tagPrimaryOutlinedFontHover": "#FFFFFF",
            "tagPrimaryOutlinedFont": "#FFFFFF",
            "tagPrimarySolidHover": "#ff4b4b",
            "tagPrimarySolidActive": "#ff4b4b",
            "tagPrimarySolidDisabled": "#F6F6F6",
            "tagPrimarySolidFontHover": "#ff4b4b",
            "tagPrimaryLightBackground": "#F6F6F6",
            "tagPrimaryLightHover": "#ff4b4b",
            "tagPrimaryLightActive": "#ff4b4b",
            "tagPrimaryLightDisabled": "#F6F6F6",
            "tagPrimaryLightFont": "#ff4b4b",
            "tagPrimaryLightFontHover": "#ff4b4b",
            "tagPrimaryOutlinedActive": "#ff4b4b",
            "tagPrimaryOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPrimaryOutlinedBackground": "#ff4b4b",
            "tagAccentFontDisabled": "#A0BFF8",
            "tagAccentOutlinedDisabled": "#A0BFF8",
            "tagAccentSolidFont": "#FFFFFF",
            "tagAccentSolidBackground": "#276EF1",
            "tagAccentOutlinedBackground": "#A0BFF8",
            "tagAccentOutlinedFont": "#276EF1",
            "tagAccentSolidHover": "#EFF3FE",
            "tagAccentSolidActive": "#D4E2FC",
            "tagAccentSolidDisabled": "#EFF3FE",
            "tagAccentSolidFontHover": "#1E54B7",
            "tagAccentLightBackground": "#EFF3FE",
            "tagAccentLightHover": "#D4E2FC",
            "tagAccentLightActive": "#D4E2FC",
            "tagAccentLightDisabled": "#EFF3FE",
            "tagAccentLightFont": "#1E54B7",
            "tagAccentLightFontHover": "#1E54B7",
            "tagAccentOutlinedActive": "#174291",
            "tagAccentOutlinedFontHover": "#276EF1",
            "tagAccentOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPositiveFontDisabled": "#66D19E",
            "tagPositiveOutlinedDisabled": "#66D19E",
            "tagPositiveSolidFont": "#FFFFFF",
            "tagPositiveSolidBackground": "#048848",
            "tagPositiveOutlinedBackground": "#66D19E",
            "tagPositiveOutlinedFont": "#048848",
            "tagPositiveSolidHover": "#E6F2ED",
            "tagPositiveSolidActive": "#ADDEC9",
            "tagPositiveSolidDisabled": "#E6F2ED",
            "tagPositiveSolidFontHover": "#03703C",
            "tagPositiveLightBackground": "#E6F2ED",
            "tagPositiveLightHover": "#ADDEC9",
            "tagPositiveLightActive": "#ADDEC9",
            "tagPositiveLightDisabled": "#E6F2ED",
            "tagPositiveLightFont": "#03703C",
            "tagPositiveLightFontHover": "#03703C",
            "tagPositiveOutlinedActive": "#03582F",
            "tagPositiveOutlinedFontHover": "#048848",
            "tagPositiveOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagWarningFontDisabled": "#FFCF70",
            "tagWarningOutlinedDisabled": "#FFCF70",
            "tagWarningSolidFont": "#674D1B",
            "tagWarningSolidBackground": "#FFC043",
            "tagWarningOutlinedBackground": "#FFCF70",
            "tagWarningOutlinedFont": "#996F00",
            "tagWarningSolidHover": "#FFFAF0",
            "tagWarningSolidActive": "#FFF2D9",
            "tagWarningSolidDisabled": "#FFFAF0",
            "tagWarningSolidFontHover": "#BC8B2C",
            "tagWarningLightBackground": "#FFFAF0",
            "tagWarningLightHover": "#FFF2D9",
            "tagWarningLightActive": "#FFF2D9",
            "tagWarningLightDisabled": "#FFFAF0",
            "tagWarningLightFont": "#BC8B2C",
            "tagWarningLightFontHover": "#BC8B2C",
            "tagWarningOutlinedActive": "#996F00",
            "tagWarningOutlinedFontHover": "#996F00",
            "tagWarningOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagNegativeFontDisabled": "#F1998E",
            "tagNegativeOutlinedDisabled": "#F1998E",
            "tagNegativeSolidFont": "#FFFFFF",
            "tagNegativeSolidBackground": "#E11900",
            "tagNegativeOutlinedBackground": "#F1998E",
            "tagNegativeOutlinedFont": "#E11900",
            "tagNegativeSolidHover": "#FFEFED",
            "tagNegativeSolidActive": "#FED7D2",
            "tagNegativeSolidDisabled": "#FFEFED",
            "tagNegativeSolidFontHover": "#AB1300",
            "tagNegativeLightBackground": "#FFEFED",
            "tagNegativeLightHover": "#FED7D2",
            "tagNegativeLightActive": "#FED7D2",
            "tagNegativeLightDisabled": "#FFEFED",
            "tagNegativeLightFont": "#AB1300",
            "tagNegativeLightFontHover": "#AB1300",
            "tagNegativeOutlinedActive": "#870F00",
            "tagNegativeOutlinedFontHover": "#E11900",
            "tagNegativeOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tableHeadBackgroundColor": "#0e1117",
            "tableBackground": "#0e1117",
            "tableStripedBackground": "#262730",
            "tableFilter": "rgba(250, 250, 250, 0.4)",
            "tableFilterHeading": "#a3a8b8",
            "tableFilterBackground": "#0e1117",
            "tableFilterFooterBackground": "#262730",
            "toastText": "#FFFFFF",
            "toastPrimaryText": "#FFFFFF",
            "toastInfoBackground": "#276EF1",
            "toastInfoText": "#FFFFFF",
            "toastPositiveBackground": "#048848",
            "toastPositiveText": "#FFFFFF",
            "toastWarningBackground": "#FFC043",
            "toastWarningText": "#000000",
            "toastNegativeBackground": "#E11900",
            "toastNegativeText": "#FFFFFF",
            "spinnerTrackFill": "#fafafa",
            "progressbarTrackFill": "#262730",
            "tooltipBackground": "#fafafa",
            "tooltipText": "#0e1117",
            "backgroundPrimary": "#0e1117",
            "backgroundSecondary": "#262730",
            "backgroundTertiary": "#0e1117",
            "backgroundInversePrimary": "#E2E2E2",
            "backgroundInverseSecondary": "#1F1F1F",
            "contentPrimary": "#fafafa",
            "contentSecondary": "#545454",
            "contentTertiary": "#6B6B6B",
            "contentInversePrimary": "#141414",
            "contentInverseSecondary": "#CBCBCB",
            "contentInverseTertiary": "#AFAFAF",
            "borderOpaque": "rgba(172, 177, 195, 0.25)",
            "borderTransparent": "rgba(226, 226, 226, 0.08)",
            "borderSelected": "#ff4b4b",
            "borderInverseOpaque": "#333333",
            "borderInverseTransparent": "rgba(20, 20, 20, 0.2)",
            "borderInverseSelected": "#141414",
            "backgroundStateDisabled": "#F6F6F6",
            "backgroundOverlayDark": "rgba(0, 0, 0, 0.3)",
            "backgroundOverlayLight": "rgba(0, 0, 0, 0.08)",
            "backgroundOverlayArt": "rgba(0, 0, 0, 0.00)",
            "backgroundAccent": "#276EF1",
            "backgroundNegative": "#AB1300",
            "backgroundWarning": "#BC8B2C",
            "backgroundPositive": "#048848",
            "backgroundLightAccent": "#EFF3FE",
            "backgroundLightNegative": "#FFEFED",
            "backgroundLightWarning": "#FFFAF0",
            "backgroundLightPositive": "#E6F2ED",
            "backgroundAlwaysDark": "#000000",
            "backgroundAlwaysLight": "#FFFFFF",
            "contentStateDisabled": "#AFAFAF",
            "contentAccent": "#276EF1",
            "contentOnColor": "#FFFFFF",
            "contentOnColorInverse": "#000000",
            "contentNegative": "#AB1300",
            "contentWarning": "#996F00",
            "contentPositive": "#048848",
            "borderStateDisabled": "#F6F6F6",
            "borderAccent": "#276EF1",
            "borderAccentLight": "#A0BFF8",
            "borderNegative": "#F1998E",
            "borderWarning": "#FFE3AC",
            "borderPositive": "#66D19E",
            "safety": "#276EF1",
            "eatsGreen400": "#048848",
            "freightBlue400": "#0E1FC1",
            "jumpRed400": "#E11900",
            "rewardsTier1": "#276EF1",
            "rewardsTier2": "#FFC043",
            "rewardsTier3": "#8EA3AD",
            "rewardsTier4": "#000000",
            "membership": "#996F00",
            "datepickerBackground": "#0e1117",
            "inputEnhanceFill": "#262730"
        },
        "direction": "auto",
        "grid": {
            "columns": [
                4,
                8,
                12
            ],
            "gutters": [
                16,
                36,
                36
            ],
            "margins": [
                16,
                36,
                64
            ],
            "gaps": 0,
            "unit": "px",
            "maxWidth": 1280
        },
        "lighting": {
            "shadow400": "0 1px 4px hsla(0, 0%, 0%, 0.16)",
            "shadow500": "0 2px 8px hsla(0, 0%, 0%, 0.16)",
            "shadow600": "0 4px 16px hsla(0, 0%, 0%, 0.16)",
            "shadow700": "0 8px 24px hsla(0, 0%, 0%, 0.16)",
            "overlay0": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0)",
            "overlay100": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.04)",
            "overlay200": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.08)",
            "overlay300": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.12)",
            "overlay400": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.16)",
            "overlay500": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.2)",
            "overlay600": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.24)",
            "shallowAbove": "0px -4px 16px rgba(0, 0, 0, 0.12)",
            "shallowBelow": "0px 4px 16px rgba(0, 0, 0, 0.12)",
            "deepAbove": "0px -16px 48px rgba(0, 0, 0, 0.22)",
            "deepBelow": "0px 16px 48px rgba(0, 0, 0, 0.22)"
        },
        "mediaQuery": {
            "small": "@media screen and (min-width: 320px)",
            "medium": "@media screen and (min-width: 600px)",
            "large": "@media screen and (min-width: 1136px)"
        },
        "sizing": {
            "scale0": "2px",
            "scale100": "4px",
            "scale200": "6px",
            "scale300": "8px",
            "scale400": "10px",
            "scale500": "12px",
            "scale550": "14px",
            "scale600": "16px",
            "scale650": "18px",
            "scale700": "20px",
            "scale750": "22px",
            "scale800": "24px",
            "scale850": "28px",
            "scale900": "32px",
            "scale950": "36px",
            "scale1000": "40px",
            "scale1200": "48px",
            "scale1400": "56px",
            "scale1600": "64px",
            "scale2400": "96px",
            "scale3200": "128px",
            "scale4800": "192px"
        },
        "typography": {
            "font100": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "font150": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font200": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font250": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font300": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font350": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font400": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font450": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font550": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "font650": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "font750": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "font850": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "font950": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "font1050": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "font1150": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "font1250": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "font1350": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "font1450": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "ParagraphXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "ParagraphSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "ParagraphMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "ParagraphLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "HeadingXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "HeadingSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "HeadingMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "HeadingLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "HeadingXLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "HeadingXXLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "DisplayXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "DisplaySmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "DisplayMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "DisplayLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "MonoParagraphXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "MonoParagraphSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "14px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "MonoParagraphMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "16px",
                "fontWeight": "normal",
                "lineHeight": "24px"
            },
            "MonoParagraphLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "18px",
                "fontWeight": "normal",
                "lineHeight": "28px"
            },
            "MonoLabelXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "12px",
                "fontWeight": 500,
                "lineHeight": "16px"
            },
            "MonoLabelSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "14px",
                "fontWeight": 500,
                "lineHeight": "16px"
            },
            "MonoLabelMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "16px",
                "fontWeight": 500,
                "lineHeight": "20px"
            },
            "MonoLabelLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "18px",
                "fontWeight": 500,
                "lineHeight": "24px"
            },
            "MonoHeadingXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "MonoHeadingSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "MonoHeadingMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "MonoHeadingLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "MonoHeadingXLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "MonoHeadingXXLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "MonoDisplayXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "MonoDisplaySmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "MonoDisplayMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "MonoDisplayLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "font460": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font470": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font500": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font600": {}
        },
        "zIndex": {
            "modal": 2000
        }
    },
    "primitives": {
        "primaryA": "#E2E2E2",
        "primaryB": "#141414",
        "primary": "#FFFFFF",
        "primary50": "#F6F6F6",
        "primary100": "#EEEEEE",
        "primary200": "#E2E2E2",
        "primary300": "#CBCBCB",
        "primary400": "#AFAFAF",
        "primary500": "#6B6B6B",
        "primary600": "#545454",
        "primary700": "#333333",
        "accent": "#276EF1",
        "accent50": "#EFF3FE",
        "accent100": "#D4E2FC",
        "accent200": "#A0BFF8",
        "accent300": "#5B91F5",
        "accent400": "#276EF1",
        "accent500": "#1E54B7",
        "accent600": "#174291",
        "accent700": "#102C60",
        "negative": "#AB1300",
        "negative50": "#FFEFED",
        "negative100": "#FED7D2",
        "negative200": "#F1998E",
        "negative300": "#E85C4A",
        "negative400": "#E11900",
        "negative500": "#AB1300",
        "negative600": "#870F00",
        "negative700": "#5A0A00",
        "warning": "#BC8B2C",
        "warning50": "#FFFAF0",
        "warning100": "#FFF2D9",
        "warning200": "#FFE3AC",
        "warning300": "#FFCF70",
        "warning400": "#FFC043",
        "warning500": "#BC8B2C",
        "warning600": "#996F00",
        "warning700": "#674D1B",
        "positive": "#048848",
        "positive50": "#E6F2ED",
        "positive100": "#ADDEC9",
        "positive200": "#66D19E",
        "positive300": "#06C167",
        "positive400": "#048848",
        "positive500": "#03703C",
        "positive600": "#03582F",
        "positive700": "#10462D",
        "white": "#FFFFFF",
        "black": "#000000",
        "mono100": "#CBCBCB",
        "mono200": "#AFAFAF",
        "mono300": "#6B6B6B",
        "mono400": "#545454",
        "mono500": "#333333",
        "mono600": "#292929",
        "mono700": "#1F1F1F",
        "mono800": "#141414",
        "mono900": "#111111",
        "mono1000": "#000000",
        "ratingInactiveFill": "#6B6B6B",
        "ratingStroke": "#333333",
        "primaryFontFamily": "system-ui, \"Helvetica Neue\", Helvetica, Arial, sans-serif"
    }
}
```

### JSON Base Configuration for Streamlit Light Theme

```json
{
    "name": "Light",
    "emotion": {
        "inSidebar": false,
        "breakpoints": {
            "hideWidgetDetails": 180,
            "hideNumberInputControls": 120,
            "sm": "576px",
            "columns": "640px",
            "md": "768px"
        },
        "colors": {
            "transparent": "transparent",
            "black": "#000000",
            "white": "#ffffff",
            "gray10": "#fafafa",
            "gray20": "#f0f2f6",
            "gray30": "#e6eaf1",
            "gray40": "#d5dae5",
            "gray50": "#bfc5d3",
            "gray60": "#a3a8b8",
            "gray70": "#808495",
            "gray80": "#555867",
            "gray85": "#31333F",
            "gray90": "#262730",
            "gray100": "#0e1117",
            "red10": "#fff0f0",
            "red20": "#ffdede",
            "red30": "#ffc7c7",
            "red40": "#ffabab",
            "red50": "#ff8c8c",
            "red60": "#ff6c6c",
            "red70": "#ff4b4b",
            "red80": "#ff2b2b",
            "red90": "#bd4043",
            "red100": "#7d353b",
            "orange10": "#fffae8",
            "orange20": "#fff6d0",
            "orange30": "#ffecb0",
            "orange40": "#ffe08e",
            "orange50": "#ffd16a",
            "orange60": "#ffbd45",
            "orange70": "#ffa421",
            "orange80": "#ff8700",
            "orange90": "#ed6f13",
            "orange100": "#d95a00",
            "yellow10": "#ffffe1",
            "yellow20": "#ffffc2",
            "yellow30": "#ffffa0",
            "yellow40": "#ffff7d",
            "yellow50": "#ffff59",
            "yellow60": "#fff835",
            "yellow70": "#ffe312",
            "yellow80": "#faca2b",
            "yellow90": "#edbb16",
            "yellow100": "#dea816",
            "yellow110": "#916e10",
            "green10": "#dffde9",
            "green20": "#c0fcd3",
            "green30": "#9ef6bb",
            "green40": "#7defa1",
            "green50": "#5ce488",
            "green60": "#3dd56d",
            "green70": "#21c354",
            "green80": "#09ab3b",
            "green90": "#158237",
            "green100": "#177233",
            "blueGreen10": "#dcfffb",
            "blueGreen20": "#bafff7",
            "blueGreen30": "#93ffee",
            "blueGreen40": "#6bfde3",
            "blueGreen50": "#45f4d5",
            "blueGreen60": "#20e7c5",
            "blueGreen70": "#00d4b1",
            "blueGreen80": "#29b09d",
            "blueGreen90": "#2c867c",
            "blueGreen100": "#246e69",
            "lightBlue10": "#e0feff",
            "lightBlue20": "#bffdff",
            "lightBlue30": "#9af8ff",
            "lightBlue40": "#73efff",
            "lightBlue50": "#4be4ff",
            "lightBlue60": "#24d4ff",
            "lightBlue70": "#00c0f2",
            "lightBlue80": "#00a4d4",
            "lightBlue90": "#0d8cb5",
            "lightBlue100": "#15799e",
            "blue10": "#e4f5ff",
            "blue20": "#c7ebff",
            "blue30": "#a6dcff",
            "blue40": "#83c9ff",
            "blue50": "#60b4ff",
            "blue60": "#3d9df3",
            "blue70": "#1c83e1",
            "blue80": "#0068c9",
            "blue90": "#0054a3",
            "blue100": "#004280",
            "purple10": "#f5ebff",
            "purple20": "#ebd6ff",
            "purple30": "#dbbbff",
            "purple40": "#c89dff",
            "purple50": "#b27eff",
            "purple60": "#9a5dff",
            "purple70": "#803df5",
            "purple80": "#6d3fc0",
            "purple90": "#583f84",
            "purple100": "#3f3163",
            "bgColor": "#ffffff",
            "secondaryBg": "#f0f2f6",
            "bodyText": "#31333F",
            "warning": "#926C05",
            "warningBg": "rgba(255, 227, 18, 0.1)",
            "success": "#177233",
            "successBg": "rgba(33, 195, 84, 0.1)",
            "infoBg": "rgba(28, 131, 225, 0.1)",
            "info": "#004280",
            "danger": "#7d353b",
            "dangerBg": "rgba(255, 43, 43, 0.09)",
            "primary": "#ff4b4b",
            "disabled": "#d5dae5",
            "lightestGray": "#f0f2f6",
            "lightGray": "#e6eaf1",
            "gray": "#a3a8b8",
            "darkGray": "#808495",
            "red": "#ff2b2b",
            "blue": "#0068c9",
            "green": "#09ab3b",
            "yellow": "#faca2b",
            "linkText": "#0068c9",
            "fadedText05": "rgba(49, 51, 63, 0.1)",
            "fadedText10": "rgba(49, 51, 63, 0.2)",
            "fadedText20": "rgba(49, 51, 63, 0.3)",
            "fadedText40": "rgba(49, 51, 63, 0.4)",
            "fadedText60": "rgba(49, 51, 63, 0.6)",
            "bgMix": "rgba(248, 249, 251, 1)",
            "darkenedBgMix100": "hsla(220, 27%, 68%, 1)",
            "darkenedBgMix25": "rgba(151, 166, 195, 0.25)",
            "darkenedBgMix15": "rgba(151, 166, 195, 0.15)",
            "lightenedBg05": "hsla(0, 0%, 100%, 1)",
            "borderColor": "rgba(49, 51, 63, 0.2)",
            "borderColorLight": "rgba(49, 51, 63, 0.1)",
            "codeTextColor": "#09ab3b",
            "codeHighlightColor": "rgba(248, 249, 251, 1)",
            "metricPositiveDeltaColor": "#09ab3b",
            "metricNegativeDeltaColor": "#ff2b2b",
            "metricNeutralDeltaColor": "rgba(49, 51, 63, 0.6)",
            "docStringModuleText": "#31333F",
            "docStringTypeText": "#21c354",
            "docStringContainerBackground": "rgba(240, 242, 246, 0.4)",
            "headingColor": "#31333F",
            "navTextColor": "#555867",
            "navActiveTextColor": "#262730",
            "navIconColor": "#a3a8b8",
            "sidebarControlColor": "#808495"
        },
        "fonts": {
            "sansSerif": "\"Source Sans Pro\", sans-serif",
            "monospace": "\"Source Code Pro\", monospace",
            "serif": "\"Source Serif Pro\", serif",
            "materialIcons": "Material Symbols Rounded"
        },
        "fontSizes": {
            "twoSm": "12px",
            "sm": "14px",
            "md": "1rem",
            "mdLg": "1.125rem",
            "lg": "1.25rem",
            "xl": "1.5rem",
            "twoXL": "1.75rem",
            "threeXL": "2.25rem",
            "fourXL": "2.75rem",
            "twoSmPx": 12,
            "smPx": 14,
            "mdPx": 16
        },
        "fontWeights": {
            "normal": 400,
            "bold": 600,
            "extrabold": 700
        },
        "genericFonts": {
            "bodyFont": "\"Source Sans Pro\", sans-serif",
            "codeFont": "\"Source Code Pro\", monospace",
            "headingFont": "\"Source Sans Pro\", sans-serif",
            "iconFont": "Material Symbols Rounded"
        },
        "iconSizes": {
            "xs": "0.5rem",
            "sm": "0.75rem",
            "md": "0.9rem",
            "base": "1rem",
            "lg": "1.25rem",
            "xl": "1.5rem",
            "twoXL": "1.8rem",
            "threeXL": "2.3rem"
        },
        "lineHeights": {
            "none": 1,
            "headings": 1.2,
            "tight": 1.25,
            "inputWidget": 1.4,
            "small": 1.5,
            "base": 1.6,
            "menuItem": 2
        },
        "radii": {
            "md": "0.25rem",
            "default": "0.5rem",
            "xl": "0.75rem",
            "xxl": "1rem",
            "full": "9999px"
        },
        "sizes": {
            "full": "100%",
            "headerHeight": "3.75rem",
            "fullScreenHeaderHeight": "2.875rem",
            "sidebarTopSpace": "6rem",
            "toastWidth": "21rem",
            "contentMaxWidth": "46rem",
            "maxChartTooltipWidth": "30rem",
            "checkbox": "1rem",
            "borderWidth": "1px",
            "smallElementHeight": "1.5rem",
            "minElementHeight": "2.5rem",
            "largestElementHeight": "4.25rem",
            "smallLogoHeight": "1.25rem",
            "defaultLogoHeight": "1.5rem",
            "largeLogoHeight": "2rem",
            "sliderThumb": "0.75rem",
            "wideSidePadding": "5rem",
            "headerDecorationHeight": "0.125rem",
            "appRunningMen": "1.6rem",
            "appStatusMaxWidth": "20rem",
            "spinnerSize": "1.375rem",
            "spinnerThickness": "0.2rem",
            "tabHeight": "2.5rem",
            "minPopupWidth": "20rem",
            "maxTooltipHeight": "18.75rem",
            "chatAvatarSize": "2rem",
            "clearIconSize": "1.5em",
            "numberInputControlsWidth": "2rem",
            "emptyDropdownHeight": "5.625rem",
            "dropdownItemHeight": "2.5rem",
            "maxDropdownHeight": "18.75rem",
            "appDefaultBottomPadding": "3.5rem"
        },
        "spacing": {
            "px": "1px",
            "none": "0",
            "threeXS": "0.125rem",
            "twoXS": "0.25rem",
            "xs": "0.375rem",
            "sm": "0.5rem",
            "md": "0.75rem",
            "lg": "1rem",
            "xl": "1.25rem",
            "twoXL": "1.5rem",
            "threeXL": "2rem",
            "fourXL": "4rem"
        },
        "zIndices": {
            "hide": -1,
            "auto": "auto",
            "base": 0,
            "priority": 1,
            "sidebar": 100,
            "menuButton": 110,
            "balloons": 1000000,
            "header": 999990,
            "sidebarMobile": 999995,
            "popupMenu": 1000040,
            "fullscreenWrapper": 1000050,
            "tablePortal": 1000110,
            "bottom": 99,
            "cacheSpinner": 101,
            "toast": 100,
            "vegaTooltips": 1000060
        }
    },
    "basewebTheme": {
        "animation": {
            "timing100": "100ms",
            "timing200": "200ms",
            "timing300": "300ms",
            "timing400": "400ms",
            "timing500": "500ms",
            "timing600": "600ms",
            "timing700": "700ms",
            "timing800": "800ms",
            "timing900": "900ms",
            "timing1000": "1000ms",
            "easeInCurve": "cubic-bezier(.8, .2, .6, 1)",
            "easeOutCurve": "cubic-bezier(.2, .8, .4, 1)",
            "easeInOutCurve": "cubic-bezier(0.4, 0, 0.2, 1)",
            "easeInQuinticCurve": "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
            "easeOutQuinticCurve": "cubic-bezier(0.23, 1, 0.32, 1)",
            "easeInOutQuinticCurve": "cubic-bezier(0.86, 0, 0.07, 1)",
            "linearCurve": "cubic-bezier(0, 0, 1, 1)"
        },
        "borders": {
            "border100": {
                "borderColor": "hsla(0, 0%, 0%, 0.04)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border200": {
                "borderColor": "hsla(0, 0%, 0%, 0.08)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border300": {
                "borderColor": "hsla(0, 0%, 0%, 0.12)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border400": {
                "borderColor": "hsla(0, 0%, 0%, 0.16)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border500": {
                "borderColor": "hsla(0, 0%, 0%, 0.2)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "border600": {
                "borderColor": "hsla(0, 0%, 0%, 0.24)",
                "borderStyle": "solid",
                "borderWidth": "1px"
            },
            "radius100": "0.5rem",
            "radius200": "0.5rem",
            "radius300": "0.5rem",
            "radius400": "0.5rem",
            "radius500": "0.5rem",
            "useRoundedCorners": true,
            "buttonBorderRadiusMini": "0.25rem",
            "buttonBorderRadius": "0.5rem",
            "checkboxBorderRadius": "0.25rem",
            "inputBorderRadiusMini": "0.25rem",
            "inputBorderRadius": "0.5rem",
            "popoverBorderRadius": "0.5rem",
            "surfaceBorderRadius": "0.5rem",
            "tagBorderRadius": "0.25rem"
        },
        "breakpoints": {
            "small": 320,
            "medium": 600,
            "large": 1136
        },
        "colors": {
            "primaryA": "#ff4b4b",
            "primaryB": "#FFFFFF",
            "primary": "#ff4b4b",
            "primary50": "#F6F6F6",
            "primary100": "#ff4b4b",
            "primary200": "#ff4b4b",
            "primary300": "#ff4b4b",
            "primary400": "#ff4b4b",
            "primary500": "#ff4b4b",
            "primary600": "#ff4b4b",
            "primary700": "#ff4b4b",
            "accent": "rgba(255, 75, 75, 0.5)",
            "accent50": "#EFF3FE",
            "accent100": "#D4E2FC",
            "accent200": "#A0BFF8",
            "accent300": "#5B91F5",
            "accent400": "#276EF1",
            "accent500": "#1E54B7",
            "accent600": "#174291",
            "accent700": "#102C60",
            "negative": "#E11900",
            "negative50": "#FFEFED",
            "negative100": "#FED7D2",
            "negative200": "#F1998E",
            "negative300": "#E85C4A",
            "negative400": "#E11900",
            "negative500": "#AB1300",
            "negative600": "#870F00",
            "negative700": "#5A0A00",
            "warning": "#FFC043",
            "warning50": "#FFFAF0",
            "warning100": "#FFF2D9",
            "warning200": "#FFE3AC",
            "warning300": "#FFCF70",
            "warning400": "#FFC043",
            "warning500": "#BC8B2C",
            "warning600": "#996F00",
            "warning700": "#674D1B",
            "positive": "#03703C",
            "positive50": "#E6F2ED",
            "positive100": "#ADDEC9",
            "positive200": "#66D19E",
            "positive300": "#06C167",
            "positive400": "#048848",
            "positive500": "#03703C",
            "positive600": "#03582F",
            "positive700": "#10462D",
            "white": "#ffffff",
            "black": "#000000",
            "mono100": "#ffffff",
            "mono200": "#f0f2f6",
            "mono300": "#e6eaf1",
            "mono400": "#e6eaf1",
            "mono500": "#a3a8b8",
            "mono600": "rgba(49, 51, 63, 0.4)",
            "mono700": "#a3a8b8",
            "mono800": "#31333F",
            "mono900": "#31333F",
            "mono1000": "#000000",
            "ratingInactiveFill": "#EEEEEE",
            "ratingStroke": "#CBCBCB",
            "bannerActionLowInfo": "#D4E2FC",
            "bannerActionLowNegative": "#FED7D2",
            "bannerActionLowPositive": "#ADDEC9",
            "bannerActionLowWarning": "#FFE3AC",
            "bannerActionHighInfo": "#1E54B7",
            "bannerActionHighNegative": "#AB1300",
            "bannerActionHighPositive": "#03703C",
            "bannerActionHighWarning": "#FFE3AC",
            "buttonPrimaryFill": "#000000",
            "buttonPrimaryText": "#FFFFFF",
            "buttonPrimaryHover": "#ff4b4b",
            "buttonPrimaryActive": "#ff4b4b",
            "buttonPrimarySelectedFill": "#ff4b4b",
            "buttonPrimarySelectedText": "#FFFFFF",
            "buttonPrimarySpinnerForeground": "#276EF1",
            "buttonPrimarySpinnerBackground": "#FFFFFF",
            "buttonSecondaryFill": "#ff4b4b",
            "buttonSecondaryText": "#000000",
            "buttonSecondaryHover": "#ff4b4b",
            "buttonSecondaryActive": "#ff4b4b",
            "buttonSecondarySelectedFill": "#ff4b4b",
            "buttonSecondarySelectedText": "#000000",
            "buttonSecondarySpinnerForeground": "#276EF1",
            "buttonSecondarySpinnerBackground": "#FFFFFF",
            "buttonTertiaryFill": "transparent",
            "buttonTertiaryText": "#000000",
            "buttonTertiaryHover": "#F6F6F6",
            "buttonTertiaryActive": "#ff4b4b",
            "buttonTertiarySelectedFill": "#ff4b4b",
            "buttonTertiarySelectedText": "#000000",
            "buttonTertiaryDisabledActiveFill": "#F6F6F6",
            "buttonTertiaryDisabledActiveText": "rgba(49, 51, 63, 0.4)",
            "buttonTertiarySpinnerForeground": "#276EF1",
            "buttonTertiarySpinnerBackground": "#ff4b4b",
            "buttonDisabledFill": "hsla(0, 0%, 100%, 1)",
            "buttonDisabledText": "rgba(49, 51, 63, 0.4)",
            "buttonDisabledActiveFill": "#a3a8b8",
            "buttonDisabledActiveText": "#ffffff",
            "buttonDisabledSpinnerForeground": "rgba(49, 51, 63, 0.4)",
            "buttonDisabledSpinnerBackground": "#d5dae5",
            "breadcrumbsText": "#000000",
            "breadcrumbsSeparatorFill": "#a3a8b8",
            "calendarBackground": "#ffffff",
            "calendarForeground": "#31333F",
            "calendarForegroundDisabled": "#a3a8b8",
            "calendarHeaderBackground": "#f0f2f6",
            "calendarHeaderForeground": "#31333F",
            "calendarHeaderBackgroundActive": "#f0f2f6",
            "calendarHeaderForegroundDisabled": "#d5dae5",
            "calendarDayForegroundPseudoSelected": "#31333F",
            "calendarDayBackgroundPseudoSelectedHighlighted": "#ff4b4b",
            "calendarDayForegroundPseudoSelectedHighlighted": "#31333F",
            "calendarDayBackgroundSelected": "#ff4b4b",
            "calendarDayForegroundSelected": "#ffffff",
            "calendarDayBackgroundSelectedHighlighted": "#ff4b4b",
            "calendarDayForegroundSelectedHighlighted": "#ffffff",
            "comboboxListItemFocus": "#f0f2f6",
            "comboboxListItemHover": "#e6eaf1",
            "fileUploaderBackgroundColor": "#f0f2f6",
            "fileUploaderBackgroundColorActive": "#F6F6F6",
            "fileUploaderBorderColorActive": "#000000",
            "fileUploaderBorderColorDefault": "#a3a8b8",
            "fileUploaderMessageColor": "#31333F",
            "linkText": "#000000",
            "linkVisited": "#ff4b4b",
            "linkHover": "#ff4b4b",
            "linkActive": "#ff4b4b",
            "listHeaderFill": "#FFFFFF",
            "listBodyFill": "#FFFFFF",
            "progressStepsCompletedText": "#FFFFFF",
            "progressStepsCompletedFill": "#000000",
            "progressStepsActiveText": "#FFFFFF",
            "progressStepsActiveFill": "#000000",
            "toggleFill": "#FFFFFF",
            "toggleFillChecked": "#000000",
            "toggleFillDisabled": "rgba(49, 51, 63, 0.4)",
            "toggleTrackFill": "#d5dae5",
            "toggleTrackFillDisabled": "#f0f2f6",
            "tickFill": "hsla(0, 0%, 100%, 1)",
            "tickFillHover": "#f0f2f6",
            "tickFillActive": "#f0f2f6",
            "tickFillSelected": "#ff4b4b",
            "tickFillSelectedHover": "#ff4b4b",
            "tickFillSelectedHoverActive": "#ff4b4b",
            "tickFillError": "#FFEFED",
            "tickFillErrorHover": "#FED7D2",
            "tickFillErrorHoverActive": "#F1998E",
            "tickFillErrorSelected": "#E11900",
            "tickFillErrorSelectedHover": "#AB1300",
            "tickFillErrorSelectedHoverActive": "#870F00",
            "tickFillDisabled": "rgba(49, 51, 63, 0.4)",
            "tickBorder": "#a3a8b8",
            "tickBorderError": "#E11900",
            "tickMarkFill": "#f0f2f6",
            "tickMarkFillError": "#FFFFFF",
            "tickMarkFillDisabled": "hsla(0, 0%, 100%, 1)",
            "sliderTrackFill": "#d5dae5",
            "sliderHandleFill": "#000000",
            "sliderHandleFillDisabled": "#ff4b4b",
            "sliderHandleInnerFill": "#d5dae5",
            "sliderTrackFillHover": "#a3a8b8",
            "sliderTrackFillActive": "rgba(49, 51, 63, 0.4)",
            "sliderTrackFillDisabled": "#f0f2f6",
            "sliderHandleInnerFillDisabled": "#d5dae5",
            "sliderHandleInnerFillSelectedHover": "#000000",
            "sliderHandleInnerFillSelectedActive": "#ff4b4b",
            "inputBorder": "#f0f2f6",
            "inputFill": "#f0f2f6",
            "inputFillError": "#FFEFED",
            "inputFillDisabled": "#f0f2f6",
            "inputFillActive": "#f0f2f6",
            "inputFillPositive": "#E6F2ED",
            "inputTextDisabled": "rgba(49, 51, 63, 0.4)",
            "inputBorderError": "#F1998E",
            "inputBorderPositive": "#66D19E",
            "inputEnhancerFill": "#e6eaf1",
            "inputEnhancerFillDisabled": "#f0f2f6",
            "inputEnhancerTextDisabled": "rgba(49, 51, 63, 0.4)",
            "inputPlaceholder": "rgba(49, 51, 63, 0.6)",
            "inputPlaceholderDisabled": "rgba(49, 51, 63, 0.4)",
            "menuFill": "#ffffff",
            "menuFillHover": "#f0f2f6",
            "menuFontDefault": "#31333F",
            "menuFontDisabled": "#a3a8b8",
            "menuFontHighlighted": "#31333F",
            "menuFontSelected": "#31333F",
            "modalCloseColor": "#31333F",
            "modalCloseColorHover": "#31333F",
            "modalCloseColorFocus": "#31333F",
            "tabBarFill": "#f0f2f6",
            "tabColor": "#31333F",
            "notificationInfoBackground": "rgba(28, 131, 225, 0.1)",
            "notificationInfoText": "#004280",
            "notificationPositiveBackground": "rgba(33, 195, 84, 0.1)",
            "notificationPositiveText": "#177233",
            "notificationWarningBackground": "rgba(255, 227, 18, 0.1)",
            "notificationWarningText": "#926C05",
            "notificationNegativeBackground": "rgba(255, 43, 43, 0.09)",
            "notificationNegativeText": "#7d353b",
            "tagFontDisabledRampUnit": "100",
            "tagSolidFontRampUnit": "0",
            "tagSolidRampUnit": "400",
            "tagOutlinedFontRampUnit": "400",
            "tagOutlinedRampUnit": "200",
            "tagSolidHoverRampUnit": "50",
            "tagSolidActiveRampUnit": "100",
            "tagSolidDisabledRampUnit": "50",
            "tagSolidFontHoverRampUnit": "500",
            "tagLightRampUnit": "50",
            "tagLightHoverRampUnit": "100",
            "tagLightActiveRampUnit": "100",
            "tagLightFontRampUnit": "500",
            "tagLightFontHoverRampUnit": "500",
            "tagOutlinedHoverRampUnit": "50",
            "tagOutlinedActiveRampUnit": "0",
            "tagOutlinedFontHoverRampUnit": "400",
            "tagNeutralFontDisabled": "rgba(49, 51, 63, 0.4)",
            "tagNeutralOutlinedDisabled": "#e6eaf1",
            "tagNeutralSolidFont": "#FFFFFF",
            "tagNeutralSolidBackground": "#000000",
            "tagNeutralOutlinedBackground": "rgba(49, 51, 63, 0.4)",
            "tagNeutralOutlinedFont": "#000000",
            "tagNeutralSolidHover": "#e6eaf1",
            "tagNeutralSolidActive": "#e6eaf1",
            "tagNeutralSolidDisabled": "#f0f2f6",
            "tagNeutralSolidFontHover": "#31333F",
            "tagNeutralLightBackground": "#e6eaf1",
            "tagNeutralLightHover": "#e6eaf1",
            "tagNeutralLightActive": "#e6eaf1",
            "tagNeutralLightDisabled": "#f0f2f6",
            "tagNeutralLightFont": "#31333F",
            "tagNeutralLightFontHover": "#31333F",
            "tagNeutralOutlinedActive": "#31333F",
            "tagNeutralOutlinedFontHover": "#31333F",
            "tagNeutralOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPrimaryFontDisabled": "rgba(49, 51, 63, 0.4)",
            "tagPrimaryOutlinedDisabled": "transparent",
            "tagPrimarySolidFont": "#FFFFFF",
            "tagPrimarySolidBackground": "#ff4b4b",
            "tagPrimaryOutlinedFontHover": "#000000",
            "tagPrimaryOutlinedFont": "#000000",
            "tagPrimarySolidHover": "#ff4b4b",
            "tagPrimarySolidActive": "#ff4b4b",
            "tagPrimarySolidDisabled": "#F6F6F6",
            "tagPrimarySolidFontHover": "#ff4b4b",
            "tagPrimaryLightBackground": "#F6F6F6",
            "tagPrimaryLightHover": "#ff4b4b",
            "tagPrimaryLightActive": "#ff4b4b",
            "tagPrimaryLightDisabled": "#F6F6F6",
            "tagPrimaryLightFont": "#ff4b4b",
            "tagPrimaryLightFontHover": "#ff4b4b",
            "tagPrimaryOutlinedActive": "#ff4b4b",
            "tagPrimaryOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPrimaryOutlinedBackground": "#ff4b4b",
            "tagAccentFontDisabled": "#A0BFF8",
            "tagAccentOutlinedDisabled": "#A0BFF8",
            "tagAccentSolidFont": "#FFFFFF",
            "tagAccentSolidBackground": "#276EF1",
            "tagAccentOutlinedBackground": "#A0BFF8",
            "tagAccentOutlinedFont": "#276EF1",
            "tagAccentSolidHover": "#EFF3FE",
            "tagAccentSolidActive": "#D4E2FC",
            "tagAccentSolidDisabled": "#EFF3FE",
            "tagAccentSolidFontHover": "#1E54B7",
            "tagAccentLightBackground": "#EFF3FE",
            "tagAccentLightHover": "#D4E2FC",
            "tagAccentLightActive": "#D4E2FC",
            "tagAccentLightDisabled": "#EFF3FE",
            "tagAccentLightFont": "#1E54B7",
            "tagAccentLightFontHover": "#1E54B7",
            "tagAccentOutlinedActive": "#174291",
            "tagAccentOutlinedFontHover": "#276EF1",
            "tagAccentOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagPositiveFontDisabled": "#66D19E",
            "tagPositiveOutlinedDisabled": "#66D19E",
            "tagPositiveSolidFont": "#FFFFFF",
            "tagPositiveSolidBackground": "#048848",
            "tagPositiveOutlinedBackground": "#66D19E",
            "tagPositiveOutlinedFont": "#048848",
            "tagPositiveSolidHover": "#E6F2ED",
            "tagPositiveSolidActive": "#ADDEC9",
            "tagPositiveSolidDisabled": "#E6F2ED",
            "tagPositiveSolidFontHover": "#03703C",
            "tagPositiveLightBackground": "#E6F2ED",
            "tagPositiveLightHover": "#ADDEC9",
            "tagPositiveLightActive": "#ADDEC9",
            "tagPositiveLightDisabled": "#E6F2ED",
            "tagPositiveLightFont": "#03703C",
            "tagPositiveLightFontHover": "#03703C",
            "tagPositiveOutlinedActive": "#03582F",
            "tagPositiveOutlinedFontHover": "#048848",
            "tagPositiveOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagWarningFontDisabled": "#FFCF70",
            "tagWarningOutlinedDisabled": "#FFCF70",
            "tagWarningSolidFont": "#674D1B",
            "tagWarningSolidBackground": "#FFC043",
            "tagWarningOutlinedBackground": "#FFCF70",
            "tagWarningOutlinedFont": "#996F00",
            "tagWarningSolidHover": "#FFFAF0",
            "tagWarningSolidActive": "#FFF2D9",
            "tagWarningSolidDisabled": "#FFFAF0",
            "tagWarningSolidFontHover": "#BC8B2C",
            "tagWarningLightBackground": "#FFFAF0",
            "tagWarningLightHover": "#FFF2D9",
            "tagWarningLightActive": "#FFF2D9",
            "tagWarningLightDisabled": "#FFFAF0",
            "tagWarningLightFont": "#BC8B2C",
            "tagWarningLightFontHover": "#BC8B2C",
            "tagWarningOutlinedActive": "#996F00",
            "tagWarningOutlinedFontHover": "#996F00",
            "tagWarningOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tagNegativeFontDisabled": "#F1998E",
            "tagNegativeOutlinedDisabled": "#F1998E",
            "tagNegativeSolidFont": "#FFFFFF",
            "tagNegativeSolidBackground": "#E11900",
            "tagNegativeOutlinedBackground": "#F1998E",
            "tagNegativeOutlinedFont": "#E11900",
            "tagNegativeSolidHover": "#FFEFED",
            "tagNegativeSolidActive": "#FED7D2",
            "tagNegativeSolidDisabled": "#FFEFED",
            "tagNegativeSolidFontHover": "#AB1300",
            "tagNegativeLightBackground": "#FFEFED",
            "tagNegativeLightHover": "#FED7D2",
            "tagNegativeLightActive": "#FED7D2",
            "tagNegativeLightDisabled": "#FFEFED",
            "tagNegativeLightFont": "#AB1300",
            "tagNegativeLightFontHover": "#AB1300",
            "tagNegativeOutlinedActive": "#870F00",
            "tagNegativeOutlinedFontHover": "#E11900",
            "tagNegativeOutlinedHover": "rgba(0, 0, 0, 0.08)",
            "tableHeadBackgroundColor": "#ffffff",
            "tableBackground": "#ffffff",
            "tableStripedBackground": "#f0f2f6",
            "tableFilter": "rgba(49, 51, 63, 0.4)",
            "tableFilterHeading": "#a3a8b8",
            "tableFilterBackground": "#ffffff",
            "tableFilterFooterBackground": "#f0f2f6",
            "toastText": "#FFFFFF",
            "toastPrimaryText": "#FFFFFF",
            "toastInfoBackground": "#276EF1",
            "toastInfoText": "#FFFFFF",
            "toastPositiveBackground": "#048848",
            "toastPositiveText": "#FFFFFF",
            "toastWarningBackground": "#FFC043",
            "toastWarningText": "#000000",
            "toastNegativeBackground": "#E11900",
            "toastNegativeText": "#FFFFFF",
            "spinnerTrackFill": "#31333F",
            "progressbarTrackFill": "#f0f2f6",
            "tooltipBackground": "#31333F",
            "tooltipText": "#ffffff",
            "backgroundPrimary": "#ffffff",
            "backgroundSecondary": "#f0f2f6",
            "backgroundTertiary": "#ffffff",
            "backgroundInversePrimary": "#000000",
            "backgroundInverseSecondary": "#1F1F1F",
            "contentPrimary": "#31333F",
            "contentSecondary": "#545454",
            "contentTertiary": "#6B6B6B",
            "contentInversePrimary": "#FFFFFF",
            "contentInverseSecondary": "#CBCBCB",
            "contentInverseTertiary": "#AFAFAF",
            "borderOpaque": "rgba(151, 166, 195, 0.25)",
            "borderTransparent": "rgba(0, 0, 0, 0.08)",
            "borderSelected": "#ff4b4b",
            "borderInverseOpaque": "#333333",
            "borderInverseTransparent": "rgba(255, 255, 255, 0.2)",
            "borderInverseSelected": "#FFFFFF",
            "backgroundStateDisabled": "#F6F6F6",
            "backgroundOverlayDark": "rgba(0, 0, 0, 0.3)",
            "backgroundOverlayLight": "rgba(0, 0, 0, 0.08)",
            "backgroundOverlayArt": "rgba(0, 0, 0, 0.00)",
            "backgroundAccent": "#276EF1",
            "backgroundNegative": "#E11900",
            "backgroundWarning": "#FFC043",
            "backgroundPositive": "#048848",
            "backgroundLightAccent": "#EFF3FE",
            "backgroundLightNegative": "#FFEFED",
            "backgroundLightWarning": "#FFFAF0",
            "backgroundLightPositive": "#E6F2ED",
            "backgroundAlwaysDark": "#000000",
            "backgroundAlwaysLight": "#FFFFFF",
            "contentStateDisabled": "#AFAFAF",
            "contentAccent": "#276EF1",
            "contentOnColor": "#FFFFFF",
            "contentOnColorInverse": "#000000",
            "contentNegative": "#E11900",
            "contentWarning": "#996F00",
            "contentPositive": "#048848",
            "borderStateDisabled": "#F6F6F6",
            "borderAccent": "#276EF1",
            "borderAccentLight": "#A0BFF8",
            "borderNegative": "#F1998E",
            "borderWarning": "#FFE3AC",
            "borderPositive": "#66D19E",
            "safety": "#276EF1",
            "eatsGreen400": "#048848",
            "freightBlue400": "#0E1FC1",
            "jumpRed400": "#E11900",
            "rewardsTier1": "#276EF1",
            "rewardsTier2": "#FFC043",
            "rewardsTier3": "#8EA3AD",
            "rewardsTier4": "#000000",
            "membership": "#996F00",
            "datepickerBackground": "#ffffff",
            "inputEnhanceFill": "#f0f2f6"
        },
        "direction": "auto",
        "grid": {
            "columns": [
                4,
                8,
                12
            ],
            "gutters": [
                16,
                36,
                36
            ],
            "margins": [
                16,
                36,
                64
            ],
            "gaps": 0,
            "unit": "px",
            "maxWidth": 1280
        },
        "lighting": {
            "shadow400": "0 1px 4px hsla(0, 0%, 0%, 0.16)",
            "shadow500": "0 2px 8px hsla(0, 0%, 0%, 0.16)",
            "shadow600": "0 4px 16px hsla(0, 0%, 0%, 0.16)",
            "shadow700": "0 8px 24px hsla(0, 0%, 0%, 0.16)",
            "overlay0": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0)",
            "overlay100": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.04)",
            "overlay200": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.08)",
            "overlay300": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.12)",
            "overlay400": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.16)",
            "overlay500": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.2)",
            "overlay600": "inset 0 0 0 1000px hsla(0, 0%, 0%, 0.24)",
            "shallowAbove": "0px -4px 16px rgba(0, 0, 0, 0.12)",
            "shallowBelow": "0px 4px 16px rgba(0, 0, 0, 0.12)",
            "deepAbove": "0px -16px 48px rgba(0, 0, 0, 0.22)",
            "deepBelow": "0px 16px 48px rgba(0, 0, 0, 0.22)"
        },
        "mediaQuery": {
            "small": "@media screen and (min-width: 320px)",
            "medium": "@media screen and (min-width: 600px)",
            "large": "@media screen and (min-width: 1136px)"
        },
        "sizing": {
            "scale0": "2px",
            "scale100": "4px",
            "scale200": "6px",
            "scale300": "8px",
            "scale400": "10px",
            "scale500": "12px",
            "scale550": "14px",
            "scale600": "16px",
            "scale650": "18px",
            "scale700": "20px",
            "scale750": "22px",
            "scale800": "24px",
            "scale850": "28px",
            "scale900": "32px",
            "scale950": "36px",
            "scale1000": "40px",
            "scale1200": "48px",
            "scale1400": "56px",
            "scale1600": "64px",
            "scale2400": "96px",
            "scale3200": "128px",
            "scale4800": "192px"
        },
        "typography": {
            "font100": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "font150": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font200": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font250": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font300": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font350": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font400": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font450": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "font550": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "font650": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "font750": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "font850": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "font950": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "font1050": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "font1150": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "font1250": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "font1350": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "font1450": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "ParagraphXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "ParagraphSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "ParagraphMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "ParagraphLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "LabelLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "fontSizeSm": "14px",
                "lineHeightTight": 1.25
            },
            "HeadingXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "HeadingSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "HeadingMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "HeadingLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "HeadingXLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "HeadingXXLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "DisplayXSmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "DisplaySmall": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "DisplayMedium": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "DisplayLarge": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "MonoParagraphXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "12px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "MonoParagraphSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "14px",
                "fontWeight": "normal",
                "lineHeight": "20px"
            },
            "MonoParagraphMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "16px",
                "fontWeight": "normal",
                "lineHeight": "24px"
            },
            "MonoParagraphLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "18px",
                "fontWeight": "normal",
                "lineHeight": "28px"
            },
            "MonoLabelXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "12px",
                "fontWeight": 500,
                "lineHeight": "16px"
            },
            "MonoLabelSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "14px",
                "fontWeight": 500,
                "lineHeight": "16px"
            },
            "MonoLabelMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "16px",
                "fontWeight": 500,
                "lineHeight": "20px"
            },
            "MonoLabelLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "18px",
                "fontWeight": 500,
                "lineHeight": "24px"
            },
            "MonoHeadingXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "20px",
                "fontWeight": 700,
                "lineHeight": "28px"
            },
            "MonoHeadingSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "24px",
                "fontWeight": 700,
                "lineHeight": "32px"
            },
            "MonoHeadingMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "28px",
                "fontWeight": 700,
                "lineHeight": "36px"
            },
            "MonoHeadingLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "32px",
                "fontWeight": 700,
                "lineHeight": "40px"
            },
            "MonoHeadingXLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "MonoHeadingXXLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "40px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "MonoDisplayXSmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "36px",
                "fontWeight": 700,
                "lineHeight": "44px"
            },
            "MonoDisplaySmall": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "44px",
                "fontWeight": 700,
                "lineHeight": "52px"
            },
            "MonoDisplayMedium": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "52px",
                "fontWeight": 700,
                "lineHeight": "64px"
            },
            "MonoDisplayLarge": {
                "fontFamily": "\"Lucida Console\", Monaco, monospace",
                "fontSize": "96px",
                "fontWeight": 700,
                "lineHeight": "112px"
            },
            "font460": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font470": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font500": {
                "fontFamily": "\"Source Sans Pro\", sans-serif",
                "fontSize": "1rem",
                "fontSizeSm": "14px",
                "fontWeight": "normal",
                "lineHeight": 1.6,
                "lineHeightTight": 1.25
            },
            "font600": {}
        },
        "zIndex": {
            "modal": 2000
        }
    },
    "primitives": {
        "primaryA": "#000000",
        "primaryB": "#FFFFFF",
        "primary": "#000000",
        "primary50": "#F6F6F6",
        "primary100": "#EEEEEE",
        "primary200": "#E2E2E2",
        "primary300": "#CBCBCB",
        "primary400": "#AFAFAF",
        "primary500": "#6B6B6B",
        "primary600": "#545454",
        "primary700": "#333333",
        "accent": "#276EF1",
        "accent50": "#EFF3FE",
        "accent100": "#D4E2FC",
        "accent200": "#A0BFF8",
        "accent300": "#5B91F5",
        "accent400": "#276EF1",
        "accent500": "#1E54B7",
        "accent600": "#174291",
        "accent700": "#102C60",
        "negative": "#E11900",
        "negative50": "#FFEFED",
        "negative100": "#FED7D2",
        "negative200": "#F1998E",
        "negative300": "#E85C4A",
        "negative400": "#E11900",
        "negative500": "#AB1300",
        "negative600": "#870F00",
        "negative700": "#5A0A00",
        "warning": "#FFC043",
        "warning50": "#FFFAF0",
        "warning100": "#FFF2D9",
        "warning200": "#FFE3AC",
        "warning300": "#FFCF70",
        "warning400": "#FFC043",
        "warning500": "#BC8B2C",
        "warning600": "#996F00",
        "warning700": "#674D1B",
        "positive": "#03703C",
        "positive50": "#E6F2ED",
        "positive100": "#ADDEC9",
        "positive200": "#66D19E",
        "positive300": "#06C167",
        "positive400": "#048848",
        "positive500": "#03703C",
        "positive600": "#03582F",
        "positive700": "#10462D",
        "white": "#FFFFFF",
        "black": "#000000",
        "mono100": "#FFFFFF",
        "mono200": "#F6F6F6",
        "mono300": "#EEEEEE",
        "mono400": "#E2E2E2",
        "mono500": "#CBCBCB",
        "mono600": "#AFAFAF",
        "mono700": "#6B6B6B",
        "mono800": "#545454",
        "mono900": "#333333",
        "mono1000": "#000000",
        "ratingInactiveFill": "#EEEEEE",
        "ratingStroke": "#CBCBCB",
        "primaryFontFamily": "system-ui, \"Helvetica Neue\", Helvetica, Arial, sans-serif"
    }
}
```
