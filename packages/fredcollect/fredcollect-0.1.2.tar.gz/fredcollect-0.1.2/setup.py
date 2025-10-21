from setuptools import setup, find_packages

setup(
    name='fredcollect', 
    version='0.1.2',
    author='Oliver Grenon',
    author_email='grenonoliver@gmail.com',
    description='A Python wrapper for the Federal Reserve Economic Database (FRED) API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/versaucc/fredcollect',
    packages=find_packages(include=['fredcollect', 'fredcollect.*']),
    install_requires=[
        'requests',
        'pandas>=1.5.3',
        'numpy>=1.23.5',
        'python-dotenv',
        'matplotlib'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    include_package_data=True,
    license='Apache 2.0',
)