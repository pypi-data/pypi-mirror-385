from setuptools import setup, find_packages
from pathlib import Path

# Path to current directory
HERE = Path(__file__).parent

# Read README.md correctly
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="django-otp-auth",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    description="OTP module for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "Django>=3.0",
    ],
)

