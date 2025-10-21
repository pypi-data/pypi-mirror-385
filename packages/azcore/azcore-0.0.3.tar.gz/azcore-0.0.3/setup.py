"""
Setup configuration for Azcore..
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="azcore",
    version="0.0.3",
    author="Azrienlabs team",
    author_email="info@azrianlabs.com",
    description="A professional hierarchical multi-agent framework built on python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Azrienlabs/Az-Flow",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "mcp": [
            "langchain-mcp-adapters>=0.1.0",
        ],
    },
    include_package_data=True,
    package_data={
        "azcore": ["py.typed"],
    },
    zip_safe=False,
    keywords="Multi-agent agents ai framework hierarchical azcore reinforcement-learning",
    project_urls={
        "Bug Reports": "https://github.com/Azrienlabs/Az-Flow/issues",
        "Source": "https://github.com/Azrienlabs/Az-Flow",
        "Documentation": "https://github.com/Azrienlabs/Az-Flow",
    },
)
