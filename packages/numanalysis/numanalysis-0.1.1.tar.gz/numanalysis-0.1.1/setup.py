from setuptools import setup, find_packages

setup(
    name='numanalysis',
    version='0.1.1',
    packages=find_packages(),
    description='Package for LU decomp',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Aminouche',
    author_email='solenouche@aminouche.fr',
    url='https://github.com/1030minouche',
    classifiers=[
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7',
    install_requires=[],
)