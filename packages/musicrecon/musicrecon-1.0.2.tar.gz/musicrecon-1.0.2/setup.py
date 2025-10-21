import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "CLI toolkit for searching, recognizing and downloading music."
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db"]


setup(
    name="musicrecon",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/MusicRecon/",
    entry_points={
        "console_scripts": [
            "musicrecon=musicrecon:main",
            "mrecon=musicrecon:main",
        ],
    },
    python_requires=">=3.12",
    install_requires=[
        "setuptools",
        "wheel",
        "argparse",
        "yt_dlp",
    ],
    include_package_data=True,
    package_data={
        # "soundscan": ["cli.py"],
    },
    # include_dirs=[...],
    zip_safe=False,
    license="GNU v3",
    keywords=["soundscan", "shazam", "music_downloader"],
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
