from pathlib import Path

dev_url = "http://localhost:3000"

# _RELEASE = os.getenv("RELEASE", "").upper() != "DEV"
_RELEASE = True
# _RELEASE = False
absolute_path = Path(__file__).parent
build_path = absolute_path / "frontend" / "build"
