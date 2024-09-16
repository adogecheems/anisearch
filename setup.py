from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Anisearch-lib',
    version='1.3.4',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    entry_points={
        'console_scripts': ['anisearch=anisearch.cli:main'],
    },
    author='adogecheems',
    author_email='adogecheems@outlook.com',
    description='A library for searching anime magnet links',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://anisearch.mmoe.work',
    license='AGPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='search download magnet link magnet-link torrent anime dmhy comicat kisssub miobt nyaa acg.rip acgrip tokyotosho cli commandline',
)
