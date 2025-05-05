from setuptools import setup, find_packages

setup(
    name="log_analysis",
    version="0.1",
    packages=find_packages(),
    description="Remote log analysis automation tools",
    author="Ben Kaan",
    author_email="benkaan001@gmail.com",
    python_requires=">=3.6",
    # Add any package dependencies here
    install_requires=[
        "pandas",
        "paramiko",
        "python-dotenv",
        "openpyxl",
        "jupyter",
        "notebook",
        "ipykernel",
        "tabulate"
    ],
    # Add entry points for command-line tools
    entry_points={
        'console_scripts': [
            'log-analyzer=src.log_analyzer:main',  # Assumes you have a main() function
        ],
    },
)