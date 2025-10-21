# SemanticLayerTools

![PyPI](https://img.shields.io/pypi/v/semanticlayertools?label=pypi%20package) [![DH community code review: May 2022](https://img.shields.io/badge/DHCodeReview-May_2022-blue)](https://github.com/DHCodeReview/SemanticLayerTools/pull/1) [![Documentation Status](https://readthedocs.org/projects/semanticlayertools/badge/?version=latest)](https://semanticlayertools.readthedocs.io/en/latest/?badge=latest)

Collects tools to create semantic layers in the socio-epistemic networks framework. Source material can be any structured corpus with metadata of authors, time, and at least one text column.

Documentation is available on [ReadTheDocs](https://semanticlayertools.readthedocs.io/).

Part of the code was reviewed by [Itay Zandbank](https://github.com/zmbq), thank you. 

## Installation

tl;dr Use pip

~~~bash
pip install semanticlayertools
~~~

Consider using a clean virtual environment to keep your main packages separated.
Create a new virtual environment and install the package

~~~bash
python3 -m venv env
source env/bin/activate
pip install semanticlayertools
~~~

To use some sentence embedding utility functions please install with the
`ml` option

~~~bash
pip install semanticlayertools[ml]
~~~


## Testing

Tests can be run by installing the _dev_ requirements and running `tox`.

~~~bash
pip install semanticlayertools[dev]
tox
~~~

## Building documentation

The documentation is build using _sphinx_. Install with the _dev_ option and run

~~~bash
pip install semanticlayertools[dev]
tox -e docs
~~~

## Funding information

The development was part of the research project [ModelSEN](https://modelsen.gea.mpg.de)

> Socio-epistemic networks: Modelling Historical Knowledge Processes,

in Department I of the Max Planck Institute for the History of Science
and funded by the Federal Ministry of Education and Research, Germany (Grant No. 01 UG2131). The work is continued at the Max Planck Institute of Geoanthropology, Jena. 
