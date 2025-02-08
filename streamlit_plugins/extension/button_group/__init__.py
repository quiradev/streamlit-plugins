from typing import Literal, Sequence, Any, Callable

import streamlit as st
from streamlit.elements.lib.options_selector_utils import convert_to_sequence_and_check_comparable, get_default_indices
from streamlit.elements.widgets.button_group import SingleOrMultiSelectSerde, V
from streamlit.errors import StreamlitAPIException
from streamlit.proto.ButtonGroup_pb2 import ButtonGroup as ButtonGroupProto
from streamlit.runtime.state import WidgetCallback
from streamlit.string_util import validate_material_icon


def st_button_group(
    options: Sequence[Any],
    *,
    default: Sequence[V] | V | None = None,
    selection_mode: Literal["single", "multi"] = "single",
    selection_visualization: Literal["only_selected", "all_up_to_selected"] = "only_selected",
    disabled: bool = False,
    format_func: Callable[[Any], str] | None = None,
    style: Literal["borderless", "pills", "segmented_control"] = "pills",
    on_change: WidgetCallback | None = None,
    args=None,
    kwargs=None,
    label: str | None = None,
    label_visibility: Literal["visible", "hidden", "collapsed"] = "visible",
    keep_selection: Literal["always_visible", "never_visible"] = None,
    key: str = "button_group",
):
    i_key = 0
    # if f"{key}_{i_key}__check" in st.session_state:
    #     # Exist a button with this value
    #     if st.session_state[f"{key}_{i_key}__check"]:
    #         i_key += 1
    #         st.session_state[f"{key}_{i_key}__check"] = False

    unique_key = f"{key}_{i_key}"

    indexable_options = convert_to_sequence_and_check_comparable(options)
    default_values = get_default_indices(indexable_options, default)

    serde: SingleOrMultiSelectSerde[V] = SingleOrMultiSelectSerde[V](
        indexable_options, default_values, selection_mode
    )
    if selection_visualization == "only_selected":
        selection_visualization = ButtonGroupProto.SelectionVisualization.ONLY_SELECTED
    elif selection_visualization == "all_up_to_selected":
        selection_visualization = ButtonGroupProto.SelectionVisualization.ALL_UP_TO_SELECTED

    def _transformed_format_func(option: V) -> ButtonGroupProto.Option:
        """If option starts with a material icon or an emoji, we extract it to send
        it parsed to the frontend."""
        transformed = format_func(option) if format_func else str(option)
        transformed_parts = transformed.split(" ")
        icon: str | None = None
        if len(transformed_parts) > 0:
            maybe_icon = transformed_parts[0].strip()
            try:
                # we only want to extract material icons because we treat them
                # differently than emojis visually
                if maybe_icon.startswith(":material"):
                    icon = validate_material_icon(maybe_icon)
                    # reassamble the option string without the icon - also
                    # works if len(transformed_parts) == 1
                    transformed = " ".join(transformed_parts[1:])
            except StreamlitAPIException:
                # we don't have a valid icon or emoji, so we just pass
                pass
        return ButtonGroupProto.Option(
            content=transformed,
            content_icon=icon,
        )

    params = dict(
        indexable_options=indexable_options,
        label=label,
        default=default_values,
        disabled=disabled,
        on_change=on_change, args=args, kwargs=kwargs,
        format_func=_transformed_format_func,
        selection_visualization=selection_visualization,
        style=style,
        selection_mode=selection_mode,
        label_visibility=label_visibility,
        key=unique_key,
        serializer=serde.serialize,
        deserializer=serde.deserialize,
    )

    if selection_mode == "single" and keep_selection == "always_visible":
        view = st.empty()
        if st.session_state.get(unique_key) is None:
            st.session_state[unique_key] = st.session_state.get(f"{unique_key}__prev_value", default)
            params["default"] = get_default_indices(indexable_options, st.session_state.get(f"{unique_key}__prev_value", default))
        with view:
            res = st._main._button_group(**params)
            # st.session_state[f"{unique_key}__check"] = True

    elif selection_mode == "single" and keep_selection == "never_visible":
        view = st.empty()
        if st.session_state.get(unique_key) is not None:
            st.session_state[unique_key] = st.session_state.get(f"{unique_key}__prev_value", default)
            params["default"] = None
        with view:
            res = st._main._button_group(**params)
            # st.session_state[f"{unique_key}__check"] = True

    else:
        res = st._main._button_group(**params)
        # st.session_state[f"{unique_key}__check"] = True

    if selection_mode == "multi":
        return res.value

    st.session_state[f"{unique_key}__prev_value"] = res.value

    return res.value
