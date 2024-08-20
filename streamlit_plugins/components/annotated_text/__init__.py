import hashlib
import html
import random
import string
from enum import Enum
from typing import List, Union, Tuple

import streamlit as st
import webcolors
from htbuilder import H, HtmlElement, styles
from htbuilder.units import unit


@st.cache_data
def hsla_to_hex(hue, saturation, lightness, alpha):
    lightness /= 100
    _a = saturation * min(lightness, 1 - lightness) / 100
    alpha = str(hex(int(alpha * 255)))[2:]

    def _calculate(val):
        k = (val + hue / 30) % 12
        color = lightness - _a * max(min(k - 3, 9 - k, 1), -1)
        return str(hex(int(255 * color)))[2:].zfill(2)

    # convert to Hex and prefix "0" if needed
    return f"#{_calculate(0)}{_calculate(8)}{_calculate(4)}{alpha}"


@st.cache_data
def contrast_color(hex_color: str, bw=True):
    def _padZero(str, size=2):
        zeros = "0" * size
        return (zeros + str)[-size:]

    alpha = ""
    if hex_color[0] == "#":
        hex_color = hex_color[1:]

    # convert 3-digit hex to 6-digits.
    if len(hex_color) == 3:
        hex_color = hex_color[0] + hex_color[0] + hex_color[1] + hex_color[1] + hex_color[2] + hex_color[2]
    if len(hex_color) != 6:
        alpha = hex_color[-2:]

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # https://stackoverflow.com/a/3943023/112731
    if bw:
        return f"#000000{alpha}" if r * 0.299 + g * 0.587 + b * 0.114 > 186 else f"#FFFFFF{alpha}"

    # invert color components
    r = str(hex(255 - r))[2:]
    g = str(hex(255 - g))[2:]
    b = str(hex(255 - b))[2:]
    # pad each with zeros and return
    return "#" + _padZero(r) + _padZero(g) + _padZero(b) + alpha


@st.cache_data
def generate_hsla_colors(saturation, lightness, alpha, amount):
    huedelta = 360 // amount
    return [
        (
            hsla_to_hex(i * huedelta, saturation, lightness, alpha),
            contrast_color(hsla_to_hex(i * huedelta, saturation, lightness, alpha), bw=True)
        )
        for i in range(amount)
    ]


def get_color_pallete(types_list: list[str]) -> dict[str, tuple[str, str]]:
    # colors = generate_hsla_colors(70, 50, 1, len(types_list))
    colors = generate_hash_colors(types_list, 70, 50, 1)
    colored_patterns = dict(zip(types_list, colors))
    return colored_patterns


def generate_hash_colors(names: list[str], saturation: int, lightness: int, alpha: float) -> list[tuple[str, str]]:
    colors = []
    for name in names:
        # Obtener un número hash único para el nombre
        hash_num = int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16)

        # Convertir el hash en valores de H (matiz), S (saturación) y V (brillo)
        h = hash_num % 256
        # Variacion de la saturacion en base al hash de un 20%
        s = saturation + (hash_num % 51) - 25
        # Variacion de la luminosidad de un 10% en base al hash
        l = lightness + (hash_num % 26) - 13

        colors.append(
            (
                hsla_to_hex(h, s, l, alpha),
                contrast_color(hsla_to_hex(h, s, l, alpha), bw=True)
            )
        )
    return colors

# Only works in 3.7+: from htbuilder import div, span
div = H.div
span = H.span

# Only works in 3.7+: from htbuilder.units import px, rem, em
px = unit.px
rem = unit.rem
em = unit.em


class AnnotationDisplayMode(Enum):
    NORMAL = 0
    MINIMAL = 1
    READING = 2


class AnnotaionContainerClass(Enum):
    NORMAL = "displayed"
    MINIMAL = "displayed"
    READING = "compressive"


class AnnotaionClass(Enum):
    NORMAL = "side"
    MINIMAL = "floating"
    READING = "floating"


CSS_COLOR_MAP = {
    "transparent": "#00000000",
    "gray": "#808080",
}

