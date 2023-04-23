import hashlib
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from hashlib import md5
from typing import Any, List, Mapping, Optional, Tuple, Dict, Type, TypeVar

import streamlit.components.v1 as components
import streamlit as st

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
# (This is, of course, optional - there are innumerable ways to manage your
# release process.)
_RELEASE = os.getenv("RELEASE", "").upper() != "DEV"

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function "_component_func", with an underscore prefix, because we don't want
# to expose it directly to users. Instead, we will create a custom wrapper
# function, below, that will serve as our component's public API.

# It's worth noting that this call to `declare_component` is the
# *only thing* you need to do to create the binding between Streamlit and
# your component frontend. Everything else we do in this file is simply a
# best practice.

if not _RELEASE:
    _component_func = components.declare_component(
        # We give the component a simple, descriptive name ("my_component"
        # does not fit this bill, so please choose something better for your
        # own component :)
        "labelstudio",
        # Pass `url` here to tell Streamlit that the component will be served
        # by the local dev server that you run via `npm run start`.
        # (This is useful while your component is in development.)
        url="http://localhost:3000",
    )
else:
    # When we're distributing a production version of the component, we'll
    # replace the `url` param with `path`, and point it to to the component's
    # build directory:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_labelstudio_builder", path=build_dir)


SATURATION = 70
LIGHTNESS = 50
ALPHA = 1


@st.cache_data
def _make_rgb(key: str) -> str:
    k = key.encode()
    hash = md5(k).hexdigest()
    return hash[:6]

@st.cache_data
def hsla_to_hex(hue: int, saturation: int, lightness: int, alpha: float) -> str:
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
def make_hash_color(name: str, saturation: int, lightness: int, alpha: float) -> str:
    # Obtener un número hash único para el nombre
    hash_num = int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16)

    # Convertir el hash en valores de H (matiz), S (saturación) y L (brillo)
    h = hash_num % 256

    hex_color = hsla_to_hex(h, saturation, lightness, alpha)
    return hex_color


@st.cache_data
def generate_hash_colors(names: List[str], saturation: int, lightness: int, alpha: float) -> List[str]:
    colors = []
    for name in names:
        hex_color = make_hash_color(name, saturation, lightness, alpha)
        colors.append(hex_color)
    return colors


@st.cache_data
def get_color_pallete(types_list: List[str]) -> Dict[str, str]:
    # colors = generate_hsla_colors(70, 50, 1, len(types_list))
    colors = generate_hash_colors(types_list, SATURATION, LIGHTNESS, ALPHA)
    colored_patterns = dict(zip(types_list, colors))
    return colored_patterns


@dataclass
class LabelStudioUser:
    pk: int
    firstName: str
    lastName: str

    def dumps(self):
        return asdict(self)


class LabelStudioTask(ABC):
    ...

# LabelStudioTaskType = TypeVar(bound=LabelStudioTask)

DEFAULT_USER = LabelStudioUser(pk=-1, firstName="who", lastName="knows")


class STLabelStudioComponent(ABC):
    FROM_NAME = "label"
    TO_NAME = "text"
    TEXT_KEY = "text"

    def __init__(self, tasks: List[LabelStudioTask], *args, user: LabelStudioUser = DEFAULT_USER, **kwargs):
        self.tasks = tasks
        self.user = user
        self.config = self.make_xml(*args, **kwargs)

    @abstractmethod
    def make_xml(self, *args, **kwargs):
        raise NotImplemented

    @abstractmethod
    def make_interfaces(self):
        raise NotImplemented

    def run_task(self, task: Dict):
        # Arguments passed here will be sent to the frontend as "args" dictionary.
        return st_labelstudio(self.config, self.make_interfaces(), self.user.dumps(), task)


@dataclass(frozen=True)
class ResultLSNER:
    start: int
    end: int
    text: str
    labels: List[str]

    def to_ls(self) -> Dict[str, Any]:
        return {
            "from_name": STLabelStudioNER.FROM_NAME,
            "to_name": STLabelStudioNER.TO_NAME,
            "type": "labels",
            "value": asdict(self),
        }


