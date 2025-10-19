import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "A Python-based DOT language interpreter with multiple API styles"
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db"]


setup(
    name="dotflow-py",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/dotflow-py/",
    entry_points={
        "console_scripts": [
            "dotflow=dotflow.cli.main:cli",
        ],
    },
    python_requires=">=3.12",
    install_requires=[
        "setuptools",
        "wheel",
        "argparse",
    ],
    include_package_data=True,
    package_data={
        "dotflow": ["tests/**"],
    },
    include_dirs=["tests"],
    zip_safe=False,
    license="MIT",
    keywords=["graphviz", "dot", "diagram", "flowchart"],
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
