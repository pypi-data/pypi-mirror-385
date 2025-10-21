import setuptools
setuptools.setup(
    name="tradeapi",
    version="0.1.13",
    author="Alexander Illyuk",
    author_email="aaillyuk@gmail.com",
    description="Python package for Finam API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/example-pip-package",
    license="MIT",
    py_modules=["tradeapi"],
    packages=setuptools.find_packages(include=["finamgrpc", "finamgrpc.*"]),
    # package_dir maps package roots -> filesystem dirs; here root is "."
    package_dir={"": "."},
    python_requires=">=3.7",
    install_requires=[
        "grpcio>=1.39.0",                    # gRPC core library
        "protobuf>=5.0.0",                  # Google Protobuf runtime
        "googleapis-common-protos>=1.53.0",  # Common proto types (e.g., Timestamp)
        "pandas>=1.1.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        # Example console script
        # 'console_scripts': ['example=example_pip_package.greet:main'],
    },
)



