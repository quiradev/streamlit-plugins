import os
import sys
from pathlib import Path

from streamlit.web import bootstrap
from streamlit import config as _config

if __name__ == '__main__':
    # Se agregan los componentes y modulos nuevos
    example_dir = Path(__file__).resolve().parent
    sys.path.append(str(example_dir.parents[3]))
    real_script = str(example_dir / "app.py")
    os.environ['RELEASE'] = 'DEV'
    _config.set_option("browser.gatherUsageStats", False)
    _config.set_option("server.headless", True)
    # _config.set_option("server.port", 8502)
    args = []

    bootstrap.run(real_script, False, args, flag_options={})
