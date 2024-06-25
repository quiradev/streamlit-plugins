from pathlib import Path


if __name__ == '__main__':
    from streamlit.web import bootstrap

    bootstrap.run(str(Path(__file__).parent / "multi_page.py"), False, [], flag_options={})
