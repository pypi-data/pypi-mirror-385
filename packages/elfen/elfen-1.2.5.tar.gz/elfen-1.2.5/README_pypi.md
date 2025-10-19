# ELFEN - Efficient Linguistic Feature Extraction for Natural Language Datasets

This Python package provides efficient linguistic feature extraction for text datasets (i.e. datasets with N text instances, in a tabular structure).

For further information, check the [GitHub repository](https://github.com/mmmaurer/elfen) and the [documentation](https://elfen.readthedocs.io)

## Using spacy models

If you want to use the spacy backbone, you will need to download the respective model, e.g. "en_core_web_sm":
 ```bash
 python -m spacy download en_core_web_sm
 ```

## Usage of third-party resources usable in this package
For the full functionality, some external resources are necessary. While most of them are downloaded and located automatically, some have to be loaded manually.

### WordNet features
To use wordnet features, download open multilingual wordnet using:
```bash
python -m wn download omw:1.4
```

Note that for some languages, you will need to install another wordnet collection. For example, for German, you can use the following command:

```bash
python -m wn download odenet:1.4
```

For more information on the available wordnet collections, consult the [wn package documentation](https://wn.readthedocs.io/en/latest/guides/lexicons.html).

### Lexicons
The extraction of psycholinguistic, emotion/lexicon and semantic features relies on third-party resources such as lexicons.
Please refer to the original author's licenses and conditions for usage, and cite them if you use the resources through this package in your analyses.

For an overview which features use which resource, and how to export all third-party resource references in a `bibtex` string, consult the [documentation](https://elfen.readthedocs.io).

## Multiprocessing and limiting the numbers of cores used
The underlying dataframe library, polars, uses all available cores by default.
If you are working on a shared server, you may want to consider limiting the resources available to polars.
To do that, you will have to set the ``POLARS_MAX_THREADS`` variable in your shell, e.g.:

```bash
export POLARS_MAX_THREADS=8
```

## Acknowledgements

While all feature extraction functions in this package are written from scratch, the choice of features in the readability and lexical richness feature areas (partially) follows the [`readability`](https://github.com/andreasvc/readability) and [`lexicalrichness`](https://github.com/LSYS/LexicalRichness) Python packages.

We use the [`wn`](https://github.com/goodmami/wn) Python package to extract Open  Multilingual Wordnet synsets.

## Citation
If you use this package in your work, for now, please cite
```bibtex
@misc{maurer-2025-elfen,
  author = {Maurer, Maximilian},
  title = {ELFEN - Efficient Linguistic Feature Extraction for Natural Language Datasets},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/mmmaurer/elfen}},
}
```