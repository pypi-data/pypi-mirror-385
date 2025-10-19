from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="linkminer",
    version="1.0.0",
    author="Skye Wambua",
    description="A CLI tool to recursively download specific file types from websites (e.g., pdf, txt).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="swskye17@gmail.com",
    url="https://github.com/skye-cyber/linkminer",
    packages=find_packages(),
    # py_modules=["cli"],
    entry_points={
        "console_scripts": [
            "linkminer = linkminer.cli:main",
        ]
    },
    install_requires=["requests", "beautifulsoup4", "tqdm"],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
