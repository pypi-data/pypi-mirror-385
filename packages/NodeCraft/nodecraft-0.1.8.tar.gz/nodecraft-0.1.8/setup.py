from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="NodeCraft",
    version="0.1.8",
    description="A modular framework for building composable AI workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NodeCraft Team",
    url="https://github.com/bethneyQQ/NodeCraft",
    packages=find_packages(
        exclude=["tests", "tests.*", "examples", "tutorial_examples"]
    ),
    py_modules=["cli", "engine"],
    include_package_data=True,
    package_data={
        "prompts": ["*.md"],
    },
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0.0",
        "requests>=2.28.0",
        "gitpython>=3.1.0",
        "tree-sitter>=0.20.0",
        "jinja2>=3.1.0",
        "pathspec>=0.11.0",
        "anthropic>=0.18.0",
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nodecraft=cli:cli",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="code-analysis llm ai devops quality-assurance",
)
