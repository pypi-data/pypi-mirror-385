from setuptools import setup, find_packages

setup(
    name="enventory",
    version="0.0.1",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0",
    ],
    description="Simple python dotenv utility wrapper",
    author="Bec",
)