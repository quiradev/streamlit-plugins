import traceback

import streamlit as st

from cognitionlit.plugins.multilit.app_template import MultiHeadApp
from cognitionlit.plugins.components.Loader.loader import LoadersLib, Loader


class LoadingApp(MultiHeadApp):
    def run(self, app_target):
        try:
            app_title = ""
            if hasattr(app_target, "title"):
                app_title = app_target.title

            with Loader(loader_name=LoadersLib.book_loader):
                app_target.run()

        except Exception as e:
            # st.image("./resources/failure.png", width=100, )
            st.error(f"Error details: {e}")
            traceback.print_exc()
