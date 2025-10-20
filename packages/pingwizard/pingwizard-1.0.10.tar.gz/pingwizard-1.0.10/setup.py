
from setuptools import setup, find_packages
from pathlib import Path

DESCRIPTION = 'Light-weight interface for running PING ecosystem (PINGMapper, etc.)'
LONG_DESCRIPTION = Path('README.md').read_text()

exec(open('pingwizard/version.py').read())

setup(
    name="pingwizard",
    version=__version__,
    author="Cameron Bodine",
    author_email="bodine.cs@gmail.email",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    data_files=[("pingmapper_config", ["pingwizard/assets/PINGMapper_Logo_small.png"])],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Oceanography",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Hydrology"
        ],
    keywords=[
        "pingmapper",
        "sonar",
        "ecology",
        "remotesensing",
        "sidescan",
        "sidescan-sonar",
        "aquatic",
        "humminbird",
        "lowrance",
        "gis",
        "oceanography",
        "limnology",],
    python_requires=">=3.6",
    install_requires=[],
    project_urls={
        "Issues": "https://github.com/CameronBodine/PINGWizard/issues",
        "GitHub":"https://github.com/CameronBodine/PINGWizard",
        "Homepage":"https://cameronbodine.github.io/PINGMapper/",
    },
)