from setuptools import setup

# Read the contents of the README file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mediacrop",
    version="4.0.0",
    author="Mallik Mohammad Musaddiq",
    author_email="mallikmusaddiq1@gmail.com",
    description="A CLI tool for visually determining FFmpeg crop coordinates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mallikmusaddiq1/mediacrop",
    license="MIT",

    # This is the most important part that includes all your .py files
    py_modules=[
        "mediacrop",
        "http_handler",
        "http_handler_js",
        "utils"
    ],

    # This creates the 'mediacrop' command in the terminal
    entry_points={
        "console_scripts": [
            "mediacrop = mediacrop:main",
        ],
    },

    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Utilities",
    ],
)
