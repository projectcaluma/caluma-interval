"""Setuptools package definition."""

from setuptools import find_packages, setup

setup(
    name="caluma_interval",
    version="0.0.0",
    description="Caluma companion app for periodic usage of forms",
    url="https://projectcaluma.github.io/",
    license="MIT",
    packages=find_packages(),
)
