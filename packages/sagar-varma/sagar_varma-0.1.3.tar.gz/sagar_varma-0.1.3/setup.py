from setuptools import setup, find_packages

setup(
    name='sagar-varma',
    version='0.1.3',
    author='huiiy',
    description='A simple terminal-based snake game.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/tsnake',  # Replace with your GitHub URL
    packages=find_packages(),
    install_requires=['unicurses'],
    entry_points={
        'console_scripts': [
            'sagar = tsnake.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
    ],
)
