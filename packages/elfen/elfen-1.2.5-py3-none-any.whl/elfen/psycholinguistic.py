"""
This module contains functions for calculating psycholinguistic features
from text data.

If you are using this module, please cite the respective sources for the
norms used in the functions. Consult them for more information on the
norms, their collection, and their interpretation in your analyses.

The psycholinguistic features implemented in this module are:

- Abstractness/Concreteness:
    - Average concreteness score
    - Average standard deviation of the concreteness score
    - Number of low concreteness words
    - Number of high concreteness words
    - Number of controversial concreteness words

- Age of Acquisition:
    - Average age of acquisition score
    - Average standard deviation of the age of acquisition score
    - Number of low age of acquisition words
    - Number of high age of acquisition words
    - Number of controversial age of acquisition words

- Word Prevalence:
    - Average prevalence score
    - Number of low prevalence words
    - Number of high prevalence words

- Socialness:
    - Average socialness score
    - Average standard deviation of the socialness score
    - Number of low socialness words
    - Number of high socialness words
    - Number of controversial socialness words

- Iconicity:
    - Average iconicity score
    - Average standard deviation of the iconicity score
    - Number of low iconicity words
    - Number of high iconicity words
    - Number of controversial iconicity words

- Sensorimotor:
    - Average sensorimotor score
    - Average standard deviation of the sensorimotor score
    - Number of low sensorimotor words
    - Number of high sensorimotor words
    - Number of controversial sensorimotor words
"""
import polars as pl
import warnings

from .resource_utils.psycholinguistics import (
    SENSORIMOTOR_VARS
)

from .preprocess import (
    get_lemmas,
)
from .util import (
    filter_lexicon,
)


# ---------------------------------------------------- #
#            Abstractness/Concreteness                 #
# ---------------------------------------------------- #

def load_concreteness_norms(path: str,
                            language: str = "en",
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Loads the concreteness norms dataset.

    Args:
        path (str): The path to the concreteness norms dataset.

    Returns:
        concreteness_norms (pl.DataFrame):
            A Polars DataFrame containing the concreteness norms dataset.
    """
    if language == "en":
        concreteness_norms = pl.read_excel(path)
    elif language == "fr":
        concreteness_norms = pl.read_excel(path, sheet_name="Norms", 
                                           read_options={
                                               "header_row": 1})
        concreteness_norms = concreteness_norms.rename({
            "items": "Word",
            "mean": "Conc.M",
            "sd": "Conc.SD"
        }).select(
            ["Word", "Conc.M", "Conc.SD"]
        )
    elif language == "de":
        concreteness_norms = pl.read_csv(path,
                                         separator="\t",
                                         skip_rows=7,
                                         eol_char="\n",
                                         encoding="latin-1",
                                         ignore_errors=True
                                         )
        concreteness_norms = concreteness_norms.rename({
            "word": "Word",
            "concreteness_mean": "Conc.M",
            "concreteness_sd": "Conc.SD"
        }).select(
            ["Word", "Conc.M", "Conc.SD"]
        )
    elif language == "it":
        concreteness_norms = pl.read_excel(path,
                                           read_options={
                                               "header_row": 1
                                           })
        concreteness_norms = concreteness_norms.rename({
            "Ita_Word": "Word",
            "M_Con": "Conc.M",
            "SD_Con": "Conc.SD"
        }).select(
            ["Word", "Conc.M", "Conc.SD"]
        ).drop_nans()  # Drop last three empty rows

    return concreteness_norms

def filter_concreteness_norms(concreness_norms: pl.DataFrame,
                              words: list,
                              **kwargs: dict[str, str],
                              ) -> pl.DataFrame:
    """
    Filters the concreteness norms dataset by a list of words.

    Args:
        concreness_norms:
            A Polars DataFrame containing the concreteness norms.
        words (list[str]):
            A list of words to filter the concreteness norms dataset.

    Returns:
        filtered_concreteness_norms (pl.DataFrame):
            A Polars DataFrame containing the filtered concreteness norms
            dataset.
    """
    filtered_concreteness_norms = concreness_norms.filter(
        pl.col("Word").is_in(words))
    return filtered_concreteness_norms

def get_avg_concreteness(data: pl.DataFrame,
                         lexicon: pl.DataFrame,
                         backbone: str = 'spacy',
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Calculates the average concreteness score of a text. NaN/Null values
    indicate that no word in the text was found in the concreteness norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame): 
            A Polars DataFrame containing the concreteness norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average concreteness score
            of the text data. The average concreteness score is stored in
            a new column named 'avg_concreteness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Conc.M")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_concreteness")
    )
    if data.filter(pl.col("avg_concreteness").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the concreteness "
            "norms. The average concreteness for these texts is set to NaN."
            "You may want to consider filling NaNs with a specific value."
        )

    return data

def get_avg_sd_concreteness(data: pl.DataFrame,
                             lexicon: pl.DataFrame,
                             backbone: str = 'spacy',
                             **kwargs: dict[str, str],
                             ) -> pl.DataFrame:
    """
    Calculates the average standard deviation of concreteness score of a
    text. NaN/Null values indicate that no word in the text was found in
    the concreteness norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame): 
            A Polars DataFrame containing the concreteness norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average standard deviation
            of concreteness score of the text data.
            The average standard deviation of concreteness score is stored
            in a new column named 'avg_sd_concreteness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Conc.SD")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_sd_concreteness")
    )
    if data.filter(pl.col("avg_sd_concreteness").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the concreteness "
            "norms. The average standard deviation of concreteness for "
            "these texts is set to NaN. You may want to consider filling "
            "NaNs with a specific value."
        )

    return data

