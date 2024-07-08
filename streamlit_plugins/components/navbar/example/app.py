import sys

try:
    if '_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper' not in sys.modules:
        import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
except ImportError:
    pass

import datetime

import streamlit as st

from streamlit_plugins.components.navbar import st_navbar

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# specify the primary menu definition
menu_data = [
    {'icon': ":material/content_copy:", 'label': "Left End"},
    {'id': 'Copy', 'icon': "🐙", 'label': "Copy"},
    {'icon': ":material/radar:", 'label': "Dropdown1",
     'submenu': [{'id': ' subid11', 'icon': ":material/attach_file:", 'label': "Sub-item 1"},
                 {'id': 'subid12', 'icon': "💀", 'label': "Sub-item 2"},
                 {'id': 'subid13', 'icon': ":material/database:", 'label': "Sub-item 3"}]},
    {'icon': ":material/insert_chart:", 'label': "Chart"},  # no tooltip message
    {'id': ' Crazy return value 💀', 'icon': "💀", 'label': "Calendar"},
    {'icon': ":material/dashboard:", 'label': "Dashboard", 'ttip': "I'm the Dashboard tooltip!"},
    # can add a tooltip message
    {'icon': ":material/send:", 'label': "Right End"},
    {'icon': ":material/radar:", 'label': "Dropdown2",
     'submenu': [{'label': "Sub-item 1", 'icon': ":material/face:"}, {'label': "Sub-item 2"},
                 {'icon': '🙉', 'label': "Sub-item 3", }]},
]


menu_id = st_navbar(
    menu_definition=menu_data,
    home_name='Home',
    login_name='Logout',
    hide_streamlit_markers=False,  # will show the st hamburger as well as the navbar now!
    sticky_nav=True,  # at the top or not
    sticky_mode='pinned',  # jumpy or not-jumpy, but sticky or pinned
)

if st.button('click me'):
    st.info('You clicked at: {}'.format(datetime.datetime.now()))

if st.sidebar.button('click me too'):
    st.info('You clicked at: {}'.format(datetime.datetime.now()))

# get the id of the menu item clicked
st.info(f"{menu_id}")
