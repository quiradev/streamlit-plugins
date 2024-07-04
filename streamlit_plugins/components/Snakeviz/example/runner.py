import os.path
import sys

from streamlit.web import bootstrap
from streamlit import config as _config

if __name__ == '__main__':
    # Se agregan los componentes y modulos nuevos
    sys.path.append(os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )))
    real_script = "app.py"
    os.environ['RELEASE'] = 'DEV'
    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.port", 8502)
    args = []

    bootstrap.run(real_script, '', args, flag_options={})