def annotation(body: str | HtmlElement, label: str, body_css: dict = None, label_css: dict = None):
    """Build an HtmlElement span object with the given body and annotation label.

    The end result will look something like this:

        [body | label]

    Parameters
    ----------
    body : string
        The string to put in the "body" part of the annotation.
    label : string
        The string to put in the "label" part of the annotation.
    body_class: str

    label_class: str

    body_css : dict
        The string to put in the "body" part of the annotation.
    label_css : dict
        The color to use for the background "chip" containing this annotation.

    Examples
    --------

    Produce a simple annotation with default colors:

    >>> annotation("apple", "fruit")

    Produce an annotation with custom colors:

    >>> annotation("apple", "fruit", label_css={"background":"#FF0", "color":"black"})

    Produce an annotation with crazy CSS:

    >>> annotation("apple", "fruit", label_css={'background':"#FF0", 'border':"1px dashed red"})

    """

    if body_css is None:
        body_css = {}
    if label_css is None:
        label_css = {}

    # Se asigna la clase del contenedor y de la anotacion para los estilos
    body_class = f"annotation-container"
    label_class = f"annotation"

    return H.span(
        _class=f'{body_class} {label.lower().replace(" ", "-")}',
        _data_label=label,
        style=styles(
            **body_css,
        )
    )(
        span(
            _class=label_class,
            style=styles(
                **label_css,
            )
        )(html.escape(label)),
        html.escape(body) if isinstance(body, str) else body
    )


def extract_labels(tokens) -> list[str]:
    # Extraccion recursiva de las etiquetas de anotacion
    labels = []
    for tok in tokens:
        if isinstance(tok, tuple):
            labels.append(tok[1])
            if isinstance(tok[0], tuple):
                labels.extend(extract_labels(tok[0]))

    return list(set(labels))


def resolve_background_style(styles_map: dict[str, str]) -> str:
    bg = styles_map.get("background", None)
    if bg is not None:
        return CSS_COLOR_MAP.get(bg, bg)

    # Try to get from background-image
    # Support for linear-gradient
    bg_image = styles_map.get("background-image", None)
    if bg_image is not None:
        if bg_image.startswith("linear-gradient"):
            bg = bg_image.split("linear-gradient(")[1].split(",")[0]
            return CSS_COLOR_MAP.get(bg, bg)

    # Try to get crontrast from color
    fg = styles_map.get("color", None)
    if fg is not None:
        fg = CSS_COLOR_MAP.get(fg, fg)
        return contrast_color(fg)

    # Defaults to gray
    return CSS_COLOR_MAP["gray"]


