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
    name='streamlit-component-snakeviz',
    version='0.2.0',
    license='MIT',
    url='https://github.com/quiradev/streamlit-plugins',
    description='Snakeviz Component to analyze ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='v.quilonr@gmail.com',
    author='Victor Quilon Ranera',
    packages=find_packages(include=["streamlit_plugins.components.snakeviz", "streamlit_plugins.components.snakeviz.*"]),
    python_requires='>=3.9',
    install_requires=requirements,
    include_package_data=True,
    package_data={
          "streamlit_plugins.components.snakeviz": ["frontend/build/**/*"]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords=["streamlit", "plugins", "components", "snakeviz"],
    options={
        'sdist': {'dist_dir': './dist/streamlit-plugins-component-snakeviz'},
        'bdist_wheel': {'dist_dir': './dist/streamlit-plugins-component-snakeviz'},
        'build': {'build_base': './build/streamlit-plugins-component-snakeviz'}
    }
)
