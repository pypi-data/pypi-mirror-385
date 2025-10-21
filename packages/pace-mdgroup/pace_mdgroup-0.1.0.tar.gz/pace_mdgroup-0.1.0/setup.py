from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name='pace',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # 'numpy>=1.24',
        # 'python>=3.10'

    ],
    long_description=description,
    long_description_content_type='text/markdown'
)