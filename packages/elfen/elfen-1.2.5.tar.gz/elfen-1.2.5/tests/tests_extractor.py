import pytest
import polars as pl
from elfen import Extractor

@pytest.fixture
def sample_data_en():
    """
    Fixture to provide sample data for testing.
    """
    data = {
        'text': [
            "This is a test sentence.",
            "Another test sentence.",
            "Yet another test sentence."
        ]
    }
    df = pl.DataFrame(data)
    return df

@pytest.fixture
def sample_data_de():
    """
    Fixture to provide sample data for testing in German.
    """
    data = {
        'text': [
            "Dies ist ein Testsatz.",
            "Noch ein Testsatz.",
            "Wieder ein weiterer Testsatz."
        ]
    }
    df = pl.DataFrame(data)
    return df

def test_initialization(sample_data_en):
    """
    Test the initialization of the Extractor class.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    assert extractor.data is not None
    assert 'nlp' in extractor.data.columns

def test_extraction_single_feature(sample_data_en):
    """
    Test the extraction of features from the text data.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    extractor.extract("n_tokens")
    assert 'n_tokens' in extractor.data.columns
    assert len(extractor.data['n_tokens']) == len(sample_data_en)
    assert extractor.data.shape == (3, 3)  # 3 rows, 3 columns (text, nlp, n_tokens)

def test_extraction_multiple_features(sample_data_en):
    """
    Test the extraction of multiple features from the text data.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    extractor.extract(["n_tokens", "n_sentences"])
    assert 'n_tokens' in extractor.data.columns
    assert 'n_sentences' in extractor.data.columns
    assert len(extractor.data['n_tokens']) == len(sample_data_en)
    assert len(extractor.data['n_sentences']) == len(sample_data_en)
    assert extractor.data.shape == (3, 4)  # 3 rows, 4 columns (text, nlp, n_tokens, n_sentences)

def test_extraction_invalid_feature(sample_data_en):
    """
    Test the extraction of an invalid feature from the text data.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    extractor.extract("invalid_feature")
    assert 'invalid_feature' not in extractor.data.columns

def test_initialization_invalid_backbone(sample_data_en):
    """
    Test the extraction with an invalid backbone.
    """
    with pytest.raises(ValueError):
        Extractor(data=sample_data_en,
                  backbone='invalid_backbone',
                  text_column='text',
                  language='en',
                  model='en_core_web_sm')

def test_token_normalization(sample_data_en):
    """
    Test the token normalization feature.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    extractor.extract(["n_tokens", "n_long_words"])
    extractor.token_normalize()
    first_ratio = extractor.data['n_long_words'][0]
    max_tokens = extractor.data['n_tokens'].max()
    # make sure the ratio works as expected
    assert pytest.approx(first_ratio) == 1/6 
    # make sure n_tokens is not normalized
    assert max_tokens == 6

def test_empty_text_warning():
    """
    Test whether a warning is raised for empty texts.
    """
    data = {
        'text': [
            "This is a test sentence.",
            "",
            "Yet another test sentence."
        ]
    }
    df = pl.DataFrame(data)
    with pytest.warns(UserWarning, match="Some texts are empty. "
                      "This can affect the results. "
                      "You may want to remove these rows."):
        Extractor(data=df,
                  backbone='spacy',
                  text_column='text',
                  language='en',
                  model='en_core_web_sm')

def test_full_run_en(sample_data_en):
    """
    Test whether the Extractor runs without errors for English texts.
    """
    extractor = Extractor(data=sample_data_en,
                          backbone='spacy',
                          text_column='text',
                          language='en',
                          model='en_core_web_sm')
    extractor.extract_features()
    assert extractor.data is not None

def test_full_run_de(sample_data_de):
    """
    Test whether the Extractor runs without errors for German texts.
    """
    extractor = Extractor(data=sample_data_de,
                          backbone='spacy',
                          text_column='text',
                          language='de',
                          model='de_core_news_sm')
    extractor.extract_features()
    assert extractor.data is not None

