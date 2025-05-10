from setuptools import setup, find_packages

setup(
    name='get_weather',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A package to fetch and parse weather data.',
    packages=find_packages(),
    install_requires=[
        'requests',  # Example dependency for making HTTP requests
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)