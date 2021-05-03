# SCELC Shared Print Scripts

A Pymarc script for processing our Koha catalog exports and preparing data for a consortial shared print agreement. It filters out bib records based on their items status. Items must be in a circulating location such as the Main Stacks and must not be lost or non-circulating for other reasons.

## Setup

Use [pipenv](https://pipenv.pypa.io/en/latest/) to install a Python 3 virtual environment with the necessary dependencies (pymarc).

```sh
> pipenv --three
> pipenv install
> pipenv shell
> python scelc.py koha.mrc # running the script in the virtual env
```

## License

[ECL 2.0](https://opensource.org/licenses/ECL-2.0)
