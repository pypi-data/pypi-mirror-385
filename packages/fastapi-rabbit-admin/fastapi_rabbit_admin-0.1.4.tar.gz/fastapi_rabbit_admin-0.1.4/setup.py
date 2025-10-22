from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A FastAPI admin dashboard for Tortoise ORM models"

setup(
    name="fastapi-rabbit-admin",
    version="0.1.4",
    author="Your Name",
    author_email="your.email@example.com",
    description="A FastAPI admin dashboard for Tortoise ORM models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rabbit-admin",
    packages=find_packages(exclude=["tests", "tests.*", "migrations", "migrations.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "tortoise-orm>=0.20.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "aerich>=0.7.0",
            "uvicorn[standard]>=0.24.0",
        ],
    },
    include_package_data=True,
    package_data={
        "rabbit_admin": ["static/**/*", "static/**/**/*", "static/**/**/**/*"],
    },
)
