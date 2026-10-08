import streamlit

import streamlit as st

# from streamlit.runtime.scriptrunner import RerunException, get_script_run_ctx
# from streamlit.proto.WidgetStates_pb2 import WidgetState, WidgetStates


try:
    from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
except ImportError as e:
    _DEFAULT_ALLOWED_MESSAGE_ORIGINS = None


def add_trusted_url(url: str):
    if _DEFAULT_ALLOWED_MESSAGE_ORIGINS is not None:
        if url not in _DEFAULT_ALLOWED_MESSAGE_ORIGINS:
            streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append(url)
    else:
        try:
            allowed_origins = list(st._config.get_option("client.allowedOrigins"))
        except RuntimeError:
            allowed_origins = []

        if url not in allowed_origins:
            allowed_origins.append(url)

        st._config.set_option("client.allowedOrigins", allowed_origins)