def get_n_low_concreteness(data: pl.DataFrame,
                           lexicon: pl.DataFrame,
                           threshold: float = 1.66,
                           backbone: str = 'spacy',
                           **kwargs: dict[str, str],
                           ) -> pl.DataFrame:
    """
    Calculates the number of low concreteness words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the concreteness norms.
        threshold (float): The threshold for the low concreteness words.
                    Defaults to 1.66.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of low concreteness
            words in the text data.
            The number of low concreteness words is stored in a new column
            named 'n_low_concreteness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Conc.M")).filter(
                    pl.col("Conc.M") < threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_low_concreteness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_high_concreteness(data: pl.DataFrame,
                            lexicon: pl.DataFrame,
                            backbone: str = 'spacy',
                            threshold: float = 3.33,
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Calculates the number of high concreteness words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the concreteness norms.
        threshold (float): The threshold for the high concreteness words.
                    Defaults to 3.33.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of high concreteness
            words in the text data.
            The number of high concreteness words is stored in a new
            column named 'n_high_concreteness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Conc.M")).filter(
                    pl.col("Conc.M") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_high_concreteness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_controversial_concreteness(data: pl.DataFrame,
                                     lexicon: pl.DataFrame,
                                     backbone: str = 'spacy',
                                     threshold: float = 2.0,
                                     **kwargs: dict[str, str],
                                     ) -> pl.DataFrame:
    """
    Calculates the number of controversial concreteness words in a text
    (i.e. items with a high standard deviation in the ratings).

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the concreteness norms.
        threshold (float): The threshold for the standard deviation.
                 Defaults to 2.5.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of controversial
            concreteness words in the text data.
            The number of controversial concreteness words is stored in a
            new column named 'n_controversial_concreteness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Conc.SD")).filter(
                    pl.col("Conc.SD") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_controversial_concreteness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

# ---------------------------------------------------- #
#            Age of Acquisition                        #
# ---------------------------------------------------- #

def load_aoa_norms(path: str,
                   language: str = "en",
                   **kwargs: dict[str, str],
                   ) -> pl.DataFrame:
    """
    Loads the age of acquisition norms dataset.

    Args:
        path (str): The path to the age of acquisition norms dataset.

    Returns:
        aoa_norms (pl.DataFrame):
            A Polars DataFrame containing the age of acquisition norms
            dataset.
    """
    if language == "en":
        aoa_norms = pl.read_excel(path)
    elif language == "de":
        aoa_norms = pl.read_excel(path,
                                 read_options={"header_row": 1})
        aoa_norms = aoa_norms.rename({
            "GERMAN ": "Word",
            "M _1": "Rating.Mean",
            "SD ": "Rating.SD"
        }).select(
            ["Word", "Rating.Mean", "Rating.SD"]
        )
    elif language == "it":
        aoa_norms = pl.read_excel(path,
                                  sheet_name="Database")
        aoa_norms = aoa_norms.rename({
            "Ita_Word": "Word",
            "M_AoA": "Rating.Mean",
            "SD_AoA": "Rating.SD"
        }).select(
            ["Word", "Rating.Mean", "Rating.SD"]
        )
        
    return aoa_norms

