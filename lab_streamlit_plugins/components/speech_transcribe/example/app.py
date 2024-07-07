import streamlit as st

from streamlit_plugins.components.speech_transcribe import st_speech_transcribe

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')


transcription = st_speech_transcribe()
