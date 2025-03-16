import os.path
from pathlib import Path
import sys

import streamlit
from streamlit.web.server.routes import _DEFAULT_ALLOWED_MESSAGE_ORIGINS
streamlit.web.server.routes._DEFAULT_ALLOWED_MESSAGE_ORIGINS.append("http://localhost:8501")


from streamlit.web import bootstrap
from streamlit import config as _config

if __name__ == '__main__':
    # Se agregan los componentes y modulos nuevos
    sys.path.append(os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )))
    real_script = Path(__file__).parent / "app.py"
    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.headless", True)
    # _config.set_option("server.port", 8502)
    args = []

    bootstrap.run(str(real_script), False, args, flag_options={})