def get_avg_aoa(data: pl.DataFrame,
                lexicon: pl.DataFrame,
                backbone: str = 'spacy',
                **kwargs: dict[str, str],
                ) -> pl.DataFrame:
    """
    Calculates the average age of acquisition score of a text. NaN/Null
    values indicate that no word in the text was found in the age of
    acquisition norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the age of acquisition norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average age of acquisition
            score of the text data.
            The average age of acquisition score is stored in a new column
            named 'avg_aoa'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Rating.Mean")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_aoa")
    )
    if data.filter(pl.col("avg_aoa").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the age of "
            "acquisition norms. The average age of acquisition for these "
            "texts is set to NaN. You may want to consider filling NaNs "
            "with a specific value."
        )

    return data

def get_avg_sd_aoa(data: pl.DataFrame,
                    lexicon: pl.DataFrame,
                    backbone: str = 'spacy',
                    **kwargs: dict[str, str],
                    ) -> pl.DataFrame:
    """
    Calculates the average standard deviation of age of acquisition score 
    of a text. NaN/Null values indicate that no word in the text was found
    in the age of acquisition norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the age of acquisition norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average standard deviation
            of age of acquisition score of the text data.
            The average standard deviation of age of acquisition score is 
            stored in a new column named 'avg_sd_aoa'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Rating.SD")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_sd_aoa")
    )
    if data.filter(pl.col("avg_sd_aoa").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the age of "
            "acquisition norms. The average standard deviation of age of "
            "acquisition for these texts is set to NaN. You may want to "
            "consider filling NaNs with a specific value."
        )

    return data

def get_n_low_aoa(data: pl.DataFrame,
                  lexicon: pl.DataFrame,
                  backbone: str = 'spacy',
                  threshold: float = 10.0,
                  **kwargs: dict[str, str],
                  ) -> pl.DataFrame:
        """
        Calculates the number of low age of acquisition words in a text.

        Args:
            data (pl.DataFrame):
                A Polars DataFrame containing the text data.
            aoa_norms (pl.DataFrame): 
                A Polars DataFrame containing the age of acquisition norms.
            backbone (str): The NLP library used to process the text data.
                    Either 'spacy' or 'stanza'. 
            threshold (float): The threshold for the low age of acquisition words.
                    Defaults to 10.0.

        Returns:
            data (pl.DataFrame):
                A Polars DataFrame containing the number of low age of
                acquisition words in the text data.
                The number of low age of acquisition words is stored in a
                new column named 'n_low_aoa'.
        """
        if "lemmas" not in data.columns:
            data = get_lemmas(data, backbone=backbone)
        data = data.with_columns(
            pl.col("lemmas").map_elements(
                lambda x: filter_lexicon(lexicon=lexicon,
                                         words=x,
                                         word_column="Word"). \
                    select(pl.col("Rating.Mean")
                           ).filter(pl.col("Rating.Mean") < threshold). \
                        count().item(),
                    return_dtype=pl.Int64).alias("n_low_aoa")
        ).fill_null(0) # If no words are found, set count to 0
    
        return data

def get_n_high_aoa(data: pl.DataFrame,
                   lexicon: pl.DataFrame,
                   threshold: float = 10.0,
                   backbone: str = 'spacy',
                   **kwargs: dict[str, str],
                   ) -> pl.DataFrame:
        """
        Calculates the number of high age of acquisition words in a text.

        Args:
            data (pl.DataFrame): A Polars DataFrame containing the text data.
            lexicon (pl.DataFrame):
                A Polars DataFrame containing the age of acquisition norms.
            threshold (float): The threshold for the high age of acquisition words.
                    Defaults to 10.0.

        Returns:
            data (pl.DataFrame):
                A Polars DataFrame containing the number of high age of
                acquisition words in the text data.
                The number of high age of acquisition words is stored in a new
                column named 'n_high_aoa'.
        """
        if "lemmas" not in data.columns:
            data = get_lemmas(data, backbone=backbone)
        data = data.with_columns(
            pl.col("lemmas").map_elements(
                lambda x: filter_lexicon(lexicon=lexicon,
                                         words=x,
                                         word_column="Word"). \
                    select(pl.col("Rating.Mean")).filter(
                        pl.col("Rating.Mean") > threshold
                        ).count().item(),
                    return_dtype=pl.Int64).alias("n_high_aoa")
        ).fill_null(0) # If no words are found, set count to 0
    
        return data

