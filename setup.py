
from setuptools import setup, find_packages

setup(
    name='pytest-oot',
    description='Run object-oriented tests in a simple format',
    author='Steven LI',
    author_email='steven004@gmail.com',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: System :: Logging",
        "Programming Language :: Python :: 3"
    ],
    version='0.5.6',
    #py_modules = ['pytest_oot'],
    entry_points = {
        'pytest11': [
            'pytest_oot = pytest_oot.oot_plugin',
        ]
    },
    url = "https://github.com/steven004/pytest_oot",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['py>=1.3.0', 'pytest', 'test_steps>=0.6'],
)

