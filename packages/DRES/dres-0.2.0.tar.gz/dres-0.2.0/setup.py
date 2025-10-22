import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DRES",
    version="0.2.0",
    author="Danish",
    author_email="askthedanish@gmail.com",
    description="A pure-Python hybrid encryption system with EKC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1Danish-00",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.6",
)
