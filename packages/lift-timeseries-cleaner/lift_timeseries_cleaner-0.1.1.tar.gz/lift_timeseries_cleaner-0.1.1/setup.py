from setuptools import setup, find_packagesfrom setuptools import setup, find_packagesfrom setuptools import setup, find_packages



setup(from pathlib import Path

    name="lift_timeseries_cleaner",

    version="0.1.0",setup(

    packages=find_packages(),

    install_requires=["pandas>=1.0.0"],    name="lift_timeseries_cleaner",# Read the README file for the long description on PyPI

)
    version="0.1.0",this_directory = Path(__file__).parent

    packages=find_packages(),readme_path = this_directory / "README.md"

    install_requires=["pandas>=1.0.0"],long_description = readme_path.read_text(encoding="utf-8")

)
setup(
    name="lift_timeseries_cleaner",
    version="0.1.0",
    author="John Kamau",
    author_email="kkamaujohn@gmail.com",
    description="A small library to preprocess diary/transaction data for time series models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://example.com/timeseries-cleaner",  # update with real project URL
    packages=find_packages(include=["timeseries_cleaner*"]),
    install_requires=["pandas>=1.0.0"],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)