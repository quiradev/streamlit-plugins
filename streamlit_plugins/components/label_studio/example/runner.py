import os.path
from pathlib import Path
import sys

from streamlit.web import bootstrap
from streamlit import config as _config

if __name__ == '__main__':
    # Se agregan los componentes y modulos nuevos
    sys.path.append(Path(__file__).parents[4])
    real_script = "app.py"
    # os.environ['RELEASE'] = 'DEV'
    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.port", 8502)
    _config.set_option("server.headless", True)
    args = []

    bootstrap.run(str(Path(__file__).parent / real_script), False, args, flag_options={})
