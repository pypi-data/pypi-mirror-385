from setuptools import setup, find_packages

setup(
    name="pydeskpro",
    version="1.0.0",
    author="SHAFIQUL ISLAM",
    author_email="shafiqul.cmt@gmail.com",
    description="Personal CLI Assistant for tasks, notes, expenses with backup system",
    packages=find_packages(),
    install_requires=["click", "rich"],
    entry_points={
        "console_scripts": [
            "pydesk = pydesk.main:cli"
        ],
    },
)