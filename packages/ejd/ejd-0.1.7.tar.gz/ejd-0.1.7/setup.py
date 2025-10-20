from setuptools import setup, find_packages

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ejd",
    version="0.1.7",
    author="Ahmed Samir",
    author_email="ahmedsamirhelmy2003@gmail.com",
    description="A CLI tool for static code analysis and fixing using Gemini AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "google-generativeai>=0.3.0",
    ],
    entry_points={
        'console_scripts': [
            'ejd=ejad.cli:main',
        ],
    },
)
