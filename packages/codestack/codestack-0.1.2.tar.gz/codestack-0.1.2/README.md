# Codestack

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![PyPI Version](https://img.shields.io/pypi/v/codestack)
![License](https://img.shields.io/badge/license-MIT-green)

**Codestack** is a universal, programming- and framework-agnostic project generator for any tech stack.  
It allows developers to generate any kind of full projects, be it web apps, mobile apps, machine learning solutions, to backend services using simple natural language instructions. Codestack automatically creates folder structures, source files, configuration files, and dependency files.

---

## Features

- Generate full projects using natural language instructions  
- Supports any tech stack: frontend, backend, mobile, machine learning, hybrid projects, etc.  
- Automatically generates dependency files and environment configuration  
- Preview generated projects without opening them  
- Easy-to-use Python package  

---

## Python Version Requirement

Codestack requires **Python 3.9 or higher**. Tested on Python 3.9, 3.10, 3.11, 3.12, and 3.13.

---

## Installation

Install Codestack via pip:

```bash
pip install codestack
```

```env
# .env file should contain this
GOOGLE_API_KEY="your google api key here"
GEMINI_MODEL_NAME="model name here"
```

```python
from codestack import create_env, build_project, preview_project

# Step 1: If you haven't created the .env file already to create a .env file
create_env()
# Set the appropriate API keys and model name in the .env

# Step 2: Build a project from a natural language prompt
build_project(
    "Create a functional finance calculator which has the following features: CAGR calculator, EMI calculator, wealth time estimator",
    output_dir="finance_calculator"
)

# Step 3: Preview the generated project
preview_project("finance_calculator")

# Developers have full access to the generated project for further customization and development
```