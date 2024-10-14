import streamlit as st
from streamlit_plugins.framework.multilit import MultiApp, MultiHeadApp


def run():
    with st.sidebar:
        position_mode = st.radio(
            "Navbar position mode",
            ["top", "under"],
            index=0 if st.session_state.get("position_mode", "top") == "top" else 1,
        )
        sticky_nav = st.checkbox(
            "Sticky navbar", value=st.session_state.get("sticky_nav", True)
        )
        within_fragment = st.checkbox(
            "Use within fragment", value=st.session_state.get("within_fragment", False)
        )
        st.divider()
        st.session_state["position_mode"] = position_mode
        st.session_state["sticky_nav"] = sticky_nav
        st.session_state["within_fragment"] = within_fragment
    # sticky_nav = False
    # position_mode = "top"
    # within_fragment = False
    multi_app = MultiApp(
        title="Demo", nav_horizontal=True, layout='wide', favicon="📚",
        use_navbar=True, navbar_sticky=sticky_nav, navbar_mode=position_mode,
        use_cookie_cache=True, sidebar_state='auto',
        navbar_animation=True, allow_url_nav=False, hide_streamlit_markers=False, use_banner_images=None,
        banner_spacing=None, clear_cross_app_sessions=True, session_params=None,
        use_loader=True, within_fragment=within_fragment
    )

    class Demo1App(MultiHeadApp):
        def run(self):
            with st.sidebar:
                st.write("This is a sidebar defined on App")

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
                    time.sleep(0.01)

            st.write_stream(stream_data)

            st.markdown("\n\n".join(_LOREM_IPSUM))

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

    @multi_app.addapp(title="Home", app_type="home")
    def my_home():
        st.info('HOME')
        if st.button('Demo1', key="change-app_demo1"):
            multi_app.change_app(demo1_app.get_id())
        if st.button('Demo2', key="change-app_demo2"):
            multi_app.change_app(demo2_app.get_id())

    multi_app.add_app(title="Demo1", app=demo1_app, icon=None)
    multi_app.add_app(title="Demo2", app=demo2_app, icon=None)

    multi_app.get_nav_transition()

    # st.logo(
    #     image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaoAAAB2CAMAAACu2ickAAABC1BMVEX///8mJzD/S0u9QEN9NTsAABYLDRzT09QDBxgHChofICoAAAsAABP5+fm5ubsAABAZGiUVFiLNzc/Dw8UAAACnp6rk5OWFhYkdHimWl5o9PUXg4eFmZmtZWV7/Ozvt7e7/QUF0dXk0NT3/Pz+Li47/Nja5LDB5KzL/Tk6srK//ysp8fYFFRk1yFyFPUFYqKzT/4+O/SEtqa2//cHDeqar/hYX/kZH/q6v/trb/ZWX/1NT/e3v/8PD6U1P/3t7NdnjWkpPmvr67NjrEWVulfH//oaGuioxvDBjJamyKTVHApKbJsrSCPUPhsLHXxcfi1tePV1uecHPbXF6pR0uQQ0fqU1Sshonahof/paUVYasIAAAMNElEQVR4nO2ce3vaOBaHgcTG9wtgsAPE4JBSCoFM0nZ6STOzve1O253Opbvb7/9J1pJ8kWzZOIlJyvOc9y+whWzp53N0dCTTaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPxo6A99Az86w67/0LdA+OXRrzXXOOw6IUb7B2ngHfFXqqROH/ouEE8fHTz6R33V6c5YFGTRtkVRENZOv76a7xFrs9lY7ejLkdVsNqXBg94Q5urRwcHB26uaatNnsqg0ExRbvdhH09LCNmiRVB0TN8V6+GHi3Vsk1b/qqcyw7WYGS3Pqqfs+kcIbFyKpuhJuh/ngj9xTZFQHNbnAmRoZk2WLsmhF5qWxfr59MQ2p43K7g5bK13CTVslJ3ICLe7+nK6JUPS5wRholmiPPMbrO4MgkNiYzwnRV17Xsu19tl9BSNZyepdi9YXKygxqg3vs9vTuIpbq7CzR6SBc7MBKvrjuKhe2K9oFdGel556vtFEaqRns5nlHur4POyjVe7dnzCnbyNDaqai7Qf/9n8Ukdm5C2ZA9OkTBNgWrp/kmVoW6prk8npx+2BS3nqVKhVtuk9T+ezf9ZPLh6SCrJyx5eosMWFeqCVFket1qTyc/lZd5RSm1zgfqns/nh4W/FBTZIgXH++BGKLqixCaTK8n3SarVOWi9Kivz6lpbq4NG/S8p+modCHc4/FxYYmgXNw9JobfY7SEVxddpCHD9+UlSCcX/lLvDzIRIqlKrYpRpi2ICAd6Zn23ZvkXzdKpXuP/gUplSqNjor1nm515MWEetNgVg/ZZQqdIGfvxChDufviy/nhGOSsuae8UI66FPbcZzFAAeFCwcTiYI/40+dZeCG0jJidbyLoyBYT51ho4CON10FQbBa5ooMUc1d/LE9WwfB0cih6vaNQfi7FXMMwUjVT+8ONcDBDXDZBtyNJ8etiOOXrzjnM+6v0AX+/tvZYcTZ1+LLoaiCmifyy6ihClippo3pke7QQ8MTtdBi2ysTnxbTHtBnlmC7SlNRXNsMeJkPfybiEnjqbW4WzEkjrBrPwTvhLE8Jq3Ht3jLyDf6yF87TybEp0+eMVB10dz380enxG3BXWinHl9fZszn3x3eBX/9IhDo8/FJytQVygG55zOlk004CMQIdZTms8LwaJThSq1owqSpF3HSylXoCW6sc0Cli5JfdKXpK0tSk3cQluiL1Q8umO52VSkjGJtxIpgH1SPVhkmo1OX19zp7NuT+eCwyFmqdKlQQVcYOM0jtysi3VGKm6vaQzY6lGWixS1NNKjzUsfS1HJ1wrymQpKtV/kVSOylTihvUveuRQfMykFGakaqdhRE4qrR6posAiFuv4GW0yHPeXc4H9P2mhQv9XZjO6gO+91Kw8zYr708L0KKkUH8/AJFPtqb1IqjF+7l1Rba5Xtkly9iajVWARa1OD6XK5NmXsBynjxlItUR7PVjfrlSrhOqxxox1e0xKkYLwyyTHaexdKZYY37dINqEeqxmWLYXKaJjCuee6PdYH+e1ao0qAiZIo6TTnaOs52sBkwh7BUm3C4tt1ZJ6zAb5O+HmGlhFEXf/UXAf7eo3zgmAxtqziZ1cXSWWnSkVjV1FVsD99ZZ40NQzBWSlOYko6OjmmpSyhygJj6I0A6sIjFOokTGFz3h13gO1JA/5gRqjyoCOmbxLeU+0BusI6larpNbcYY5QJ5P8Xqpkdm5BpJKQP7R5VOkazRQ99LHhg8h3BdN32EZliX0ELlVPIlOkbFr6VS1T6vQrRyRAmMAveHzeppI05NZCgLKhAOWYOTAqfUCxZK1TTZ4A07RCVgzBSrZyfSaMiGzG7uV2kJLFVo7FSJEfFgAh2grJEPVJP7vn+pnk/yYqEExtci9xe5QJKayDD/tO1yA6KVImpjp9iHF0plz9iCM9zpGYdKUopxn3aWtqx5+Z+lBkKk0uigkCxAuczKTBvJISXi3b9U56d5qdCc+K8SpQ4O3n3hCHV4WJKpjVnEEbFia8powZ+xFltVpiASXsq6Ux2ZBBVo6t3sKiUeSpK6sFQWm+4fK/nYDZmnmFh1UViB2YlUjZc8qULe/FU4WIXD1d88peYl6x8J/bGZTF9c0WzOinKCHKnsjHWgTubMqdFU2y1bg/WRxMkcGkuVmf0skS6Zxc2RQt/B/VtV48VJgVatUsv6xpHq7PdKV+yuVSudbFraapErUSCVlJncoiFFzMcoQy3fzywq7fEMzszc4+TAULbISjzwA0ilcwarRKxiw/rpC0erqtfszwLTTtRSZCvT3UVSCew+NB1VYXICFCFflgFblRY7X2ybR2wJLFVmuQZLlayq5R0gFZzvRipuYJHwn0Kx8i5w/vEGVx06Y1OyYrVMdjSpKBWyHm5OEa1/ZS2Q/h0ZifZPquvs1KqiWDkXeHbDFLLeHWy0KMdmr2jjqCgV7uOR38/iIynEnFtF82bDGVy4AjboPZSqMLCIeFwgVtYFzv+4xbWHXhDlceiBoaJUOF+omHnwojKTXPI7znQlqoJoR0mf/ZSqOLAoFyvjAisGFTkMkguSqeiuolRebvMnBR0tGmNRImsg0ei4r1Lp5R6wWCzWBc5vfQMDPM0RUhdYh1Rpp3YDyU2PK66o7utY1Wg8KwssSsRiXOCNgooMOOcmph7rJlIpIh81ntPOokm34tqiIAgBWilW91WqLYFFLFZ+Tky7wC2Z2nJQyEZNY6qOVXjyYxQQdaNHUlm2uZp6xjCKfPZWqsabKlLxEhiUC7xNUJGA1+NSbW4UAZbX3Merg5boMT/dX6m2BhapWEUusHT5dys4FZpmrStKhTuEuwMqhWSIRpl58v5KpXNztnyxWMNKXGDp8m90FQT/VB+lgtJ3XipK5bMCc8GjVG6X1P5KVSmwiGHji8gFzv+7/SJjAe3f4Z7CTbuxVTUC1CHdRglYTTmbuNjXxBLiVaXAIoIJBiMXWCWowItLGnfZg4TdydeqUiHvVppCJ+vOOcMju3l3LVXNC/YxFQMLjljEBZZsVE/AHWTNeKfwzpRRpiRTgitVR+McDMt6yfOAPWvuRacL9z6k0vLtrIOfqwYWebG+VQ0qyIYlkZMpxPZGJe3IU8/+mCdVYxNq7OZiQE81lSlJ1vsotNQyPxviG9m5VFtG0dtyVT2wyIqFXGCFoKIRRWNKkCvrZbMVZG2cWezjS4X3uMgZQ+0joe0oMkQvn2RXJIOdJ5bwillJbv9OvL5BYJER6+9te8pi8BjfVDbsgqt/QayN6k887LMzJr5UZG+KwPwLQR+vW8YbX/DjIdK/01ckzbRLqXQ82HJeT6qD3C6zKkRz4m9VMxUOeRNYG6VR23BANni7TF+tUG+LU9TDkb8skKpPdsccpQ+wg9cs3bib2nirp5tecKG4TXvXUpG9GfYF1YAaeXwLqWKxqgQVGPIuadOV5NHMc5zZyBbI8qKiMC0ycDbIFQRXiKL7AqkaXbJ9WdgMjE6ns5iKZKeYlVQ3whcQVl5n2G93Z0p4XlrYu5aK3FbYAEXgT0/uwvfbmBURq/QFOZYpycjhNzJC4nUJe5N59kZJ0jyKCYqkahi9aNu0KEuySHybIqVTAp8seSi2rGmCjHMX451PgcMgM21A4XtEt+by+ObDFWLS+t8NrmJI+ZULxZzmQo1VvEs/2uZSKFWj3cxu6JePmD19G4s9O959tiJknTSAsxx9V15cPp6cHh+fnEwmW0ULi0xOjo+PTydvLsteUM2jz0T6f3vQH/eMeZs3B9G2JpssZug913VV7tYW3bOpGl3JzbxhpV+oqVg23r6JKkv+ZsIwXdfKpBI9yXXtrFSi64rJdkEV3U+yYwl9M9niM5U4DXtH/5Vydf7qyYsPz59dvmxNTpAWOZCSb16+fv7h+4snr85vM3XQFyPyb1i2KGvSyivYWtSfBbIkyU0SGerj0Wg0Lhii9cVYFCQR/buWdcHZED9cioIo2qKouQNcBa4svm4Hfcv05yI8NMr8vZWDjiWPAa4iVnuIv2Wu6pMGKNxJf83oV1fn59fXryKur6/Pz6+uapnY9bvo7ctFd1ham+77la827KA1qsJwa2iElzPqHzbKCRvw4C8tAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD8g/wcxNCqxaHkv7gAAAABJRU5ErkJggg==",
    #     icon_image="data:image/png;base64,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"
    # )

    multi_app.run()


if __name__ == '__main__':
    try:
        import sys

        if "_pydevd_frame_eval.pydevd_frame_eval_cython_wrapper" not in sys.modules:
            import _pydevd_frame_eval.pydevd_frame_eval_cython_wrapper
    except ImportError:
        pass

    run()

