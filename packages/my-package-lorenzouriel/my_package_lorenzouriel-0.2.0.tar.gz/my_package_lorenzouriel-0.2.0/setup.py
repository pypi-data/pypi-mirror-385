from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='my_package_lorenzouriel',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[],
    author='Lorenzo Uriel',
    long_description=description,
    long_description_content_type="text/markdown"
)