def get_n_controversial_aoa(data: pl.DataFrame,
                            lexicon: pl.DataFrame,
                            backbone: str = 'spacy',
                            threshold: float = 4.5,
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Calculates the number of controversial age of acquisition words in a
    text (i.e. items with a high standard deviation in the ratings).

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the age of acquisition norms.
        threshold (float): The threshold for the standard deviation.
                 Defaults to 4.5.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame): 
            A Polars DataFrame containing the number of controversial age
            of acquisition words in the text data.
            The number of controversial age of acquisition words is stored
            in a new column named 'n_controversial_aoa'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Rating.SD")).filter(
                    pl.col("Rating.SD") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_controversial_aoa")
    ).fill_null(0) # If no words are found, set count to 0

    return data

# ---------------------------------------------------- #
#                Word Prevalence                       #
# ---------------------------------------------------- #

# Note: Prevalence norms used here do not have a standard deviation column.

def load_prevalence_norms(path: str,
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Loads the word prevalence norms dataset.

    Args:
        path (str): The path to the word prevalence norms dataset.

    Returns:
        prevalence_norms (pl.DataFrame):
            A Polars DataFrame containing the word prevalence norms
            dataset.
    """
    prevalence_norms = pl.read_excel(path)

    return prevalence_norms

def get_avg_prevalence(data: pl.DataFrame,
                       lexicon: pl.DataFrame,
                       backbone: str = 'spacy',
                       **kwargs: dict[str, str],
                       ) -> pl.DataFrame:
    """
    Calculates the average prevalence score of a text. NaN/Null values
    indicate that no word in the text was found in the prevalence norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        prevalence_norms (pl.DataFrame):
            A Polars DataFrame containing the word prevalence norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average prevalence score
            of the text data. The average prevalence score is stored in a 
            new column named 'avg_prevalence'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Prevalence")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_prevalence")
    )
    if data.filter(pl.col("avg_prevalence").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the prevalence "
            "norms. The average prevalence for these texts is set to NaN."
            "You may want to consider filling NaNs with a specific value."
        )

    return data              

def get_n_low_prevalence(data: pl.DataFrame,
                         lexicon: pl.DataFrame,
                         threshold: float = 1.0,
                         backbone: str = 'spacy',
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Calculate the number of low prevalence words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the word prevalence norms.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of low prevalence
            words in the text data. The number of low prevalence words is 
            stored in a new column named 'n_low_prevalence'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Prevalence")).filter(
                    pl.col("Prevalence") < threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_low_prevalence")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_high_prevalence(data: pl.DataFrame,
                          lexicon: pl.DataFrame,
                          backbone: str = 'spacy',
                          threshold: float = 1.0,
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Calculate the number of high prevalence words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicons: A Polars DataFrame containing the word prevalence norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        threshold (float): The threshold for the high prevalence words.
                    Defaults to 1.0.

    Returns:
        data (pl.DataFrame): 
            A Polars DataFrame containing the number of high prevalence
            words in the text data.
            The number of high prevalence words is stored in a new column 
            named 'n_high_prevalence'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Prevalence")).filter(
                    pl.col("Prevalence") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_high_prevalence")
    ).fill_null(0) # If no words are found, set count to 0

    return data

# ---------------------------------------------------- #
#                Socialness Norms                      #
# ---------------------------------------------------- #

def load_socialness_norms(path: str,
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Loads the socialness norms dataset.

    Args:
        path (str): The path to the socialness norms dataset.

    Returns:
        socialness_norms (pl.DataFrame): 
            A Polars DataFrame containing the socialness norms dataset.
    """
    socialness_norms = pl.read_csv(path)

    return socialness_norms

def get_avg_socialness(data: pl.DataFrame,
                       lexicon: pl.DataFrame,
                       backbone: str = 'spacy',
                       **kwargs: dict[str, str],
                       ) -> pl.DataFrame:
    """
    Calculates the average socialness score of a text. NaN/Null values
    indicate that no word in the text was found in the socialness norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the socialness norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average socialness score
            of the text data. The average socialness score is stored in a 
            new column named 'avg_socialness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Mean")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_socialness")
    )
    if data.filter(pl.col("avg_socialness").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the socialness "
            "norms. The average socialness for these texts is set to NaN."
            "You may want to consider filling NaNs with a specific value."
        )

    return data

