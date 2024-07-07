import traceback

import streamlit as st

from streamlit_plugins.framework.multilit.app_template import MultiHeadApp
from streamlit_plugins.components.loader import LoadersLib, Loader


class LoadingApp(MultiHeadApp):
    def __init__(self, *args, loader_container=None, app_container=None, **kwargs):
        super().__init__(*args,  **kwargs)
        self.loader_container = loader_container
        self.app_container = app_container

    def run(self, app_target: MultiHeadApp, status_msg=""):
        try:
            if not status_msg:
                if hasattr(app_target, "title"):
                    status_msg = app_target.title

            loader = Loader(loader_container=self.loader_container, text=status_msg, loader_name=LoadersLib.book_loader)
            loader.run_loader()
            with self.app_container:
                app_target.run()
            loader.stop_loader()

        except Exception as e:
            st.error(f"Error details: {e}")
            traceback.print_exc()
