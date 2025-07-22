# Chemical Annotator
The Chemical Annotator is a tool to collect drug annotations from public chemical databases (including, [ChEMBL](https://www.ebi.ac.uk/chembl/), [UniChem](https://www.ebi.ac.uk/unichem/), [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and [KEGG](https://www.genome.jp/kegg/pathway.html)) based on exact match with query pattern.
This repository contains code and instructions to run the method on your own chemical library.
If you have any question, feel free to open an issue or reach out to: flavioballante@gmail.com
![Overview](/images/overview.png)
## Setup environment
Clone the current repository:
```
git clone https://github.com/REMEDI4ALL/chemical_annotator
```
Create and activate a conda environment from the environment.yml file
```
conda env create -f environment.yml
conda activate chemical_annotator
pip install -e .
```
### Usage
You can run the Chemical Annotator from the command line with the following options:
```
usage: chemical_annotator [-h] [-v] [-a] [-i INPUT] [-o OUTPUT] [-f FORMAT] [-ct CONFIDENCE_THRESHOLD] [-at ASSAY_TYPE_IN] [-pcm PCHEMBL_VALUE_GTE]

Chemical Annotator

options:
  -h, --help            show this help message and exit
  -v, --version         Show version information and exit
  -a, --author          Show author information and exit
  -i INPUT, --input INPUT
                        Input .csv file
  -o OUTPUT, --output OUTPUT
                        Output .xlsx file
  -f FORMAT, --format FORMAT
                        Type of chemical notation to use as query (SMILES, InChI, or InChIKey)
  -ct CONFIDENCE_THRESHOLD, --confidence_threshold CONFIDENCE_THRESHOLD
                        Minimum confidence score value (default: 8)
  -at ASSAY_TYPE_IN, --assay_type_in ASSAY_TYPE_IN
                        Comma-separated list of assay types (default: B, F)
  -pcm PCHEMBL_VALUE_GTE, --pchembl_value_gte PCHEMBL_VALUE_GTE
                        Minimum pChEMBL value (default: 6)
```

### Example
Let's say you want to collect annotations for a chemical library called my_library.csv.
The library csv file should contain at least one among these chemical identifiers: SMILES, InChI, and InChIKey. 
Any additional information in the input csv file (e.g., IDs, chemical properties, etc.) is retained in the results.

Example of an input file:
```
smiles,anyotherfield1,anyotherfield2
CC(=O)Oc1ccccc1C(=O)O,SomeText/Value,SomeText/Value
...
...
```
- Basic usage, all defaults: confidence score ≥ 8, assay type: Binding (B), Functional (F), and pChEMBL value ≥ 6
```
chemical_annotator -i my_library.csv -o my_library -f smiles
```
- Customize specific filters and keep the remaining on defaults:
e.g., to increase the minimum pChEMBL value to 8, while keep confidence threshold and assay types at defaults (8 and B, F).
```
chemical_annotator -i my_library.csv -o my_library -f smiles -pcm 8
```
- Customize all parameters:
e.g., to consider only binding assays with a minimum confidence score of 9 and pChEMBL value of 8.
```
chemical_annotator -i my_library.csv -o my_library -f smiles -ct 9 -at B -pcm 8
```

### Citation
If you use the Chemical Annotator in your research, please cite our work as follows:
```
Jeanette Reinshagen, Brinton Seashore-Ludlow, Yojana Gadiya, Anna-Lena Gustavsson, Ziaurrehman Tanoli, Tero Aittokallio,
Johanna Huchting, Annika Jenmalm-Jensen, Philip Gribbon, Andrea Zaliani & Flavio Ballante (2025).
“From Library to Landscape: Integrative Annotation Workflows for Compound Libraries in Drug Repurposing”, submitted.

GitHub repository: https://github.com/REMEDI4ALL/chemical_annotator
```
### License
MIT
