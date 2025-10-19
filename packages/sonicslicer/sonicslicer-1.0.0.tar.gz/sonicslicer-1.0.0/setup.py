import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "CLI toolkit for converting text to audio."
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db"]


setup(
    name="sonicslicer",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/slicer/",
    entry_points={
        "console_scripts": [
            "slicer=sonicslicer:main",
        ],
    },
    python_requires=">=3.12",
    install_requires=["setuptools", "wheel", "argparse"],
    include_package_data=True,
    package_data={
        "audiokit": ["dirname/**", "config.json"],
    },
    # include_dirs=[...],
    zip_safe=False,
    license="GNU v3",
    keywords=["trim audio", "slice files"],
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
