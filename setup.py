"""
Setup module.
"""
from setuptools import setup
from mmsim import __version__


setup(
    name='mmsim',
    version=__version__,
    description='A simple Micromouse Maze Simulator server',
    long_description='''The server can load different mazes and any client
        can connect to it to ask for the current position walls, move from
        one cell to another and visualize the simulated micromouse state.''',
    url='https://github.com/theseus/maze-simulator',
    author='Miguel Sánchez de León Peque',
    author_email='peque@neosit.es',
    license='BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords='micromouse maze server simulator',
    entry_points={
        'console_scripts': [
            'mmsim = mmsim.commands:launch',
        ],
    },
    packages=['mmsim'],
    install_requires=[
        'click',
        'numpy',
        'pyqtgraph',
        'pyqt5',
        'pyzmq'],
    extras_require={
        'dev': [],
        'test': ['tox'],
        'docs': ['sphinx', 'sphinx_rtd_theme'],
    },
)
