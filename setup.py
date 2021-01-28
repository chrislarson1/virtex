from io import open
from setuptools import setup, find_packages

setup(
    name="virtex",
    version="0.1",
    author="Chris Larson",
    author_email="chris7larson@gmail.com",
    description="Serving for computational workloads",
    long_description=open("README.md", "r", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    keywords='machine deep learning ai serving asyncronous microservice',
    license='Apache Version 2.0',
    url="https://github.com/chrislarson1/virtex.git",
    packages=find_packages(exclude=["*.data", "*.data.*", "data.*", "data"]),
    classifiers=[
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ]
)
