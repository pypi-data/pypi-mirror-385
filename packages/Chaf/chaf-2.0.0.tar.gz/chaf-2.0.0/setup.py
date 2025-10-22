import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    lng_description = fh.read()

setuptools.setup(
    name="Chaf",
    version="2.0.0",
    author="deep",
    author_email="asyncpy@gmail.com",
    license="MIT",
    description="Chaf is a Python library designed to automatically detect and decode encrypted text using the Chaf web interface. You simply provide an encoded string, and the library processes it to identify the encryption type and return the decoded result in structured JSON format.",
    long_description=lng_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
