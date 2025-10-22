from setuptools import setup, find_packages
from Cython.Build import cythonize

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='nawawan',
    version='0.1.6',
    description='A simple library for basic statistical calculations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nawawan Thaichim',
    author_email='woonzy09@email.com',
    packages=find_packages(),
    install_requires=[
        "pytest"
    ],
    license='MIT',
    python_requires='>=3.7',
    ext_modules=cythonize(
        ["nawawan/*.py"], 
        compiler_directives={'language_level': "3"}
    ),
)
