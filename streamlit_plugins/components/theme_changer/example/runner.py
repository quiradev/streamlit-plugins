import os.path
from pathlib import Path
import sys


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
    _config.set_option("client.allowedOrigins", "http://localhost")
    # _config.set_option("server.port", 8502)
    args = []

    bootstrap.run(str(real_script), False, args, flag_options={})
