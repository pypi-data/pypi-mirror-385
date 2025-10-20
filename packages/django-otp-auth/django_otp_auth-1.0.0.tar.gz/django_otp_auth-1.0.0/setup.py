from setuptools import setup, find_packages

setup(
    name="django-otp-auth",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="Reusable Django app for OTP-based authentication using external API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Saurabh Maurya",
    author_email="youremail@example.com",
    url="https://github.com/saurabhmaurya/django-otp-auth",
    install_requires=["django>=4.0", "requests"],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
