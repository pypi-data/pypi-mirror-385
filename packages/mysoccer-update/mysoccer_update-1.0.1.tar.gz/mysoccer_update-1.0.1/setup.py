"""
MySoccer Update - Setup Script
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mysoccer-update",
    version="1.0.1",
    author="ahmety",
    author_email="your-email@example.com",
    description="Mackolik.com API'den futbol maç verilerini çeken modüler Python kütüphanesi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmety/mysoccer-update",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "psycopg>=3.1.0",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "scheduler": [
            "schedule>=1.2.0",
        ],
    },
    keywords="football soccer data scraping mackolik api mysoccer",
    project_urls={
        "Bug Tracker": "https://github.com/ahmety/mysoccer-update/issues",
        "Documentation": "https://github.com/ahmety/mysoccer-update#readme",
        "Source Code": "https://github.com/ahmety/mysoccer-update",
    },
)
