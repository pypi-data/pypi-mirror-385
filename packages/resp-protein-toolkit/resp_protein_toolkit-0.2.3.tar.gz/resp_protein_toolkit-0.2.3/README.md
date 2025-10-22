# resp_protein_toolkit

A toolkit designed to perform some common tasks in protein
engineering, especially encoding protein sequences (in various
formats), assisting in fitting uncertainty-aware models to
data, and using a trained model to search for improved candidates
using a simulated annealing "in silico" directed evolution algorithm
from [Parkinson et al. 2023 (Nature Communications).](https://www.nature.com/articles/s41467-023-36028-8)

### Installation

To install this, run:
```
pip install resp_protein_toolkit
```

Numpy is a required dependency. PyTorch is not *required* but will be
necessary to use the models contained in the package so is strongly
recommended.

### Usage

For usage and general guidelines, see [the docs](https://resp-protein-toolkit.readthedocs.io/en/latest/).


### Citations

If using this toolkit in work intended for publication, please cite:

[Parkinson, J., Hard, R. & Wang, W. The RESP AI model accelerates the identification of tight-binding antibodies.
Nat Commun 14, 454 (2023).](https://doi.org/10.1038/s41467-023-36028-8)
