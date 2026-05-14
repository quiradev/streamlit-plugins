import time

import streamlit as st

from streamlit_plugins.components.skeleton import st_skeleton

# EJEMPLOS
button_placeholder = st.container()
placeholder = st.empty()

if button_placeholder.button("Load Skeleton Page"):
    placeholder_container = placeholder.container()
    with placeholder_container:
        with st_skeleton(
                base_style="page"
        ):
            time.sleep(2)
            st.title("Título de la página")
            st.subheader("Lorem ipsum dolor")
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write("""
                Lorem ipsum dolor sit amet consectetur adipiscing elit, faucibus eros dictum molestie neque hac odio vel, morbi sagittis nulla vivamus libero inceptos. Fames posuere cubilia porta pellentesque consequat mauris eget ultricies integer praesent sociis ad vitae suspendisse ornare lectus curae.
                """)
            with col2:
                st.image("https://i.pinimg.com/736x/da/61/2a/da612ad4bd8cbc5c794726e8336585eb.jpg", width="stretch")
                st.caption("Lorem ipsum dolor sit amet")

if button_placeholder.button("Load Skeleton Width/Height"):
    with placeholder.container():
        width = 400
        height = (503 * width) / 526
        skeleton = st.skeleton(width=width, height=height, key="skeleton-image")
        time.sleep(2)
        skeleton.image("https://i.pinimg.com/736x/da/61/2a/da612ad4bd8cbc5c794726e8336585eb.jpg", width=width)
