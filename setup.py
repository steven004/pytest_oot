
from setuptools import setup, find_packages

setup(
    name='pytest-oot',
    description='Run object-oriented tests in a simple format',
    author='Steven LI',
    author_email='steven004@gmail.com',
    version='0.5.0',
    #py_modules = ['pytest_oot'],
    entry_points = {
        'pytest11': [
            'pytest_oot = pytest_oot.oot_plugin',
        ]
    },
    url = "https://pypi.python.org/pypi?name=pytest-oot&:action=display",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['py>=1.3.0', 'pytest', 'test_steps>=0.6'],
)

