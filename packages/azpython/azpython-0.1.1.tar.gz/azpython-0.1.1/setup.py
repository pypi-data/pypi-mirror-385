from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='azpython',
    version='0.1.1',
    description='Python3 AZ.COM HTTP API Connector',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/selinayiya/api-python-demo",
    download_url='https://github.com/selinayiya/api-python-demo/archive/refs/tags/V0.1.1.tar.gz',
    license="MIT License",
    author="az",
    author_email="az@az.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="az api connector",
    packages=["azpython", "azpython.websocket"],
    python_requires=">=3.9",
    install_requires=[
        "requests",
        "websockets"
    ]
)
