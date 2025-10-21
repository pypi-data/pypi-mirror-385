
from setuptools import setup, find_packages
import os

# Read the README.md for the long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CVNN_Jamie',
    version='0.3.0',
    description='A neural network framework supporting complex and real-valued neural networks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jamie Keegan-Treloar',
    author_email='jamie.kt@icloud.com',
    url='https://github.com/Gunter-The-Third/Jamies_CVNN',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    keywords='complex neural network, real neural network, deep learning, numpy',
    include_package_data=True,
)
