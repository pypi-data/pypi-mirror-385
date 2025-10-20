from setuptools import setup, find_packages

setup(
    name="lowmind",
    version="0.5.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},

    install_requires=[
        "numpy>=1.19.0",
        "psutil>=5.8.0"
    ],
    author="VEDRA",
    description="Ultra-lightweight Deep Learning Framework for Raspberry Pi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dhaval-gamet/lowmind",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
)
