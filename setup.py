from setuptools import setup, find_packages

setup(
    name='publi_cast',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g.,
        'pyaudio',
        'numpy',
        'pywin32'
    ],
    entry_points={
        'console_scripts': [
            'audacity_control=main:main',
        ],
    },
)
