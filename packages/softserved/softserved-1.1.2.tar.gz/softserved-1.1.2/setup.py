from setuptools import setup # type: ignore

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="softserved",
    version="1.1.2",
    author="Tola Oyelola",
    author_email="tola@ootola.com",
    description="A lightweight, stylish local web server for static files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tolaoyelola/softserved",
    py_modules=["softserved"],
    entry_points={
        "console_scripts": [
            "softserved=softserved:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.6",
    install_requires=[
        "colorama>=0.4.3",
        "watchdog>=3.0.0",
    ],
)