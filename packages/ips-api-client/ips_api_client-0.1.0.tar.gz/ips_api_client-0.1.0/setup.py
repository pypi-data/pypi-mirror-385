from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ips-api-client",
    version="0.1.0",
    author="Steve Garrity",
    author_email="sgarrity@gmail.com",
    description="API client for IPS Controllers pool monitoring system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stgarrity/ips-api-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0",
    ],
)