def get_avg_sd_socialness(data: pl.DataFrame,
                          lexicon: pl.DataFrame,
                          backbone: str = 'spacy',
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Calculates the average standard deviation of socialness score of a
    text. NaN/Null values indicate that no word in the text was found in
    the socialness norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the socialness norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average standard deviation
            of socialness score of the text data.
            The average standard deviation of socialness score is stored
            in a new column named 'avg_sd_socialness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("SD")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_sd_socialness")
    )
    if data.filter(pl.col("avg_sd_socialness").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the socialness "
            "norms. The average standard deviation of socialness for these "
            "texts is set to NaN. You may want to consider filling NaNs "
            "with a specific value."
        )

    return data

def get_n_low_socialness(data: pl.DataFrame,
                         lexicon: pl.DataFrame,
                         threshold: float = 2.33,
                         backbone: str = 'spacy',
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Calculates the number of low socialness words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the socialness norms.
        threshold (float): The threshold for the low socialness words.
                    Defaults to 1.66.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of low socialness
            words in the text data. The number of low socialness words is 
            stored in a new column named 'n_low_socialness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Mean")).filter(
                    pl.col("Mean") < threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_low_socialness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_high_socialness(data: pl.DataFrame,
                          lexicon: pl.DataFrame,
                          backbone: str = 'spacy',
                          threshold: float = 3.66,
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Calculates the number of high socialness words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the socialness norms.
        threshold (float): The threshold for the high socialness words.
                    Defaults to 3.66.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of high socialness
            words in the text data. The number of high socialness words is
            stored in a new column named 'n_high_socialness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("Mean")).filter(
                    pl.col("Mean") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_high_socialness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_controversial_socialness(data: pl.DataFrame,
                                   lexicon: pl.DataFrame,
                                   backbone: str = 'spacy',
                                   threshold: float = 2.0,
                                   **kwargs: dict[str, str],
                                   ) -> pl.DataFrame:
    """
    Calculates the number of controversial socialness words in a text
    (i.e. items with a high standard deviation in the ratings).

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame): 
            A Polars DataFrame containing the socialness norms.
        threshold (float): The threshold for the standard deviation.
                 Defaults to 2.0.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of controversial
            socialness words in the text data.
            The number of controversial socialness words is stored in a
            new column named 'n_controversial_socialness'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="Word"). \
                select(pl.col("SD")).filter(pl.col("SD") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_controversial_socialness")
    ).fill_null(0) # If no words are found, set count to 0

    return data

# ---------------------------------------------------- #
#                      Iconicity                       #
# ---------------------------------------------------- #

def load_iconicity_norms(path: str,
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Loads the iconicity norms dataset.

    Args:
        path (str): The path to the iconicity norms dataset.

    Returns:
        iconicity_norms (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms dataset.
    """
    iconicity_norms = pl.read_csv(path)
    return iconicity_norms

def get_avg_iconicity(data: pl.DataFrame,
                        lexicon: pl.DataFrame,
                        backbone: str = 'spacy',
                        **kwargs: dict[str, str],
                        ) -> pl.DataFrame:
    """
    Calculates the average iconicity score of a text. NaN/Null values
    indicate that no word in the text was found in the iconicity norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average iconicity score
            of the text data. The average iconicity score is stored in a
            new column named 'avg_iconicity'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="word"). \
                select(pl.col("rating")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_iconicity")
    )
    if data.filter(pl.col("avg_iconicity").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the iconicity "
            "norms. The average iconicity for these texts is set to NaN."
            "You may want to consider filling NaNs with a specific value."
        )

    return data

def get_avg_sd_iconicity(data: pl.DataFrame,
                          lexicon: pl.DataFrame,
                          backbone: str = 'spacy',
                          **kwargs: dict[str, str],
                          ) -> pl.DataFrame:
    """
    Calculates the average standard deviation of iconicity score of a text.
    NaN/Null values indicate that no word in the text was found in the
    iconicity norms.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average standard deviation
            of iconicity score of the text data.
            The average standard deviation of iconicity score is stored in
            a new column named 'avg_sd_iconicity'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="word"). \
                select(pl.col("rating_sd")).mean().item(),
                return_dtype=pl.Float64
                ).alias("avg_sd_iconicity")
    )
    if data.filter(pl.col("avg_sd_iconicity").is_nan()).shape[0] > 0:
        warnings.warn(
            "Some texts do not contain any words from the iconicity "
            "norms. The average standard deviation of iconicity for these "
            "texts is set to NaN."
        )

    return data

