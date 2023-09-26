import os
import streamlit.components.v1 as components


_RELEASE = os.getenv("RELEASE", "").upper() != "DEV"
# _RELEASE = True

if _RELEASE:
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(absolute_path, "frontend", "build")
    _component_func = components.declare_component("st_speech_transcribe", path=build_path)
else:
    _component_func = components.declare_component("st_speech_transcribe", url="http://localhost:3000")


def st_speech_transcribe(*args, **kwargs):
    return _component_func(*args, **kwargs)

