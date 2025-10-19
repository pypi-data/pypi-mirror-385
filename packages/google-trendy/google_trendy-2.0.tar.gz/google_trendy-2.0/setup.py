import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="google_trendy",
    version="2.0",
    author="Michael Mondoro",
    author_email="michaelmondoro@gmail.com",
    description="Package for getting and analyzing tending Google searches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelMondoro/google_trendy",
    packages=setuptools.find_packages(exclude="tests"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['bs4', 'requests', 'lxml'],
    python_requires='>=3.7',
)
