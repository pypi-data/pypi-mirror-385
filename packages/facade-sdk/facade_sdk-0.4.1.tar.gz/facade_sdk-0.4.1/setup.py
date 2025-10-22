from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_discription = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="facade-sdk",
    version="0.4.1",
    packages=find_packages(),
    author="Data Team FALL 2025",
    url="https://github.com/mseavers1/facade_sdk",
    install_requires=["paho-mqtt>=1.6.1",],
    description="SDK for FACADE system API",
    long_description=long_discription,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)