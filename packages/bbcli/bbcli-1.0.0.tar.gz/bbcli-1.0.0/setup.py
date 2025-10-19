from setuptools import setup


setup(
    name='bbcli',
    version='1.0.0',
    description='DEPRECATED - Python version no longer maintained. Install the Rust version: cargo install bbc-news-cli',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords='bbc news console terminal deprecated',
    author='Wesley Hill, Calvin Hill',
    author_email='wesley@hakobaito.co.uk',
    url='https://github.com/hako/bbcli',
    packages=['bbcli'],
    install_requires=[],
    classifiers=[
        'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Terminals',
    ],
    entry_points={
        'console_scripts': ['bbcli = bbcli.core:live']
    })
