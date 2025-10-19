from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="abagentsdk",
    version="0.0.5",  # bump
    description="The fastest way to build AI agents using Google Gemini",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["abagentsdk*"]),
    include_package_data=True,
    install_requires=[
        "google-generativeai>=0.7.0",
        "pydantic>=2.6.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.1",
        "tzdata>=2024.1; platform_system == 'Windows'",
        "typing-extensions>=4.12.0; python_version < '3.11'",
    ],
    python_requires=">=3.10",
    license="MIT",
    author="Abu Bakar",
    url="https://github.com/ABZAgent/abzagentsdk",
    project_urls={
        "Homepage": "https://github.com/ABZAgent/abzagentsdk",
        "Issues": "https://github.com/ABZAgent/abzagentsdk/issues",
        "Documentation": "https://abzagent.vercel.app",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=["agents", "gemini", "google generative ai", "sdk", "llm", "tool calling"],
     entry_points={
        "console_scripts": [
            "abagentsdk=abagentsdk.cli:main",
        ],
     },
)