def get_n_low_iconicity(data: pl.DataFrame,
                        lexicon: pl.DataFrame,
                        threshold: float = 2.33,
                        backbone: str = 'spacy',
                        **kwargs: dict[str, str],
                        ) -> pl.DataFrame:
    """
    Calculates the number of low iconicity words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms.
        threshold (float): The threshold for the low iconicity words.
                    Defaults to 2.33.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of low iconicity
            words in the text data. The number of low iconicity words is
            stored in a new column named 'n_low_iconicity'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="word"). \
                select(pl.col("rating")).filter(
                    pl.col("rating") < threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_low_iconicity")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_high_iconicity(data: pl.DataFrame,
                         lexicon: pl.DataFrame,
                         backbone: str = 'spacy',
                         threshold: float = 3.66,
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Calculates the number of high iconicity words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms.
        threshold (float): The threshold for the high iconicity words.
                    Defaults to 3.66.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of high iconicity
            words in the text data.
            The number of high iconicity words is stored in a new column
            named 'n_high_iconicity'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="word"). \
                select(pl.col("rating")).filter(
                    pl.col("rating") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_high_iconicity")
    ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_controversial_iconicity(data: pl.DataFrame,
                                  lexicon: pl.DataFrame,
                                  backbone: str = 'spacy',
                                  threshold: float = 2.5,
                                  **kwargs: dict[str, str],
                                  ) -> pl.DataFrame:
    """
    Calculates the number of controversial iconicity words in a text
    (i.e. items with a high standard deviation in the ratings).

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the iconicity norms.
        threshold (float): The threshold for the standard deviation.
                 Defaults to 2.5.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of controversial
            iconicity words in the text data.
            The number of controversial iconicity words is stored in a new
            column named 'n_controversial_iconicity'.
    """
    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    data = data.with_columns(
        pl.col("lemmas").map_elements(
            lambda x: filter_lexicon(lexicon=lexicon,
                                     words=x,
                                     word_column="word"). \
                select(pl.col("rating_sd")).filter(
                    pl.col("rating_sd") > threshold). \
                    count().item(),
                return_dtype=pl.Int64).alias("n_controversial_iconicity")
    ).fill_null(0) # If no words are found, set count to 0

    return data

# ---------------------------------------------------- #
#                   Sensorimotor                       #
# ---------------------------------------------------- #

def load_sensorimotor_norms(path: str,
                            language: str = "en",
                            sensorimotor_vars: list[str] = SENSORIMOTOR_VARS,
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Loads the sensorimotor norms dataset.

    Args:
        path (str): The path to the sensorimotor norms dataset.

    Returns:
        sensorimotor_norms (pl.DataFrame):
            A Polars DataFrame containing the sensorimotor norms dataset.
    """
    if language == "en":
        sensorimotor_norms = pl.read_excel(path)
        # the lancaster sensorimotor norms have all caps lemmas, so we con-
        # vert them to lowercase for consistency
        sensorimotor_norms = sensorimotor_norms.with_columns(
            pl.col("Word").str.to_lowercase().alias("Word")
        )
    elif language == "it":
        sensorimotor_norms = pl.read_csv(
            path,
            separator=" ",
            quote_char='"',
            encoding="latin-1"
        ).rename({
            "Ita_Word": "Word"
        }).select(
            ["Word"] + sensorimotor_vars[language]
        ).rename({ # rename columns to match the English norms
            var: f"{var}.mean" for var in sensorimotor_vars[language]
        })
    elif language == "fr":
        pass # TODO: add French sensorimotor norms

    return sensorimotor_norms

