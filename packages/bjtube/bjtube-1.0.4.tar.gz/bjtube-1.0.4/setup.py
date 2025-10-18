from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bjtube",
    version="1.0.4",
    author="Babar Ali Jamali",
    author_email="babar995@gmail.com",
    description="🎬 YouTube downloader with faster speed, ffmpeg is essential to use before installation. with auto-update and dependency installer by Babar Ali Jamali.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/babaralijamali/bjtube",
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "bjtube=bjtube.main:main",
        ],
    },
    python_requires=">=3.7",
)
