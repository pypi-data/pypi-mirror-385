from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vault-service',
    version='1.3.0',
    description='A reusable python vault utility service for other projects to use hashicorp vault',
    author='Ankush Bansal',
    author_email='ankush.bansal@asato.ai',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'hvac>=2.3.0',
        'python-dotenv>=1.0.1',
        'pydantic>=2.9.2',
    ],
    python_requires='>=3.8',  # Specify the required Python version
)