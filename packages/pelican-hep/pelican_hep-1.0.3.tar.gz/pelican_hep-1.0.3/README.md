<div align="center">

## Efficient PELICAN

[![Tests](https://github.com/heidelberg-hepml/pelican/actions/workflows/tests.yaml/badge.svg)](https://github.com/heidelberg-hepml/pelican/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/heidelberg-hepml/pelican/branch/main/graph/badge.svg)](https://codecov.io/gh/heidelberg-hepml/pelican)
[![PyPI version](https://img.shields.io/pypi/v/pelican-hep.svg)](https://pypi.org/project/pelican-hep)
[![pytorch](https://img.shields.io/badge/PyTorch_2.0+-ee4c2c?logo=pytorch&logoColor=white)](https://pytorch.org/get-started/locally/)
[![black](https://img.shields.io/badge/Code%20Style-Black-black.svg?labelColor=gray)](https://black.readthedocs.io/en/stable/)

</div>

This is an efficient reimplementation of the PELICAN architecture. 
PELICAN was first published at the [ML4PS workshop 2022](https://arxiv.org/abs/2211.00454) and on [JHEP](https://arxiv.org/abs/2307.16506).
The official implementation is available on https://github.com/abogatskiy/PELICAN.

This implementation aims to improve efficiency and ease of use. 
For toptagging with batch size 100, we find 8x reduced memory usage and a 3x training speedup compared to the original implementation.
PELICAN can be used as the Frames-Net in [Lorentz Local Canonicalization (LLoCa)](https://github.com/heidelberg-hepml/lloca).

You can read more about this implementation in the [Efficient PELICAN documentation](https://heidelberg-hepml.github.io/pelican/).

## Installation

You can either install the latest release using pip
```
pip install pelican-hep
```
or clone the repository and install the package in dev mode
```
git clone https://github.com/heidelberg-hepml/pelican.git
cd pelican
pip install -e .
```

## How to use PELICAN

Please have a look at the [PELICAN documentation](https://heidelberg-hepml.github.io/pelican/) and our example notebook in `examples/demo.ipynb`.

## Examples

- https://github.com/heidelberg-hepml/lorentz-frames: PELICAN jet taggers and amplitude regressors. A PELICAN tagger based on the official implementation is also included, allowing a fair comparison. Within the LLoCa framework, one can also use PELICAN as the Frames-Net.

Let us know if you use `pelican`, so we can add your repo to the list!

## Citation

If you find this code useful in your research, please cite these papers

```bibtex
@article{Favaro:2025pgz,
   author = "Favaro, Luigi and Gerhartz, Gerrit and Hamprecht, Fred A. and Lippmann, Peter and Pitz, Sebastian and Plehn, Tilman and Qu, Huilin and Spinner, Jonas",
   title = "{Lorentz-Equivariance without Limitations}",
   eprint = "2508.14898",
   archivePrefix = "arXiv",
   primaryClass = "hep-ph",
   month = "8",
   year = "2025"
}
@article{Bogatskiy:2023nnw,
   author = "Bogatskiy, Alexander and Hoffman, Timothy and Miller, David W. and Offermann, Jan T. and Liu, Xiaoyang",
   title = "{Explainable equivariant neural networks for particle physics: PELICAN}",
   eprint = "2307.16506",
   archivePrefix = "arXiv",
   primaryClass = "hep-ph",
   doi = "10.1007/JHEP03(2024)113",
   journal = "JHEP",
   volume = "03",
   pages = "113",
   year = "2024"
}
@article{Bogatskiy:2022czk,
   author = "Bogatskiy, Alexander and Hoffman, Timothy and Miller, David W. and Offermann, Jan T.",
   title = "{PELICAN: Permutation Equivariant and Lorentz Invariant or Covariant Aggregator Network for Particle Physics}",
   eprint = "2211.00454",
   archivePrefix = "arXiv",
   primaryClass = "hep-ph",
   month = "11",
   year = "2022"
}
```