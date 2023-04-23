from setuptools import setup, find_packages
from io import open
import sys, os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='streamlit-plugins',
    version='0.1.0',
    license='MIT',
    url='https://github.com/vquilon/streamlit-plugins',
    description='Components and Frameworks to give new features to streamlit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='v.quilonr@gmail.com',
    author='Victor Quilon Ranera',
    packages=find_packages(),
    # install_requires=[
    #     'pywin32 >= 1.0 ; platform_system=="Windows"',
    #     'pasteboard == 0.3.3 ; platform_system=="Darwin"',
    # ],
    # extras_require=extras,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        # 'License :: OSI Approved :: Apache Software License',
        # 'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    # entry_points={
    #     'console_scripts': ['pyclip = pyclip.cli:main']
    # },
    # tests_require=test_requirements,
    keywords='streamlit plugins framework component'
)
