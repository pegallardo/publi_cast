from setuptools import setup, find_packages

setup(
    name='test',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g.,
        # 'pyaudio',
        # 'numpy',
    ],
    entry_points={
        'console_scripts': [
            'audacity_control=main:main',
        ],
    },
)
