from setuptools import setup, find_packages

setup(
    name="text-analysis-matrix",
    version="0.1.0",
    packages=find_packages(),
    description="A simple text analysis Python library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Eldar Eliyev",
    author_email="your_email@example.com",
    url="https://github.com/eldar/text-analysis-matrix",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
