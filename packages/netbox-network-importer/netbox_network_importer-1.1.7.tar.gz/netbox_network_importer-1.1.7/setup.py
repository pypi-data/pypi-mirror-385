"""Package configuration."""
from setuptools import find_packages, setup
from netbox_network_importer import __appname__

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

requirements = [
    'click',
    'pynetbox==7.4.1',
    'python-slugify',
    'appdirs',
    'pyyaml',
    'python-dotenv',
    'pyats[full]==25.2',
    'netutils',
    'nornir==3.5.0',
    'nornir-netbox',
    'nornir_utils',
    'nornir_rich',
    'deepdiff',
    'napalm==5.0.0',
    'ncclient',
    'loguru',
    'dictdiffer',
    'json2html',
    'jsonpickle',
]

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest", "pytest-cov", "pytest-mock", "pynxos", "ipdb"
]

setup(
    name=__appname__,
    author="Jan Krupa",
    author_email="jan.krupa@cesnet.cz",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Operating System :: Unix",
    ],
    description='Poll data from devices and store them into Netbox',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    include_package_data=True,
    keywords="netbox,network",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.cesnet.cz/701/done/netbox_network_importer",
    version='1.1.7',
    zip_safe=False,
    python_requires='>=3.6, <4',
    entry_points={
        'console_scripts': [
            'netbox_network_importer=netbox_network_importer.__main__:cli',
        ]
    },
)
