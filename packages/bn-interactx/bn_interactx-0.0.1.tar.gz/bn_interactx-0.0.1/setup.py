# setup.py
from setuptools import setup, find_packages

setup(
    name='bn_interactx',  # only lowercase and dashes
    version='0.0.1',
    author='jovi',
    author_email='jo.vinckier@bynubian.com',
    description='basic user-interaction',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/bynubian/bynode/python_packages/interactx',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        # 'requests>=2.32.4',
        # 'python-decouple>=3.8'
        # dependencies: other packages required
        # eg 'numpy>=1.11.1'
    ]
)