def get_avg_sensorimotor(data: pl.DataFrame,
                         lexicon: pl.DataFrame,
                         backbone: str = 'spacy',
                         sensorimotor_vars: list[str] = SENSORIMOTOR_VARS,
                         language: str = "en",
                         **kwargs: dict[str, str],
                         ) -> pl.DataFrame:
    """
    Calculates the average sensorimotor variable score of a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the sensorimotor norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        sensorimotor_vars (list[str]):
            A list of sensorimotor variables to calculate the average
            score for. Defaults to SENSORIMOTOR_VARS.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the average sensorimotor score
            of the text data.
            The average sensorimotor score is stored in a new column named
            'avg_sensorimotor'.
    """
    sensorimotor_vars = sensorimotor_vars[language]

    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    for var in sensorimotor_vars:
        data = data.with_columns(
            pl.col("lemmas").map_elements(
                lambda x: filter_lexicon(lexicon=lexicon,
                                         words=x,
                                         word_column="Word"). \
                    select(pl.col(f"{var}.mean")).mean().item(),
                    return_dtype=pl.Float64
                    ).alias(f"avg_{var}_sensorimotor")
        )
    for var in sensorimotor_vars:
        if data.filter(pl.col(f"avg_{var}_sensorimotor").is_nan()).shape[0] > 0:
            warnings.warn(
                f"Some texts do not contain any words from the {var} "
                "sensorimotor norms. The average sensorimotor score for "
                "these texts is set to NaN."
            )

    return data

