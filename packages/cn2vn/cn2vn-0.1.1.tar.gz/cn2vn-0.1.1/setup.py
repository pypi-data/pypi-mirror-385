from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cn2vn",
    version="0.1.1",
    author="jetaudio.media",
    author_email="jetaudio.media@gmail.com",
    description="A library to convert Chinese text to Vietnamese using Sino-Vietnamese readings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jetaudio.media/cn2vn",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    include_package_data=True,
    package_data={
        'cn2vn': ['dictionary.json'],
    },
)