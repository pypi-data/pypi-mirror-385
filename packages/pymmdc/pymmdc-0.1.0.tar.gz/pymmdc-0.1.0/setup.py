import os
from setuptools import find_namespace_packages, setup


DESCRIPTION = "Pure Python Mermaid Diagram Converter with robust error handling"
EXCLUDE_FROM_PACKAGES = ["build", "dist", "test", "src", "*~", "*.db"]


setup(
    name="pymmdc",
    author="wambua",
    author_email="swskye17@gmail.com",
    version=open(os.path.abspath("version.txt")).read(),
    packages=find_namespace_packages(exclude=EXCLUDE_FROM_PACKAGES),
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/pymmdc/",
    entry_points={
        "console_scripts": [
            "pymmdc=mmdc:main",
        ],
    },
    python_requires=">=3.12",
    install_requires=["setuptools", "wheel", "argparse"],
    include_package_data=True,
    package_data={
        # "pymmdc": ["dirname/**", "config.json"],
    },
    # include_dirs=[...],
    zip_safe=False,
    license="GNU v3",
    keywords=["mmdc", "pymmdc", "mermaid", "png", "mermaid_diagram"],
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
