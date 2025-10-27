import logging
import traceback
from typing import Callable, Tuple, Optional

from streamlit.runtime.scriptrunner import StopException

from streamlit_plugins.components.loader import LoadersLib, DefaultLoader, LoaderType

logger = logging.getLogger(__name__)


class LoadingWithStatement:
    def __init__(
        self, loading_engine: "LoadingEngine",
        **run_loader_kwargs
    ):
        self.loading_engine = loading_engine
        self.run_loader_kwargs = run_loader_kwargs
    
    def __enter__(self):
        try:
            self.loading_engine.loader.run_loader(
                **self.run_loader_kwargs
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
    default_loader_lib: LoadersLib = LoadersLib.book_loader

    def __init__(self, loader: LoaderType, loader_kwargs: dict = None):
        if loader_kwargs is not None:
            loader = loader.recreate_loader_with(**loader_kwargs)
        self.loader = loader

    @classmethod
    def get_default_loader(cls, loader_container, loader_params: dict = None, loader_lib: LoadersLib | Callable[..., Tuple[str, str ,str], ] = None) -> DefaultLoader:
        loader_lib = loader_lib or cls.default_loader_lib
        return DefaultLoader(
            loader_container=loader_container,
            **loader_params,
            loader_lib=loader_lib
        )

    def loading(self, **run_loader_kwargs):
        return LoadingWithStatement(
            self,
            # Any argument that can be changed dinamically
            **run_loader_kwargs
            # label=label, height=height,
            # primary_color=primary_color,
            # background_color=background_color
        )