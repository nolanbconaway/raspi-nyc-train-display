"""Setup."""

from setuptools import find_packages, setup

INSTALL_REQUIRES = [
    "underground>=0.3.0",
    "click>=7.0",
    "sqlitedict>=1.6",
    "pygame>=1.9",
    "supervisor>=4.0",
    "pytz>=2019.3",
]

DEV_REQUIRES = [
    "pytest>=5.0",
    "tox>=3.13",
    "black>=19.10b0",
]

setup(
    name="traindisplay",
    version="0.2.0",
    author="Nolan Conaway",
    author_email="nolanbconaway@gmail.com",
    packages=["traindisplay"],
    install_requires=INSTALL_REQUIRES,
    extras_require=dict(dev=DEV_REQUIRES),
)
