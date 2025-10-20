from setuptools import setup, find_packages

setup(
    name="eL-tfgen",
    version="0.1.14",
    description="Generate Terraform modules from documentation using AI",
    author="eLTitans",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "beautifulsoup4",
        "openai",
        "python-dotenv",
        "Pillow",
    ],
    entry_points={
        "console_scripts": [
            "tfgen=tfgen.cli:cli",
            "tfgen-ui=tfgen.ui:main",
        ],
    },
    python_requires=">=3.8",
) 