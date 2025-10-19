import os
from setuptools import setup, find_packages

setup(
    name="kcleaner-py",
    version=open(os.path.abspath("version.txt")).read(),
    description="Secure CLI tool to identify and delete KATE backup files (*.~ and .*~) with user confirmation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Skye",
    author_email="swskye17@gmail.com",
    url="https://github.com/skye-cyber/kcleaner",
    packages=find_packages(),
    py_modules=["kcleaner"],
    entry_points={
        "console_scripts": [
            "kcleaner=kcleaner:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        # "kcleaner": ["dirname/**", "config.json"],
    },
    # include_dirs=[...],
    zip_safe=False,
    license="GNU v3",
    keywords=["dir_clean", "tmp_clean", "scanner", "cleaner"],
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
