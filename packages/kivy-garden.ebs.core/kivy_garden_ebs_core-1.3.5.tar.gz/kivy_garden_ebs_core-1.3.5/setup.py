"""See README.md for package documentation."""

from setuptools import setup, find_namespace_packages

from io import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

URL = 'https://github.com/ebs-universe/kivy_garden.ebs.core'

setup(
    name='kivy_garden.ebs.core',
    description='A collection of pure python kivy widgets and widget '
                'infrastructure used internally by the EBS kivy GUI stack.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='Kivy kivy-garden',

    packages=find_namespace_packages(include=['kivy_garden.*']),
    install_requires=[
        'kivy>=1.11.1',
        'colorthief',  # Used by BleedImage
    ],
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    extras_require={
        'dev': ['pytest>=3.6', 'pytest-cov', 'pytest-asyncio',
                'sphinx_rtd_theme'],
        'ci': ['coveralls', 'pycodestyle', 'pydocstyle'],
    },
    package_data={},
    data_files=[],
    entry_points={},
    project_urls={
        'Bug Reports': URL + '/issues',
        'Source': URL,
    },
)
