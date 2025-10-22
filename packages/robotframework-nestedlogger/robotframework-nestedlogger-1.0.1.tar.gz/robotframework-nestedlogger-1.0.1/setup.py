"""Setup file for robotframework-NestedLogger package."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='robotframework-nestedlogger',
    version='1.0.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Robot Framework library for nested keyword logging in Python implementations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/robotframework-NestedLogger',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Robot Framework',
        'Framework :: Robot Framework :: Library',
        'Framework :: Robot Framework :: Library',
    ],
    keywords='robotframework testing testautomation nested logging',
    python_requires='>=3.10',
    install_requires=[
        'robotframework>=7.3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],
    },
    license='Apache License 2.0',
    platforms='any',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/robotframework-NestedLogger/issues',
        'Source': 'https://github.com/yourusername/robotframework-NestedLogger',
    },
)
