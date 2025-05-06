from setuptools import setup, find_packages

setup(
    name="log_analysis",
    version="0.1",
    packages=find_packages(),
    description="Remote log analysis automation tools",
    author="Ben Kaan",
    author_email="benkaan001@gmail.com",
    python_requires=">=3.6",
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
    entry_points={
        'console_scripts': [
            'log-analyzer=src.log_analyzer:main',
        ],
    },
)