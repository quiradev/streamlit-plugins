import html
import string

import random
from enum import Enum

import re

import htbuilder
import streamlit as st
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


def annotation(body: str, label: str, body_class: str, label_class: str, body_css: dict = None, label_css: dict = None):
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

    return span(
        _class=f'{body_class} {label.lower().replace(" ", "-")}',
        style=styles(
            **body_css,
        )
    )(
        html.escape(body),
        span(
            _class=label_class,
            style=styles(
                **label_css,
            )
        )(html.escape(label))
    )


def annotated_text(*tokens, annotation_style: dict = None, display_mode: AnnotationDisplayMode = AnnotationDisplayMode.NORMAL, _st=None):
    """Writes test with annotations into your Streamlit app.

    Parameters
    ----------
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

    _st: Streamlit object

    Examples
    --------

    >>> annotated_text(
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
    ...     "Hello ",
    ...     annotation("world!", "noun", body_css=dict(color="#8ef", border="1px dashed red")),
    ... )

    """

    # uuid_component = f"{random.randrange(16**5):05x}"
    uuid_component = ''.join((random.choice(string.ascii_letters) for x in range(8)))
    if _st is None:
        _st = st

    # display_mode = _st.radio(
    #     "Select display style",
    #     key=uuid_component,
    #     options=[AnnotationDisplayMode.NORMAL, AnnotationDisplayMode.MINIMAL, AnnotationDisplayMode.READING],
    #     index=display_mode.value,
    #     format_func=lambda x: x.name
    # )

    # annotated-text.normal annotation-container.displayed + annotation.side
    # annotated-text.minimal = annotation-container.displayed + annotation.floating
    # annotated-text.reading = annotation-container.compressive + annotation.floating
    out = div(
        _id=uuid_component,
        _class=f"annotated-text {display_mode.name.lower()}",
    )

    if annotation_style is None:
        annotation_style = {}
        # Generamos el mapa de anotaciones, asignando un color unico a cada una
        annotation_tags = list(set([x[1] for x in tokens if isinstance(x, tuple)]))
        if len(annotation_tags) > 0:
            colors_list = generate_hsla_colors(70, 50, 1, len(annotation_tags))
            for tag in annotation_tags:
                bg, fg = colors_list.pop()
                annotation_style[tag] = (bg, fg)

    annotations_style_colors = "<style>"
    for tag, colors in annotation_style.items():
        bg = [colors[0], colors[0]]
        fg = colors[-1]
        if len(colors) > 2:
            bg = colors[0:-1]

        annotations_style_colors += f"""
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} {{
                background-image: linear-gradient({', '.join(bg)});
                color: {fg};
            }}
            div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")}:hover {{
                color: {fg} !important;
            }}
        """
        # Se agrega un borde al label si esta en modo minimal
        if display_mode == AnnotationDisplayMode.MINIMAL:
            annotations_style_colors += f"""
               div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} .annotation:before {{
                  border-color: inherit;
               }}
            """
        else:
            annotations_style_colors += f"""
               div.annotated-text#{uuid_component} .annotation-container.{tag.lower().replace(" ", "-")} .annotation:before {{
                  border-color: {bg[0]};
               }}
            """

    annotations_style_colors += "</style>"

    # Se asigna la clase del contenedor y de la anotacion para los estilos
    annotation_container_class = f"annotation-container {AnnotaionContainerClass[display_mode.name].value}"
    annotation_class = f"annotation {AnnotaionClass[display_mode.name].value}"

    for tok in tokens:
        if isinstance(tok, str):
            out(html.escape(tok))

        elif isinstance(tok, HtmlElement):
            out(tok)

        elif isinstance(tok, tuple):
            body, label = tok[0:2]
            body_css = {}
            label_css = {}
            if len(tok) == 3:
                body_css = tok[2]
            if len(tok) == 4:
                label_css = tok[3]

            out(annotation(*tok, annotation_container_class, annotation_class, body_css=body_css, label_css=label_css))

        else:
            raise Exception("Oh noes!")

    raw_html = str(out)
    raw_html = raw_html.replace("\n", "<div></div>")

    # Genera un texto HTML con 3 radio inputs, uno por cada modo de visualización
    # de anotaciones.
    choice_raw = f"""
    <style>
        .annotated-style-label {{
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

    normal_id = f"input#{uuid_component}-annotated-style-normal:checked ~ div.annotated-text"
    minimal_id = f"input#{uuid_component}-annotated-style-minimal:checked ~ div.annotated-text"
    reading_id = f"input#{uuid_component}-annotated-style-reading:checked ~ div.annotated-text"
    # normal_id = f"div.annotated-text.normal"
    # minimal_id = f"div.annotated-text.minimal"
    # reading_id = f"div.annotated-text.reading"
    normal_style = f"""
    <style>
        {normal_id} span.annotation-container {{
            border-radius: 0.33rem;
            display: inline-flex;
            justify-content: center;
            align-items: center;
        }}

        {normal_id} span.annotation-container {{
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
    </style>
    """
    minimal_style = f"""
    <style>
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

        {minimal_id} span.annotation-container:hover span.annotation {{
            display: flex;
            top: -100%;
            width: max-content;
            padding: 0 0.5em;
        }}
        {minimal_id} span.annotation-container:hover span.annotation:before {{
            position: absolute;
            content: "";
            width: 0px;
            height: 0px;
            border-top: 0.5em solid;
            border-right: 0.5em solid transparent !important;
            border-bottom: 0.5em solid transparent !important;
            border-left: 0.5em solid transparent !important;
            top: 100%;
            z-index: 1;
        }}
    </style>
    """
    reading_style = f"""
    <style>
        {reading_id} span.annotation-container {{
            display: inline-flex;
            border-radius: 0.33rem;
            justify-content: center;
            align-items: center;
            color: inherit;
        }}

        {reading_id} span.annotation-container {{
            text-decoration: none;
            background-size: 100% 2px, 0 2px;
            background-position: 100% 100%, 0 100%;
            background-repeat: no-repeat;
            transition: background-size 0.2s linear;

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

        {reading_id} span.annotation-container:hover span.annotation {{
            display: flex;
            position: absolute;
            top: -100%;
            width: max-content;
            padding: 0 0.5em;
            background: inherit;
            border-radius: 0.5em;

            background-size: 100% 100%, 100% 0;
        }}
        {reading_id} span.annotation-container:hover span.annotation:before {{
            content: "";
            position: absolute;
            width: 0px;
            height: 0px;
            border-top: 0.5em solid;
            border-right: 0.5em solid transparent !important;
            border-bottom: 0.5em solid transparent !important;
            border-left: 0.5em solid transparent !important;
            top: 100%;
            z-index: 1;
        }}
    </style>
    """
    # display_styles_map = {
    #     AnnotationDisplayMode.NORMAL: normal_style,
    #     AnnotationDisplayMode.MINIMAL: minimal_style,
    #     AnnotationDisplayMode.READING: reading_style
    # }

    styles_tags = normal_style + minimal_style + reading_style + annotations_style_colors
    # styles_tags = styles_tags.replace("\n", "")
    styles_tags = styles_tags.strip("\n")

    choice_raw = choice_raw.replace("\n", "")

    _st.write(styles_tags + choice_raw + raw_html, unsafe_allow_html=True)