@dataclass
class LSTaskNER(LabelStudioTask):
    id: int
    text: str
    annotations: List[ResultLSNER] = None
    predictions: list = None


class STLabelStudioNER(STLabelStudioComponent):
    FROM_NAME = "label"
    TO_NAME = "text"
    TEXT_KEY = "text"

    def __init__(self, tasks: List[LSTaskNER], labels: List[str], user: LabelStudioUser = DEFAULT_USER, colors: Dict[str, str] = None, with_filters=False, with_relevance=False, with_confidence=False):
        super().__init__(tasks, labels, user=user, colors=colors, with_filters=with_filters, with_relevance=with_relevance, with_confidence=with_confidence)

    def make_xml(self, labels: List[str], colors: Dict[str, str] = None, with_filters=False, with_relevance=False, with_confidence=False) -> str:
        if colors is None:
            colors = get_color_pallete(labels)

        tags = []
        tags.append("<View>")
        if with_filters:
            tags.append(f'<Filter name="filter" toName="{self.FROM_NAME}" hotkey="shift+f" minlength="1" />')

        tags.append(f'<Labels name="{self.FROM_NAME}" toName="{self.TO_NAME}">')
        tags.extend(
            f'<Label value="{label}" background="{colors.get(label, make_hash_color(label, SATURATION, LIGHTNESS, ALPHA))}"/>'
            for label in labels
        )
        tags.append("</Labels>")
        tags.append("<Style>.htx-text{ white-space: pre-wrap; }</Style>")
        tags.append(f'<Text name="{self.TO_NAME}" value="${self.TEXT_KEY}" granularity="word" />')
        if with_relevance:
            tags.append('<Choices name="relevance" toName="text" perRegion="true">')
            tags.append('<Choice value="Relevant" />')
            tags.append('<Choice value="Non Relevant" />')
            tags.append('</Choices>')
        tags.append("</View>")

        if with_confidence:
            tags.append('<View visibleWhen="region-selected">')
            tags.append('<Header value="Your confidence" />')
            tags.append('</View>')
            tags.append('<Rating name="confidence" toName="text" perRegion="true" />')

        return "\n".join(tags)

    def run_task(self, task: LSTaskNER) -> Dict[str, Any]:
        processed_annotations: ResultLSNER = task.annotations
        if processed_annotations is None:
            processed_annotations = []

        return super().run_task({
            "id": task.id,
            "data": {self.TEXT_KEY: task.text},
            "annotations": [{"result": [v.to_ls() for v in processed_annotations]}],
            "predictions": []
        })

    def make_interfaces(self) -> List[str]:
        return [
            "panel",  # Enable navigaion panel for the current task with buttons: undo, redo and reset.
            "submit",  # Show a button to submit or update the current annotation.
            "update",  # Show a button to update the current task after submitting.
            "skip",  # Show a button to skip the current task.
            "controls",  # Enable panel with controls (submit, update, skip).
            "infobar",  # A show button for information.
            "topbar",  # A labeling interface that lists the top-level items in the Label Studio UI.
            "instruction",  # A button for the instructions.
            "side-column",  # Show a column on the left or right side of the Label Studio UI.
            "annotations:history",  # A show button for annotation history.
            "annotations:tabs",  # A show button for annotation tabs.
            "annotations:menu",  # A show button for the annotation menu.
            "annotations:current",  # A show button for the current annotation.
            "annotations:add-new",  # A show button to add new annotations.
            "annotations:delete",  # A show button to delete the current annotation.
            "annotations:view-all",  # A show button to view all annotations.
            "predictions:tabs",  # Show predictions tabs.
            "predictions:menu",  # Show predictions menu.
            "auto-annotation",  # Show auto annotations.
            "edit-history"  # Show edit history.
        ]


    def get_results(self, annotation: Dict[str, Any]) -> List[ResultLSNER]:
        return [
            ResultLSNER(
                start=v["start"],
                end=v["end"],
                text=v["text"],
                labels=v["results"][0]["value"]["labels"],
            )
            for v in annotation["areas"].values()
        ]


def st_labelstudio(config, interfaces, user, task):
    component_value = _component_func(config=config, interfaces=interfaces, user=user, task=task)
    return component_value


