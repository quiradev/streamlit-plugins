import os
from io import open
from pathlib import Path

from setuptools import setup, find_packages

with open(os.path.join(Path(__file__).parent / 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Se leen los requirements de requirements.txt
with open(os.path.join(Path(__file__).parent, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()
#

main_folder = Path(__file__).parents[4]
os.chdir(main_folder)

with open(main_folder / "VERSION", "r") as reader:
    VERSION = reader.read().strip()

MINOR_VERSION = ".".join(VERSION.split(".")[0:-1] + ["0"])

setup(
    name='streamlit-framework-multilit',
    version=VERSION,
    license='MIT',
    url='https://github.com/quiradev/streamlit-plugins',
    description='Components and Frameworks to give new features to streamlit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='v.quilonr@gmail.com',
    author='Victor Quilon Ranera',
    packages=find_packages(include=["streamlit_plugins.framework.multilit", "streamlit_plugins.components.multilit.*"]),
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require={
        "navbar": [f"streamlit-component-navbar~={MINOR_VERSION}"],
        "loader": [f"streamlit-component-loader~={MINOR_VERSION}"],
    },
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords=["streamlit", "plugins", "framework", "multipage", "multilit"],
    options={
        'sdist': {'dist_dir': './dist/streamlit-plugins-framework-multilit'},
        'bdist_wheel': {'dist_dir': './dist/streamlit-plugins-framework-multilit'},
        'build': {'build_base': './build/streamlit-plugins-framework-multilit'}
    }
)