def get_avg_sd_sensorimotor(data: pl.DataFrame,
                            lexicon: pl.DataFrame,
                            backbone: str = 'spacy',
                            sensorimotor_vars: list[str] = \
                                SENSORIMOTOR_VARS,
                            language: str = "en",
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Calculates the average standard deviation of sensorimotor variable
    score of a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the sensorimotor norms.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        sensorimotor_vars (list[str]):
            A list of sensorimotor variables to calculate the average
            standard deviation for.
    
    Returns:
        data (pl.DataFrame): A Polars DataFrame containing the average
            standard deviation of sensorimotor variable score of the text
            data. The average standard deviation of sensorimotor variable 
            score is stored in new columns named 'avg_sd_{var}' where
            {var} is the sensorimotor variable.
    """
    sensorimotor_vars = sensorimotor_vars[language]

    if language == "en":
        if "lemmas" not in data.columns:
            data = get_lemmas(data, backbone=backbone)
        
        for var in sensorimotor_vars:
            data = data.with_columns(
                pl.col("lemmas").map_elements(
                    lambda x: filter_lexicon(lexicon=lexicon,
                                            words=x,
                                            word_column="Word"). \
                        select(pl.col(f"{var}.SD")).mean().item(),
                        return_dtype=pl.Float64
                        ).alias(f"avg_sd_{var}_sensorimotor")
            )
            if data.filter(
                pl.col(f"avg_sd_{var}_sensorimotor").is_nan()
                           ).shape[0] > 0:
                warnings.warn(
                    f"Some texts do not contain any words from the {var} "
                    "sensorimotor norms. The average standard deviation "
                    f"of {var} for these texts is set to NaN. You may want "
                    "to consider filling NaNs with a specific value."
                )
    else:
        # warning, other languages do not have a standard deviation
        # column in the sensorimotor norms, so we return the same
        # dataframe without any changes
        warnings.warn(
            "Sensorimotor norms for languages other than English do not "
            "have a standard deviation column. Returning the same dataframe "
            "without any changes."
        )
    
    return data

def get_n_low_sensorimotor(data: pl.DataFrame,
                           lexicon: pl.DataFrame,
                           threshold: float = 2.33,
                           backbone: str = 'spacy',
                           sensorimotor_vars: list[str] = \
                            SENSORIMOTOR_VARS,
                           language: str = "en",
                           **kwargs: dict[str, str],
                           ) -> pl.DataFrame:
    """
    Calculates the number of low-rating sensorimotor words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the sensorimotor norms.
        threshold (float): The threshold for the low-rating sensorimotor words.
                    Defaults to 2.33.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        sensorimotor_vars (list[str]):
            A list of sensorimotor variables to calculate the number of
            low-rating words for. Defaults to SENSORIMOTOR_VARS.

    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of low-rating
            sensorimotor words in the text data.
            The number of low-rating sensorimotor words is stored in new
            columns named 'n_low_{var}' where {var} is the sensorimotor
            variable.
    """
    sensorimotor_vars = sensorimotor_vars[language]

    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    
    for var in sensorimotor_vars:
        data = data.with_columns(
            pl.col("lemmas").map_elements(
                lambda x: filter_lexicon(lexicon=lexicon,
                                         words=x,
                                         word_column="Word"). \
                    select(pl.col(f"{var}.mean")).filter(
                        pl.col(f"{var}.mean") < threshold). \
                        count().item(),
                    return_dtype=pl.Int64).alias(f"n_low_{var}"
                                                 "_sensorimotor")
        ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_high_sensorimotor(data: pl.DataFrame,
                            lexicon: pl.DataFrame,
                            backbone: str = 'spacy',
                            threshold: float = 3.66,
                            sensorimotor_vars: list[str] = \
                                SENSORIMOTOR_VARS,
                            language: str = "en",
                            **kwargs: dict[str, str],
                            ) -> pl.DataFrame:
    """
    Calculates the number of high-rating sensorimotor words in a text.

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame):
            A Polars DataFrame containing the sensorimotor norms.
        threshold (float): The threshold for the high-rating sensorimotor words.
                    Defaults to 3.66.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        sensorimotor_vars (list[str]):
            A list of sensorimotor variables to calculate the
            number of high-rating words for.
            Defaults to SENSORIMOTOR_VARS.
    
    Returns:
        data (pl.DataFrame): 
            A Polars DataFrame containing the number of high-rating
            sensorimotor words in the text data.
            The number of high-rating sensorimotor words is stored in new 
            columns named 'n_high_{var}' where {var} is the sensorimotor
            variable.
    """
    sensorimotor_vars = sensorimotor_vars[language]

    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)
    
    for var in sensorimotor_vars:
        data = data.with_columns(
            pl.col("lemmas").map_elements(
                lambda x: filter_lexicon(lexicon=lexicon,
                                         words=x,
                                         word_column="Word"). \
                    select(pl.col(f"{var}.mean")).filter(
                        pl.col(f"{var}.mean") > threshold). \
                        count().item(),
                    return_dtype=pl.Int64).alias(f"n_high_{var}"
                                                 "_sensorimotor")
        ).fill_null(0) # If no words are found, set count to 0

    return data

def get_n_controversial_sensorimotor(data: pl.DataFrame,
                                     lexicon: pl.DataFrame,
                                     backbone: str = 'spacy',
                                     threshold: float = 2.0,
                                     sensorimotor_vars: list[str] = \
                                        SENSORIMOTOR_VARS,
                                     language: str = "en",
                                     **kwargs: dict[str, str],
                                     ) -> pl.DataFrame:
    """
    Calculates the number of controversial sensorimotor words in a text
    (i.e. items with a high standard deviation in the ratings).

    Args:
        data (pl.DataFrame): A Polars DataFrame containing the text data.
        lexicon (pl.DataFrame): 
            A Polars DataFrame containing the sensorimotor norms.
        threshold (float): The threshold for the standard deviation.
                 Defaults to 2.0.
        backbone (str): The NLP library used to process the text data.
                Either 'spacy' or 'stanza'.
        sensorimotor_vars (list[str]):
            A list of sensorimotor variables to calculate the
            number of controversial words for.
    
    Returns:
        data (pl.DataFrame):
            A Polars DataFrame containing the number of controversial
            sensorimotor words in the text data.
            The number of controversial sensorimotor words is stored in
            new columns named 'n_controversial_{var}' where {var} is the
            sensorimotor variable.
    """
    sensorimotor_vars = sensorimotor_vars[language]

    if "lemmas" not in data.columns:
        data = get_lemmas(data, backbone=backbone)

    if language == "en":
        for var in sensorimotor_vars:
            data = data.with_columns(
                pl.col("lemmas").map_elements(
                    lambda x: filter_lexicon(lexicon=lexicon,
                                            words=x,
                                            word_column="Word"). \
                        select(pl.col(f"{var}.SD")).filter(
                            pl.col(f"{var}.SD") > threshold). \
                            count().item(),
                        return_dtype=pl.Int64).alias(f"n_controversial_{var}"
                                                    "_sensorimotor")
            )
    else:
        # warning, other languages do not have a standard deviation
        # column in the sensorimotor norms, so we return the same
        # dataframe without any changes
        warnings.warn(
            "Sensorimotor norms for languages other than English do not "
            "have a standard deviation column. Returning the same dataframe "
            "without any changes."
        )

    return data

