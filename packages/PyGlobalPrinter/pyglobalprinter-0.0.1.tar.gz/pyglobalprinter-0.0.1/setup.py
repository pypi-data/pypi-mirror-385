from setuptools import setup,find_packages

# print(find_packages())

with open("README.md",encoding="utf-8") as f:
    md = f.read()


setup(
    name="PyGlobalPrinter",
    version="0.0.1",
    author="wayne931121",
    author_email="",
    description="A tool when you have one more threading in a program and need to print.",
    long_description=md,
    long_description_content_type="text/markdown",
    license="Attribution 4.0 International, Copyright (c) 2025 Wayne931121.",
    url="https://github.com/wayne931121/",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
)