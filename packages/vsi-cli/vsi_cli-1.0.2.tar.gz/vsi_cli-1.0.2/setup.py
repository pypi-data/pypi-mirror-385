from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vsi-cli",
    version="1.0.2",
    author="ermiasgirmai",
    author_email="c-ermias.girmai@charter.com",
    description="vsi cli <--> aws cli wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.spectrumflow.net/C-Ermias.Girmai/vsi-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "vsi=vsi.main:app",
        ],
    },
)