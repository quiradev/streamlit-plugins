from pathlib import Path

import streamlit
from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")

# _DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")
# class CustomHostConfigHandler(HostConfigHandler):
#     async def get(self) -> None:
#         self.write(
#             {
#                 "allowedOrigins": _DEFAULT_+ALLOWED_MESSAGE_ORIGINS.copy(),
#                 "useExternalAuthToken": False,
#                 # Default host configuration settings.
#                 "enableCustomParentMessages": True,
#                 "enforceDownloadInNewTab": False,
#             }
#         )
#         self.set_status(200)
#
# streamlit.web.server.routes.HostConfigHandler = CustomHostConfigHandler

if __name__ == '__main__':
    from streamlit.web import bootstrap
    import streamlit.config as _config

    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.headless", True)
    # _config.set_option("theme.base", "light")

    bootstrap.run(str(Path(__file__).parent / "app.py"), False, [], flag_options={})
