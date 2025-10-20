import traceback

from streamlit.runtime.scriptrunner import StopException

from streamlit_plugins.components.loader import BaseLoader, LoadersLib, DefaultLoader

class LoadingWithStatement:
    def __init__(self, loading_engine: "LoadingEngine", status_msg: str = "") -> None:
        self.loading_engine = loading_engine
        self.status_msg = status_msg
    
    def __enter__(self):
        try:
            self.loading_engine.loader.run_loader()
        # except RerunException as e:
        #     st.rerun()
        except StopException as e:
            ...
        except Exception as e:
            ...
            # st.error(f"Error details: {e}")
            traceback.print_exc()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loading_engine.loader.stop_loader()


class LoadingEngine:
    default_loader: LoadersLib = LoadersLib.book_loader

    def __init__(self, loader: BaseLoader):
        self.loader = loader

    @classmethod
    def get_default_loader(cls, loader_container, loader_name: LoadersLib = None):
        loader_name = loader_name or cls.default_loader
        return DefaultLoader(loader_container=loader_container, loader_name=loader_name)

    def loading(self, status_msg=""):
        return LoadingWithStatement(self, status_msg=status_msg)