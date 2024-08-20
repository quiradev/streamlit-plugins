import sys
import time

try:
    if '_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper' not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

import streamlit as st

from streamlit_plugins.components.annotated_text import annotated_text, annotation


def generate_stream():
    yield "|\t"
    size = 5
    for i in range(size):
        yield f"Stream element {i}\t"
        time.sleep(0.5)

        if i != size - 1:
            yield "|\t"

    yield "|"


st.title("Annotated Text Example")

st.divider()

st.subheader("You can change the inputs of annotated and the rest of the application not be affected a complete reruning")
# st.write_stream(generate_stream())

st.divider()

annotated_text(
    "Hello ", ("world", "noun"), "!",
    annotation_style={"noun": {"background-image": "linear-gradient(cadetblue, royalblue)", "border": "2px dashed powderblue"}},
    front_inputs=True,
    key="annotated_text_1"
)

annotated_text(
    "This ",
    ("is", "verb"),
    " some ",
    ("annotated", "adj"),
    ("text", "noun"),
    " for those of ",
    ("you", "pronoun"),
    " who ",
    ("like", "verb"),
    " this sort of ",
    ("thing", "noun"),
    key="annotated_text_2"
)

annotated_text(
    "Hello ",
    ((("Pedro", "name"), ("Ramon", "surname"), ("Jimenez", "surname")), "person"),
    key="annotated_text_3"
)




