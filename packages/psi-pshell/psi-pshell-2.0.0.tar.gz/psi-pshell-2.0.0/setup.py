from setuptools import setup

setup(
    name='psi-pshell',
    version="2.0.0",
    author='Paul Scherrer Institute',
    author_email="daq@psi.ch",
    description="pshell is Python a client to PShell REST API",
    license="GPLv3",
    keywords="",
    url="https://github.com/paulscherrerinstitute/pshell/tree/master/python",
    install_requires=['requests', 'pyzmq'],
    packages=['pshell']
)
