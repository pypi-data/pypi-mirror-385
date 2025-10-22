from setuptools import setup, find_packages

setup(
    name="2048-river",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": ["2048-river=main_launcher.main:main"],
    },
)
