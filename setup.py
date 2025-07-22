from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='chemical_annotator',
    version='1.0',
    description='A package for chemical annotation using ChEMBL and PubChem data sources.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Linux',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    keywords='chemical annotation, ChEMBL, PubChem, cheminformatics',
    url='https://github.com/REMEDI4ALL/chemical_annotator',
    author='Flavio Ballante',
    author_email='flavioballante@gmail.com',
    license='MIT',
    packages=find_packages(include=["chemical_annotator", "utils", "utils.*"]),
    install_requires=[
        'pandas',
        'pubchempy',
        'chembl_webresource_client',
        'openpyxl',
        'tqdm',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'chemical_annotator=chemical_annotator.chemical_annotator:main'
        ],
    },
    include_package_data=True,
    python_requires='>=3.10',
    zip_safe=False
)

