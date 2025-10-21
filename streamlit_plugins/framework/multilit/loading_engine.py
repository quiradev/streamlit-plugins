import logging
import traceback
from typing import Callable, Tuple, Optional

from streamlit.runtime.scriptrunner import StopException

from streamlit_plugins.components.loader import LoadersLib, DefaultLoader, LoaderType

logger = logging.getLogger(__name__)


class LoadingWithStatement:
    def __init__(self, loading_engine: "LoadingEngine", label: Optional[str] = None, height: Optional[str | int] = None, primary_color: str = None, background_color: str = None):
        self.loading_engine = loading_engine
        self.label = label
        self.height = height
        self.primary_color = primary_color
        self.background_color = background_color
    
    def __enter__(self):
        try:
            self.loading_engine.loader.run_loader(
                label=self.label,
                height=self.height,
                primary_color=self.primary_color,
                background_color=self.background_color
            )
        # except RerunException as e:
        #     st.rerun()
        except StopException as e:
            ...
        except Exception as e:
            # st.error(f"Error details: {e}")
            logger.error(traceback.format_exc())
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loading_engine.loader.stop_loader()


class LoadingEngine:
    default_loader: LoadersLib = LoadersLib.book_loader

    def __init__(self, loader: LoaderType):
        self.loader = loader

    @classmethod
    def get_default_loader(cls, loader_container, loader_lib: LoadersLib | Callable[..., Tuple[str, str ,str], ] = None):
        loader_lib = loader_lib or cls.default_loader
        return DefaultLoader(loader_container=loader_container, loader_lib=loader_lib)

    def loading(self, label: Optional[str] = None, height: Optional[str | int] = None, primary_color: str = None, background_color: str = None):
        return LoadingWithStatement(
            self,
            label=label, height=height,
            primary_color=primary_color,
            background_color=background_color
        )