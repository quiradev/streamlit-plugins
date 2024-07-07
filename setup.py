import os
from io import open
from pathlib import Path

from setuptools import setup, find_packages

with open(os.path.join(Path(__file__).parent / 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Se leen los requirements de requirements.txt
with open(os.path.join(Path(__file__).parent, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()


setup(
    name='streamlit-plugins',
    version='0.2.1',
    license='MIT',
    url='https://github.com/quiradev/streamlit-plugins',
    description='Components and Frameworks to give new features to streamlit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='v.quilonr@gmail.com',
    author='Victor Quilon Ranera',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        *requirements,
    ],
    include_package_data=True,
    package_data={
      "streamlit_plugins": ["components/*/frontend/build/**/*"]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords=["streamlit", "plugins", "framework", "components", "navbar", "loader", "multilit"],
    options={
        'sdist': {'dist_dir': './dist/streamlit-plugins'},
        'bdist_wheel': {'dist_dir': './dist/streamlit-plugins'},
        'build': {'build_base': './build/streamlit-plugins'}
    }
)
