from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    description = file.read()

setup(
    name='clusternet',
    version='0.9.3',
    description='Distributed Software Defined Network Emulation',
    long_description=description,
    long_description_content_type='text/markdown',
    keywords=['networking', 'emulator', 'containernet', 'mininet', 'OpenFlow', 'SDN', 'fog'],
    url='https://github.com/EsauM10/clusternet',
    author='Esaú Mascarenhas',
    author_email='esaumasc@gmail.com',
    classifiers=[
        'Intended Audience :: Developers'
    ],
    packages=find_packages(),
    install_requires = [
        'Flask',
        'Flask-Cors',
        'httpx',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'RunWorker = clusternet.server.worker_app:main',
        ]
    },
    include_package_data=True,
    zip_safe=False
)
