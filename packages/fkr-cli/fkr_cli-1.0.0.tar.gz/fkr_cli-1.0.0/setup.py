from setuptools import setup, find_packages

setup(
    name="fkr-cli",
    version="1.0.0",
    description="Gerador de dados fake multi-linguagem (Python, Delphi/Pascal, C#)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="FKR CLI Contributors",
    url="https://github.com/yourusername/fkr-cli",
    license="MIT",
    py_modules=['fkr'],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Code Generators",
    ],
    install_requires=[
        "typer>=0.9.0",
        "faker>=18.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fkr=fkr:cli",
        ],
    },
    python_requires=">=3.7",
)

