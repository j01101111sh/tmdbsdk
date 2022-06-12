from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='tmdbsdk',
    version='0.1.0',
    author='Josh Odell',
    author_email='j01101111sh@gmail.com',
    description='A wrapper library for TMDB',
    keywords=['wrapper', 'tmdb', 'api'],
    url='https://github.com/j01101111sh/tmdbsdk',
    packages=['tmdbsdk'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests', 'pydantic'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)
