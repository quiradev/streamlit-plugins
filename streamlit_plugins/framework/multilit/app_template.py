import base64
import json
import pickle
import re
import uuid
from abc import ABC, abstractmethod

import compress_pickle as cp
import pandas as pd
import streamlit as st
import validators
from bokeh.models.widgets import Div


class MultiHeadApp(ABC):
    """
    This is a template class that streamlit applications can inherit from that automatically structures them for use in a Multilit application.

    A number of convenience methods are also included within the template.

    """

    def __init__(self, with_loader=None):
        self._id = None
        self.access_level = None
        self.with_loader = with_loader
        self.session_state = None
        self.parent_app = None

    def get_id(self):
        return self._id

    def has_loading(self):
        if self.with_loader is None:
            return True

        return self.with_loader

    # Must implement this method as the entry point for the application.
    @abstractmethod
    def run(self, *args, **kwargs):
        ...

    def assign_session(self, session_state, parent_app):
        """
        This method is called when the app is added to a Multilit application to gain access to the global session state.

        Parameters
        ------------
        session_state:
            The session state as created by the parent application.

        """

        self.session_state = session_state
        self.parent_app = parent_app

    def check_access(self, actual_level: int) -> bool:
        """
        Check the access permission and the assigned user for the running session.
        """
        if self.access_level is None:
            return True

        return self.access_level >= actual_level

    def do_redirect(self, redirect_target_app=None):
        """
        Used to redirect to another app within the parent application. If the redirect_target is a valid url, a new window will open and the browser will set focus on the new window while leaving this app in it's current state.

        Parameters
        ------------
        redirect_target_app: str, None
            The name of the target app or a valid url, this must be the registered name when the app was added to the parent. If no target is provided, it will redirect to the MultiApp home app. If the redirect_target is a valid url, a new window will open and the browser will set focus on the new window while leaving this app in it's current state.

        """

        self._sneaky_redirect(redirect_target_app=redirect_target_app)

    def _sneaky_redirect(self, redirect_target_app=None):

        if redirect_target_app is not None and validators.url(redirect_target_app):
            js = "window.open('{}')".format(redirect_target_app)
            html = '<img src onerror="{}">'.format(js)
            div = Div(text=html)
            st.bokeh_chart(div)
        else:
            self.session_state.other_nav_app = redirect_target_app
            st.rerun()

    def download_button(self, object_to_download, download_filename, button_text, use_compression=False,
                        parent_container=None, pickle_it=False, css_formatting=None, **kwargs):
        """
        A convenience method to include a dataframe download button within this application.

        Parameters
        ------------
        object_to_download: Pickle, DataFrame
            This is the data object that will be available to download as either a csv if the object is a Pandas DataFrame or as a JSON text file if is a pickle file.
        download_filename: str
            The default name of the download file.
        button_text: str
            The text to display on the download button
        use_compression: bool, False
            Compress the object using bz2 compression before encoding into link.
        parent_container: Streamlit.container
            The parent container in which to create the button.
        pickle_it: bool, False
            Flag to indicate if the download data should be pickled.
        css_formatting: Dict, None
            A css formatting string to be applied to the download button. The format dict must have a value of the css string and a key value of the css selection tag value, e.g. mybutton
        kwargs:
            Keyword arguments to be passed to either the json.dump or Pandas.to_csv method used for the data export.

        """

        if pickle_it:
            try:
                object_to_download = pickle.dumps(object_to_download)
            except pickle.PicklingError as e:
                st.write(e)
                return None

        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(**kwargs)

        else:
            object_to_download = json.dumps(object_to_download, **kwargs)

        try:
            if use_compression:
                b64 = base64.b64encode(cp.dumps(object_to_download.encode(), compression="gzip")).decode()
            else:
                b64 = base64.b64encode(object_to_download.encode()).decode()

        except AttributeError as e:
            if use_compression:
                b64 = base64.b64encode(cp.dumps(object_to_download, compression="gzip")).decode()
            else:
                b64 = base64.b64encode(object_to_download).decode()

        button_uuid = str(uuid.uuid4()).replace('-', '')
        button_id = re.sub('\d+', '', button_uuid)

        pc = st.get_option('theme.primaryColor')
        bc = st.get_option('theme.backgroundColor')
        sbc = st.get_option('theme.secondaryBackgroundColor')
        tc = st.get_option('theme.textColor')

        if css_formatting is None:
            css_styling = f""" 
                <style>
                    #mybutton {{
                        background-color:{sbc};
                        color: rgb(38, 39, 48);
                        padding: 0.25em 0.38em;
                        position: relative;
                        text-decoration: none;
                        border-radius: 4px;
                        border-width: 1px;
                        border-style: solid;
                        border-color: rgb(243, 135, 13);
                        border-image: initial;

                    }} 
                    #mybutton:hover {{
                        border-color:{bc};
                        background-color:{pc};
                        color:{bc};
                    }}
                    #mybutton:active {{
                        background-color:{bc};
                        color:{pc};
                        }}
                </style> """
        else:
            tag_name = next(iter(css_formatting.keys()))
            css_styling = next(iter(css_formatting.values()))
            css_styling = css_styling.replace(tag_name, button_id)

        dl_link = css_styling + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

        if parent_container is None:
            st.markdown(dl_link, unsafe_allow_html=True)
        else:
            parent_container.markdown(dl_link, unsafe_allow_html=True)

        return dl_link
