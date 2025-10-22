import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DRES",
    version="0.1.0",
    author="Danish",
    author_email="author@example.com",  # Replace with a real email if you like
    description="A pure-Python hybrid encryption system based on Diffie-Hellman and AES.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/DRES",  # Replace with your GitHub repo URL
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
