# setup.py
from setuptools import setup, find_packages

setup(
    name="qmad",              # Name of your package
    version="1.1.0",                    # Version of your package
    description="A package for adaptive variational quantum computing algorithms",
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',  # Description format
    url="https://github.com/saurabhshivpuje/QMAD",  # Project's homepage
    author="Saurabh Shivpuje",
    author_email="saushivpuje@gmail.com",
    license="MIT",                    # License for your package
    packages=find_packages(),  # Find all packages in src/
    # package_dir={"": "src"},          # Root package directory
    install_requires=[                # List of dependencies, if any
        "numpy","scipy","matplotlib"             
    ],
    python_requires='>=3.6',          # Minimum Python version
    classifiers=[                     # Additional metadata
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)