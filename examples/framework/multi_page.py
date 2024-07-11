import streamlit as st
from streamlit_plugins.framework.multilit import MultiApp, MultiHeadApp

def run():
    multi_app = MultiApp(
        title="Demo", nav_container=None, nav_horizontal=True, layout='wide', favicon="📚",
        use_navbar=True, navbar_sticky=True, navbar_mode="pinned",
        use_cookie_cache=True, sidebar_state='auto',
        navbar_animation=True, allow_url_nav=True, hide_streamlit_markers=False, use_banner_images=None,
        banner_spacing=None, clear_cross_app_sessions=True, session_params=None,
        use_loader=False, within_fragment=False
    )

    class Demo1App(MultiHeadApp):
        def run(self):
            with st.sidebar:
                st.write("This is a sidebar")

            st.title("Demo 1")
            _LOREM_IPSUM = [
                "Lorem", "ipsum", "dolor", "sit", "amet,", "consectetur",
                "adipiscing", "elit.", "Sed", "nec", "urna", "felis.",
                "Cras", "eleifend", "for ", "dolor", "at", "congue.",
                "Maecenas", "vel", "nunc", "sit", "amet", "libero", "suscipit",
                "ultrices."
            ]

            import time

            def stream_data():
                for word in _LOREM_IPSUM:
                    yield word + " "
                    time.sleep(0.1)

            st.write_stream(stream_data)

    class Demo2App(MultiHeadApp):
        def run(self):
            with st.sidebar:
                st.write("This is a sidebar")

            with st.container(height=400):
                with st.chat_message("ai"):
                    st.write("This is a chat message")

                with st.chat_message("user"):
                    st.write("Hi!")

            with st._bottom:
                st.chat_input(placeholder="Type a message...")

    demo1_app = Demo1App()
    demo2_app = Demo2App(with_loader=False)

    @multi_app.addapp(title="Home", is_home=True)
    def my_home():
        st.info('HOME')
        if st.button('Demo1'):
            multi_app.change_app(demo1_app.get_id())
        if st.button('Demo2'):
            multi_app.change_app(demo2_app.get_id())

    multi_app.add_app(title="Demo1", app=demo1_app, icon=None)
    multi_app.add_app(title="Demo2", app=demo2_app, icon=None)

    multi_app.get_nav_transition()

    multi_app.run()


if __name__ == '__main__':
    try:
        import sys

        if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
            import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
    except ImportError:
        pass

    run()

