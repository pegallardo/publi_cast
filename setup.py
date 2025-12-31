from setuptools import setup, find_packages

setup(
    name='publi_cast',
    version='0.1.0',
    description='Audio processing application that automates audio enhancement using Audacity',
    author='pegallardo',
    url='https://github.com/pegallardo/publi_cast',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'dependency-injector',
        'numpy',
        'scipy',
        'soundfile',
        'pygetwindow',
        'google-api-core',
        'google-auth',
        'pywin32',
        'rich',
        'distlib',
        'jaraco.context',
    ],
    extras_require={
        'dev': [
            'pytest',
        ]
    },
    entry_points={
        'console_scripts': [
            'publi_cast=publi_cast.main:main',
        ],
    },
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
