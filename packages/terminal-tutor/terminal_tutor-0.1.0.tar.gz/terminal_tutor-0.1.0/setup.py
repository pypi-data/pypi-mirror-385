"""Setup script for Terminal Tutor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""
except (UnicodeDecodeError, FileNotFoundError):
    long_description = ""

setup(
    name="terminal-tutor",
    version="0.1.0",
    author="Jatin Mayekar",
    author_email="jatin@terminaltutor.dev",
    description="Real-time terminal command education for Zsh - 36-38ms predictions, 459+ commands (Zsh required)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jatinmayekar/terminal-tutor",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "terminal_tutor": ["data/*.json", "*.zsh"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Shells",
        "Topic :: Education",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=10.0.0",
        "requests>=2.25.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "terminal-tutor=terminal_tutor.cli:main",
        ],
    },
    keywords="terminal, cli, learning, commands, tutorial, zsh, shell, education, real-time",
    license="Proprietary",
)