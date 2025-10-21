<!-- <h1 align="center">PACE (Precise and Accurate Configuration Evaluation)</h1>

<h4 align="center">

</h4> -->
<p align="center">
  <img src="./logo_2.png" alt="Precise and Accurate Configuration Evaluation" width="600"/>
</p>
<br/>


<h4 align="center">


![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-5C6216?logo=python&logoColor=white&style=flat-square)
[![Static Badge](https://img.shields.io/badge/doi-arXiv.2510.15397-5C6216?style=flat-square)](https://doi.org/10.48550/arXiv.2510.15397)
[![MIT License](https://img.shields.io/badge/License-MIT-5C6216.svg?style=flat-square)](https://choosealicense.com/licenses/mit/)

</h4>
The workbook contains the code and notebook to run PACE (Precise and Accurate Configuration Evaluation).

PACE identifies stable ground-state base–adsorbate configurations through a multistep approach. It begins by performing single-point MLIP calculations on adsorbates placed at predefined grid points within the unit cell, where grid resolution (number of subdivisions along each axis) controls the density of possible adsorption sites.

After ranking the resulting configurations based on single-point MLIP energy predictions, the most promising candidates undergo MLIP structure optimization, followed by first-principles DFT optimization of the MLIP-predicted ground state. 


## 🚀 Environment Setup

- System requirements: The package is designed to run on a standard Linux system equipped with a GPU that supports CUDA version 10 or higher and at least 2 GB of RAM. It has been tested on NVIDIA V100 SXM2. For GPUs with CUDA versions below 10, you will need to adjust the PyTorch and CUDA versions specified in the [environment.yml](environment.yml) file

- We’ll use conda to manage dependencies and configure the environment on an NVIDIA GPU-enabled system.

- It’s recommended to install Miniconda using the official [installer](https://docs.conda.io/projects/miniconda/en/latest/miniconda-other-installer-links.html).
- Once conda is installed, add [`mamba`](https://mamba.readthedocs.io/en/latest/) to your base environment for faster and more reliable package management.

    ```bash
    conda install mamba -n base -c conda-forge
    ```
- Then create a conda environment and install the dependencies:
    ```bash
    mamba env create -f environment.yml
    ```
    Activate the conda environment with `conda activate pace-env`.
- Alternative:
    ```bash
    mamba env create -n pace-env
    ```
  Install from the requirements.txt file
    ```bash 
    pip install -r requirements.txt
    ```



## ⚙️ Installation

```sh
pip install pace
```

if PyPI installation fails or you need the latest `main` branch commits, you can install from source:

```sh
pip install git+https://github.com/dixitmudit/PACE.git
```
    
## 🧪 Getting Started

### 1. Direct Usage

After placing the `VASP` files of the base and adsorbate in the current working directory, the `main.py` file can be executed as follows:

```bash
  python main.py --model /path/to/your/mace/model.model --metals Fe-Ru Fe-Mo --adsorbates Li2S Li2S2 --device cuda
```

### 2. Example notebook

The following is an example workflow to carry out experiments with the PACE algorithm.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dixitmudit/PACE/blob/main/examples/pace-results.ipynb)

### 3. PACE class implementation 

You can directly import PACE into your current workflow assuming you are using ase and MLIPs

```bash
from pace import PACE
from ase.io import read, write
from mace.calculators import MACECalculator

mace_calc = MACECalculator('/path/to/model/here')
base = read('/path/to/base.vasp')
adsorbate = read('/path/to/base.vasp')


# Setup PACE:
pace = PACE(base=base, adsorbate=adsorbate, division=5, z_levels=[1.35, 1.75]) # z_levels: distance of adsorbate from base in Angstroms

# Screen conformations
results = pace.screen(calculator=mace_calc, fig_save_at='/your/path/here', mlip_optimization=3)
# if mlip_optimization > 0, it will initate mlip optimization of top `input: integer` (by_default: 20) structures.

optmised_structure = results['screened_structures'][0]


```

## 🌈 Acknowledgements

M.D. and S.K. gratefully acknowledge the financial support provided by the CSIR, India, which facilitated the completion of this work. A.M.K.R. acknowledges the Department of Atomic Energy and UM-DAE-Centre for Excellence in Basic Sciences, 

We express our gratitude to the National Supercomputing Mission (NSM) for granting access to the computing resources of the Param Porul HPC System. This system is implemented by C-DAC and is supported by the Ministry of Electronics and Information Technology (MeitY) and the Department of Science and Technology (DST), Government of India.

This code repo is based on several existing repositories and MLIPs:
* [ASE](https://gitlab.com/ase/ase)
* [MACE-MP-0](https://github.com/ACEsuit/mace)
* [CHGNet](https://github.com/CederGroupHub/chgnet/)


## 📝 Citation
If you find our work useful, please consider citing it:

```bibtex
@misc{https://doi.org/10.48550/arxiv.2510.15397,
  doi = {10.48550/ARXIV.2510.15397},
  url = {https://arxiv.org/abs/2510.15397},
  author = {Kumar,  Sahil and R,  Adithya Maurya K and Dixit,  Mudit},
  keywords = {Materials Science (cond-mat.mtrl-sci),  FOS: Physical sciences,  FOS: Physical sciences},
  title = {Unravelling the Catalytic Activity of Dual-Metal Doped N6-Graphene for Sulfur Reduction via Machine Learning-Accelerated First-Principles Calculations},
  publisher = {arXiv},
  year = {2025},
  copyright = {Creative Commons Attribution 4.0 International}
}
```
