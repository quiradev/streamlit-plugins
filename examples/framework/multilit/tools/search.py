import streamlit as st
st.title("Search")
_LOREM_IPSUM = [
    "Lorem", "ipsum", "dolor", "sit", "amet,", "consectetur",
    "adipiscing", "elit.", "Sed", "nec", "urna", "felis.",
    "Cras", "eleifend", "for ", "dolor", "at", "congue.",
    "Maecenas", "vel", "nunc", "sit", "amet", "libero", "suscipit",
    "ultrices."
]

import time


def stream_data():
    for word in _LOREM_IPSUM:
        yield word + " "
        time.sleep(0.1)


st.write_stream(stream_data)