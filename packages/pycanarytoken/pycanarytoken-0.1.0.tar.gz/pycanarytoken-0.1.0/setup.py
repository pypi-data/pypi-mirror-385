from setuptools import setup, find_packages

setup(
    name='pycanarytoken',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'pycanarytoken=pycanarytoken_lib.core:main',
        ],
    },
    author='JACK',
    author_email='gsksvsksksj@gmail.com',
    description='A Python library to generate Canarytokens',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

