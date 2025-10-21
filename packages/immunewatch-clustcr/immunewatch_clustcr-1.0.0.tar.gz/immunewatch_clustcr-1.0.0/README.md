# ImmuneWatch ClusTCR

A Python interface for rapid clustering of large sets of CDR3 sequences with unknown antigen specificity

A two-step clustering approach that combines the speed of the [Faiss Clustering Library](https://github.com/facebookresearch/faiss) with the accuracy of [Markov Clustering Algorithm](https://micans.org/mcl/)

On a standard machine*, clusTCR can cluster **1 million CDR3 sequences in under 5 minutes**.  
<sub>*Intel(R) Core(TM) i7-10875H CPU @ 2.30GHz, using 8 CPUs</sub>

Compared to other state-of-the-art clustering algorithms ([GLIPH2](http://50.255.35.37:8080/),  [iSMART](https://github.com/s175573/iSMART) and [tcrdist](https://github.com/kmayerb/tcrdist3)), clusTCR shows comparable clustering quality, but provides a steep increase in speed and scalability.  


## [Documentation](https://svalkiers.github.io/clusTCR/) & Install

All of our documentation, installation info and examples can be found in the above link!
To get you started, here's how to install clusTCR

```
$ pip install immunewatch-clustcr
```


## Development Guide

#### Environment

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

#### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=clustcr --cov-report=html
```

#### Build Distribution

```bash
# Install build tool
uv pip install build twine

# Build source and wheel distributions
python -m build

# Check the built distributions
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```


## Cite

**Please cite as:**

Sebastiaan Valkiers, Max Van Houcke, Kris Laukens, Pieter Meysman, ClusTCR: a Python interface for rapid clustering of large sets of CDR3  sequences with unknown antigen specificity, *Bioinformatics*, **2021**;, btab446, https://doi.org/10.1093/bioinformatics/btab446

**Bibtex:**

```
@article{valkiers2021clustcr,
    author = {Valkiers, Sebastiaan and Van Houcke, Max and Laukens, Kris and Meysman, Pieter},
    title = "{ClusTCR: a Python interface for rapid clustering of large sets of CDR3 sequences with unknown antigen specificity}",
    journal = {Bioinformatics},
    year = {2021},
    month = {06},
    issn = {1367-4803},
    doi = {10.1093/bioinformatics/btab446},
    url = {https://doi.org/10.1093/bioinformatics/btab446},
    note = {btab446},
    eprint = {https://academic.oup.com/bioinformatics/advance-article-pdf/doi/10.1093/bioinformatics/btab446/38660282/btab446.pdf},
}
```

