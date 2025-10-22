from setuptools import setup, find_packages

setup(
    name="realstarexx",
    version="1.0.2",
    author="Ankit Mehta",
    author_email="starexx.m@gmail.com",
    description="Coding and programming isn't same",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/realstarexx/starexx",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