@st.experimental_fragment
def annotated_text(
    *tokens, annotation_style: dict[str, dict[str, str]] = None,
    display_mode: AnnotationDisplayMode = AnnotationDisplayMode.NORMAL,
    without_styles=False,
    front_inputs=False,
    key="annotated_text",
):
    """Writes test with annotations into your Streamlit app.

    Parameters
    ----------
    key : str
    *tokens : str, tuple or htbuilder.HtmlElement
        Arguments can be:
        - strings, to draw the string as-is on the screen.
        - tuples of the form (main_text, annotation_text) where
            background and foreground colors are optional and should be an CSS-valid string such as
            "#aabbcc" or "rgb(10, 20, 30)"
        - HtmlElement objects in case you want to customize the annotations further. In particular,
            you can import the `annotation()` function from this module to easily produce annotations
            whose CSS you can customize via keyword arguments.

    annotation_style: dict

    display_mode: AnnotationDisplayMode

    front_inputs: bool

    without_styles: bool

    Examples
    --------

    >>> annotated_text(
    ...     "example",
    ...     "This ",
    ...     ("is", "verb", dict(background="#8ef")),
    ...     " some ",
    ...     ("annotated", "adj", dict(background="#faa")),
    ...     ("text", "noun", dict(background="#afa")),
    ...     " for those of ",
    ...     ("you", "pronoun", dict(background="#fea")),
    ...     " who ",
    ...     ("like", "verb", dict(background="#8ef")),
    ...     " this sort of ",
    ...     ("thing", "noun", dict(background="#afa")),
    ... )

    >>> annotated_text(
    ...     "example",
    ...     "Hello ",
    ...     annotation("world!", "noun", body_css=dict(color="#8ef", border="1px dashed red")),
    ... )

    """

    if f"{key}_annotated_text_uuid" not in st.session_state:
        st.session_state[f"{key}_annotated_text_uuid"] = ''.join((random.choice(string.ascii_letters) for x in range(8)))

    uuid_component = st.session_state[f"{key}_annotated_text_uuid"]

    if not front_inputs:
        options = list(map(lambda x: x.name, [*AnnotationDisplayMode]))
        display_mode_in = st.radio(
            "Select display style",
            key=uuid_component,
            options=options,
            horizontal=True,
            index=options.index(display_mode.name)
        )
        display_mode = AnnotationDisplayMode[display_mode_in.upper()]

    out = div(
        _id=uuid_component,
        _class=f"annotated-text {display_mode.name.lower()}",
    )

    def create_out_html(_out: HtmlElement, *toks) -> HtmlElement:
        for tok in toks:
            if isinstance(tok, str):
                _out(html.escape(tok))

            elif isinstance(tok, HtmlElement):
                _out(tok)

            elif isinstance(tok, tuple):
                body, label = tok[0:2]
                if isinstance(body, tuple):
                    # Anidamiento de anotaciones
                    body = create_out_html(H.span(), *body)

                body_css = {}
                label_css = {}
                if len(tok) == 3:
                    body_css = tok[2]
                if len(tok) == 4:
                    label_css = tok[3]

                _out(annotation(body, label, body_css=body_css, label_css=label_css))

            else:
                raise Exception("Oh noes!")

        return _out

    # Genera un texto HTML con 3 radio inputs, uno por cada modo de visualización
    # de anotaciones.
    choice_raw = f"""
        <style>
            .annotated-style-label {{
                margin-right: 1em;
                margin-top: 1em;
                margin-bottom: 1em;
                display: inline-block;
                margin-right: 1em;
                cursor: pointer;
                user-select: none;
            }}
        </style>
        <input class="annotated-style-input" {"checked" if display_mode == AnnotationDisplayMode.NORMAL else ""} type="radio" name="{uuid_component}-annotation-style-mode" id="{uuid_component}-annotated-style-normal" value="{AnnotationDisplayMode.NORMAL.name.lower()}">
        <label class="annotated-style-label" for="{uuid_component}-annotated-style-normal">Normal</label>

        <input class="annotated-style-input" {"checked" if display_mode == AnnotationDisplayMode.MINIMAL else ""} type="radio" name="{uuid_component}-annotation-style-mode" id="{uuid_component}-annotated-style-minimal" value="{AnnotationDisplayMode.MINIMAL.name.lower()}">
        <label class="annotated-style-label" for="{uuid_component}-annotated-style-minimal">Minimal</label>

        <input class="annotated-style-input" {"checked" if display_mode == AnnotationDisplayMode.READING else ""} type="radio" name="{uuid_component}-annotation-style-mode" id="{uuid_component}-annotated-style-reading" value="{AnnotationDisplayMode.READING.name.lower()}">
        <label class="annotated-style-label" for="{uuid_component}-annotated-style-reading">Reading</label>
        """

    out = create_out_html(out, *tokens)

    raw_html = str(out)
    raw_html = raw_html.replace("\n", "<div></div>")

    if without_styles:
        st.markdown(raw_html, unsafe_allow_html=True)

    if front_inputs:
        normal_id = f"input#{uuid_component}-annotated-style-normal:checked ~ div.annotated-text"
        minimal_id = f"input#{uuid_component}-annotated-style-minimal:checked ~ div.annotated-text"
        reading_id = f"input#{uuid_component}-annotated-style-reading:checked ~ div.annotated-text"
    else:
        normal_id = f"div.annotated-text#{uuid_component}.normal"
        minimal_id = f"div.annotated-text#{uuid_component}.minimal"
        reading_id = f"div.annotated-text#{uuid_component}.reading"


    if annotation_style is None:
        annotation_style = {}
        # Generamos el mapa de anotaciones, asignando un color unico a cada una
        annotation_tags = extract_labels(tokens)
        if len(annotation_tags) > 0:
            colors_map = get_color_pallete(annotation_tags)
            for tag in annotation_tags:
                bg, fg = colors_map[tag]
                annotation_style[tag] = {"background": bg, "border-color": bg, "color": fg}

    annotations_style_colors = f"""
        .annotated-text {{
            margin-bottom: 2em;
        }}
        div.annotated-text#{uuid_component} .annotation-container {{
            background-image: linear-gradient(gray, gray);
        }}
        div.annotated-text#{uuid_component} .annotation-container > .annotation:before {{
            border-color: gray !important;
        }}
        div.annotated-text#{uuid_component} .annotation-container > .annotation,
        div.annotated-text#{uuid_component} .annotation-container:hover {{
            color: white;
        }}
    """
    for tag, ann_styles_map in annotation_style.items():
        # Defaults
        ann_styles_map["background"] = resolve_background_style(ann_styles_map)
        ann_styles_map["background-image"] = ann_styles_map.get('background-image', f"linear-gradient({ann_styles_map['background']}, {ann_styles_map['background']})")
        border_color = ann_styles_map.get("border-color", ann_styles_map["background"])
        if border_color == CSS_COLOR_MAP["transparent"]:
            border_color = "currentColor"

        if ann_styles_map["background"] in webcolors.names():
            ann_styles_map["background"] = webcolors.name_to_hex(ann_styles_map["background"])

        if not ann_styles_map["background"].startswith("#"):
            raise ValueError("Only hex colors are supported for background")

        if "color" not in ann_styles_map and (ann_styles_map["background"] == CSS_COLOR_MAP["transparent"] or ann_styles_map["background"][-2:] == "00"):
            color = "currentColor"
        else:
            color = ann_styles_map.get("color", contrast_color(ann_styles_map["background"]))

        ann_styles = "\n".join(f"{style_name}: {style_val};" for style_name, style_val in ann_styles_map.items() if style_name != "background")
        annotations_style_colors += f"""
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} {{
                {ann_styles}
            }}
            {normal_id} .annotation-container.{tag.lower().replace(" ", "-")},
            {minimal_id} .annotation-container.{tag.lower().replace(" ", "-")},
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} > .annotation,
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")}:hover {{
                color: {color};
            }}
        """

        annotations_style_colors += f"""
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} > .annotation:before {{
                border-color: {border_color} !important;
            }}
        """


    normal_style = f"""
        span.annotation-container {{
            font-weight: bold;
        }}

        {normal_id} span.annotation-container {{
            border-radius: 0.33rem;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            flex-direction: row-reverse;
        }}

        span.annotation-container {{
            padding: 0px 0.67rem;
        }}

        {normal_id} span.annotation-container span.annotation {{
            display: flex;
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
        }}
        {normal_id} span.annotation-container span.annotation {{
            padding-left: 0.5rem;
            font-size: 0.67em;
            opacity: 0.8;
        }}
    """
    minimal_style = f"""
        {minimal_id} span.annotation-container {{
            border-radius: 0.33rem;
            display: inline-flex;
            justify-content: center;
            align-items: center;
        }}
        {minimal_id} span.annotation-container {{
            padding: 0px 0.67rem;
        }}

        {minimal_id} span.annotation-container {{
            position: relative;
        }}

        {minimal_id} span.annotation-container span.annotation {{
            display: flex;
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
        }}

        {minimal_id} span.annotation-container span.annotation {{
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
        }}

        {minimal_id} span.annotation-container span.annotation {{
            display: none;
            font-size: 0.8em;
            opacity: 1;
            background: inherit;
            position: absolute;
            border-radius: 0.5em;
            border: 2px solid white;
        }}

        {minimal_id} span.annotation-container:hover > span.annotation {{
            display: flex;
            top: -100%;
            width: max-content;
            padding: 0 0.5em;
        }}
        {minimal_id} span.annotation-container:hover > span.annotation:before {{
            position: absolute;
            content: "";
            width: 0px;
            height: 0px;
            border-top-width: 0.5em;
            border-top-style: solid;
            border-right: 0.5em solid transparent !important;
            border-bottom: 0.5em solid transparent !important;
            border-left: 0.5em solid transparent !important;
            top: 90%;
            z-index: 1;
        }}
    """
    reading_style = f"""
        {reading_id} span.annotation-container {{
            display: inline-flex;
            border-radius: 0.33rem;
            justify-content: center;
            align-items: center;
            color: inherit;
        }}

        {reading_id} span.annotation-container {{
            color: inherit;
            text-decoration: none;
            background-size: 100% 2px, 0 2px;
            background-position: 100% 100%, 0 100%;
            background-repeat: no-repeat;
            transition: color 0.2s, background-size 0.2s linear;

            position: relative;
        }}
        {reading_id} span.annotation-container:hover {{
            background-size: 100% 100%, 100% 0;
        }}

        {reading_id} span.annotation-container span.annotation {{
            display: none;
            font-size: 0.8em;
            opacity: 1;
            align-items: center;
            justify-content: center;
            text-transform: uppercase;
        }}

        {reading_id} span.annotation-container:hover > span.annotation {{
            display: flex;
            position: absolute;
            top: -100%;
            width: max-content;
            padding: 0 0.5em;
            background: inherit;
            border-radius: 0.5em;

            background-size: 100% 100%, 100% 0;
        }}
        {reading_id} span.annotation-container:hover > span.annotation:before {{
            content: "";
            position: absolute;
            width: 0px;
            height: 0px;
            border-top: 0.5em solid;
            border-right: 0.5em solid transparent !important;
            border-bottom: 0.5em solid transparent !important;
            border-left: 0.5em solid transparent !important;
            top: 90%;
            z-index: 1;
        }}

        {reading_id} span.annotation:hover {{
            opacity: 1 !important;
            z-index: 100;
        }}
    """

    styles = "<style>\n" + normal_style + minimal_style + reading_style + annotations_style_colors + "</style>"
    styles = styles.strip("\n")

    choice_raw = choice_raw.replace("\n", "")

    if front_inputs:
        res_html = styles + choice_raw + raw_html
    else:
        res_html = styles + raw_html

    st.markdown(res_html, unsafe_allow_html=True)
