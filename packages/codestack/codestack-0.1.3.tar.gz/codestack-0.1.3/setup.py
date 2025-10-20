from setuptools import setup, find_packages
import pathlib
# Path to this directory
here = pathlib.Path(__file__).parent.resolve()

# Read the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="codestack",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "codestack": [".env.example"],
    },
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv==1.1.1",
        "google-generativeai==0.8.5",
    ],
    description="AI-powered developer that transforms natural language instructions into complete, runnable projects for any tech stack.",
    long_description=long_description,  # README content
    long_description_content_type="text/markdown",
    url="https://github.com/AdityaTheDev/codestack",
    author="Aditya Hariharan",
    author_email="aditya.h@zohomail.in",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
)
