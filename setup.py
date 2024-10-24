from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkedin-profile-pic",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool to download LinkedIn profile pictures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linkedin-profile-pic",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "requests",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "linkedin-profile-pic=linkedin_profile_pic.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
