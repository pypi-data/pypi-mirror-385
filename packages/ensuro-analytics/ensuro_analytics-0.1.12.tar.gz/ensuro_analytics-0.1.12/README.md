# Ensuro Analytics Package

## Description

Ensuro's analytics tool suite.

## Modules

`ensuro_analytics`: This module contains the main analytics functions. It is further divided into two submodules:
    - `analytics/`: This module functions to compute standard portfolio metrics (`analytics/portfolio`), Ensuro's accessors for pandas dataframes (`analytics/dataframe`), functions to compute portfolio reviews (`analytics/review`), and functions to compute "financial" etoken metrics (`analytics/etokens`)
    - `download/`: This file contains interfaces to download data from Ensuro's API and BigQuery,
    - `visual/`: This file contains functions to set up plotting libraries according to Ensuro's layout and functions to visualize portfolio metrics.

## Requirements

See the list of requirements in `requirements.txt/`

## Installation

To install the required packages, run the following command:

```
pip install ensuro-analytics
```

## Usage

See the package [notebook](example.ipynb) for the package instructions.

## Contributing

Thank you for your interest in Ensuro! Head over to our [Contributing Guidelines](CONTRIBUTING.md) for instructions on how to sign our Contributors Agreement and get started with
Ensuro!

Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## Authors

- _Luca Mungo_
- _Ludovico Napoli_

## License

The repository and all contributions are licensed under
[APACHE 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please review our [LICENSE](LICENSE) file.
