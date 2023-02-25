from setuptools import setup, find_packages

EXCLUDED_PACKAGES = list()

setup(
    name='parsi_io',
    version='0.1.0',
    packages=find_packages(include=['parsi_io', 'parsi_io.*'], exclude=EXCLUDED_PACKAGES),
    install_requires = [
        'hazm>=0.7.0',
        'tqdm',
        'camel-tools',
        'Tashaphyne',
        'gdown'
    ],
    setup_requires=['flake8'],
    url='https://github.com/language-ml/parsi.io.git',
    license='Apache License 2.0',
    author='Language-ml team',
    description='A persian NLP module',
)