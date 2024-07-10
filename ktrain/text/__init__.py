import pickle

from . import shallownlp, textutils
from .data import texts_from_array, texts_from_csv, texts_from_df, texts_from_folder
from .eda import get_topic_model
from .models import (
    print_text_classifiers,
    print_text_regression_models,
    text_classifier,
    text_regression_model,
)
from .ner.data import (
    entities_from_array,
    entities_from_conll2003,
    entities_from_df,
    entities_from_gmb,
    entities_from_txt,
)
from .ner.models import print_sequence_taggers, sequence_tagger
from .preprocessor import Transformer, TransformerEmbedding
from .qa import AnswerExtractor, SimpleQA
from .summarization import TransformerSummarizer
from .textextractor import TextExtractor
from .textutils import extract_filenames, filter_by_id, load_text_files
from .translation import EnglishTranslator, Translator
from .zsl import ZeroShotClassifier

__all__ = [
    "text_classifier",
    "text_regression_model",
    "print_text_classifiers",
    "print_text_regression_models",
    "texts_from_folder",
    "texts_from_csv",
    "texts_from_df",
    "texts_from_array",
    "entities_from_gmb",
    "entities_from_conll2003",
    "entities_from_txt",
    "entities_from_array",
    "entities_from_df",
    "sequence_tagger",
    "print_sequence_taggers",
    "get_topic_model",
    "Transformer",
    "TransformerEmbedding",
    "shallownlp",
    "TransformerSummarizer",
    "ZeroShotClassifier",
    "EnglishTranslator",
    "Translator",
    "SimpleQA",
    "AnswerExtractor",
    "TextExtractor",
    "extract_filenames",
    "load_text_files",
]


def load_topic_model(fname):
    """
    Load saved TopicModel object
    Args:
        fname(str): base filename for all saved files
    """
    with open(fname + ".tm_vect", "rb") as f:
        vectorizer = pickle.load(f)
    with open(fname + ".tm_model", "rb") as f:
        model = pickle.load(f)
    with open(fname + ".tm_params", "rb") as f:
        params = pickle.load(f)
    tm = get_topic_model(
        n_topics=params["n_topics"],
        n_features=params["n_features"],
        verbose=params["verbose"],
    )
    tm.model = model
    tm.vectorizer = vectorizer
    return tm


seqlen_stats = Transformer.seqlen_stats
