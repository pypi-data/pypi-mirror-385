from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name='rushconsole',
    version='0.1.0',
    packages=find_packages(),
    requires=[
        'questionary'
    ],
    description='python console input',
    author='ndrzy',
    author_email='dandan0019@outlook.com',
    python_requires='>=3.10',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meatdumplings0019/rushconsole",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)