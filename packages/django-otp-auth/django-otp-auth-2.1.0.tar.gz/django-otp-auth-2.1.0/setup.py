from setuptools import setup
from pathlib import Path

# Path to current directory
HERE = Path(__file__).parent

# Read README.md safely
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="django-otp-auth",
    version="2.1.0",
    py_modules=["otp_auth"],  
    include_package_data=True,
    description="OTP authentication module for Django without database storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Saurabh Maurya",
    author_email="youremail@example.com",  # optional but recommended
    url="https://pypi.org/project/django-otp-auth/",
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.0",
        "Django>=3.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ],
)

