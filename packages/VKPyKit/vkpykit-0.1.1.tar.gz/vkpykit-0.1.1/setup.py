from setuptools import setup, find_packages

setup(
    name='VKPyKit',
    version='0.1.0',
    description='Packaged functions for ML and Data Science tasks.',
    author='Vishal Khapre',
    author_email='assignarc@gmail.com',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'IPython.display'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
