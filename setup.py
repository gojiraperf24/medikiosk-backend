"""Setup configuration for MediKiosk Backend"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="medikiosk-backend",
    version="0.1.0",
    author="MediKiosk Team",
    description="AI-powered clinical history software platform backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gojiraperf24/medikiosk-backend",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Healthcare",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "psycopg2-binary>=2.9.9",
        "pydantic>=2.4.2",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
    entry_points={
        "console_scripts": [
            "medikiosk=app.main:app",
        ],
    },
)
