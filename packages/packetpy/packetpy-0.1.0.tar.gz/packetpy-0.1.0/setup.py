from setuptools import setup, find_packages

setup(
    name="packetpy",
    version="0.1.0",
    author="Arun Sundar K",
    author_email="karthicksundar2001@gmail.com",
    description="Windows raw packet sniffer (TCP/UDP) module",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arunsundark01",
    packages=find_packages(),
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Networking",
    ],
)