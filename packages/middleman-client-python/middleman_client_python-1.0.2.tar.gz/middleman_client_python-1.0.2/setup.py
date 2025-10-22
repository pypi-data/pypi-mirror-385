import os
from setuptools import setup, find_packages

# Read requirements from requirements.txt
def read_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        with open(req_file, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["websockets>=11.0", "typing-extensions>=4.0.0", "aiohttp>=3.8.0"]

setup(
    name="middleman-client-python",
    version="1.0.2",
    author="andyyy2k",
    description="Python client library for MiddleMan applications",
    long_description="A Python client library for connecting to MiddleMan applications using WebSocket connections.",
    long_description_content_type="text/plain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    include_package_data=True,
    zip_safe=False,
)
