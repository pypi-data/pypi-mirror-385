from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="omam-authkit",
    version="0.1.0",
    author="Osman",
    author_email="osman@hamashool.com",
    description="Python SDK for OMAM AuthKit - OAuth 2.0 authentication provider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hamashoool/omam-authkit-python-sdk",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "PyJWT>=2.8.0",
    ],
    extras_require={
        "django": [
            "Django>=3.2",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)
