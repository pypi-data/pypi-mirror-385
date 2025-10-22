from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="thinagents_web",
    author="Prabhu Kiran Konda",
    description="Web application for ThinAgents",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/PrabhuKiran8790/thinagents_web",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "thinagents.frontend", "thinagents.frontend.*", "scripts", "scripts.*"]),
    package_data={
        "thinagents.web": ["ui/build/**/*"],
    },
    include_package_data=True,
    python_requires=">=3.10",   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="AI LLM Agentic AI AI Agents",
    use_scm_version=True,
    dependencies=[
        "thinagents>=0.0.16",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0"
    ],
    setup_requires=["setuptools-scm"],
)
