from setuptools import setup, find_packages

setup(
    name="codestack",
    version="0.1.1",
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
    author="Aditya Hariharan",
    author_email="aditya.h@zohomail.in",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
)
