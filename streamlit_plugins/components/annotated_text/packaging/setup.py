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

setup(
    name='streamlit-component-annotated-text',
    version='0.2.1',
    license='MIT',
    url='https://github.com/quiradev/streamlit-plugins',
    description='Components and Frameworks to give new features to streamlit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='v.quilonr@gmail.com',
    author='Victor Quilon Ranera',
    packages=find_packages(include=["streamlit_plugins.components.annotated_text", "streamlit_plugins.components.annotated_text.*"]),
    python_requires='>=3.9',
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords=["streamlit", "plugins", "components", "loader"],
    options={
        'sdist': {'dist_dir': './dist/streamlit-plugins-component-annotated-text'},
        'bdist_wheel': {'dist_dir': './dist/streamlit-plugins-component-annotated-text'},
        'build': {'build_base': './build/streamlit-plugins-component-annotated-text'}
    }
)
