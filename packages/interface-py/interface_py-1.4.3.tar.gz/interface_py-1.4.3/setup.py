import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="interface-py",
    version="1.4.3",
    author="Ehsan Karbasian",
    author_email="ehsan.karbasian@gmail.com",
    description="A package to define interface in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ehsankarbasian/interface-py",
    package_dir={"": "src"},
    packages=setuptools.find_packages(
        where="src",
        include=["interface_py", "interface_py._internals"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
