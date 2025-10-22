from setuptools import setup, find_packages

setup(
    name='butext',
    version='0.3.5',
    description='https://butext.readthedocs.io/en/latest/',
    long_description="placeholder",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn'
    ]
)