from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='anisearch',
    version='1.0.0',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['anisearch=anisearch.search.cli:main'],
    },
    author='adogecheems',
    author_email='adogecheems@outlook.com',
    description='A library for searching anime magnet links',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/adogecheems/anisearch',
    license='AGPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 (AGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='search download anime dmhy',
    pyton_requires='>=3.6'
)
