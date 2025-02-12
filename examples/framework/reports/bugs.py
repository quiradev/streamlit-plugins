import time
import streamlit as st
st.title("Bug reports")


progress = st.progress(0)
for i in range(100):
    progress.progress(i)
    time.sleep(0.1)

with st._bottom:
    st.chat_input("Type here to chat")