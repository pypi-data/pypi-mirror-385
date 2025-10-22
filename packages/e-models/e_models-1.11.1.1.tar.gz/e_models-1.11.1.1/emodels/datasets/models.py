"""
"""
import logging
from functools import partial
from abc import abstractmethod, ABC
from typing import (
    Generator,
    List,
    Protocol,
    Tuple,
    Generic,
    TypeVar,
    Sequence,
    Dict,
    Any,
    Mapping,
    get_args,
    NewType,
    Optional,
    Iterator,
    ClassVar,
)
from dataclasses import dataclass, Field
import collections.abc

import joblib
from scrapy.http import HtmlResponse
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    recall_score,
    precision_score,
    roc_auc_score,
    confusion_matrix,
)
import numpy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sentencepiece import SentencePieceProcessor
from shub_workflow.utils.futils import FSHelper
from shub_workflow.utils import get_project_settings
from typing_extensions import Self

from emodels.datasets.utils import (
    ResponseConverter,
    Filename,
    DatasetFilename,
    CloudDatasetFilename,
    WebsiteSampleData,
    build_sample_data_from_response,
)
from emodels.datasets.tokenizers import (
    extract_dataset_text_from_website_sampledata,
    train_tokenizer,
    load_tokenizer_from_file,
    TokenizerFilename,
)
from emodels.datasets.stypes import DatasetBucket


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ModelFilename(Filename):
    pass


class VectorizerFilename(Filename):
    pass


class LowLevelModelProtocol(Protocol):
    @abstractmethod
    def fit(self, samples: Sequence[Sequence[float]], labels: Sequence[float]):
        ...

    @abstractmethod
    def predict(self, vectorized_samples: Sequence[Sequence[float]]) -> Sequence[float]:
        ...

    @abstractmethod
    def predict_proba(self, vectorized_samples: Sequence[Sequence[float]]) -> Sequence[Sequence[float]]:
        ...


# Sample coming from scraper
RAW_SAMPLE = TypeVar("RAW_SAMPLE", bound=Mapping[str, Any])
# MODEL_SAMPLE: DatasetFilename samples type, used for model sample. It may already contain the features for the model
# training
MODEL_SAMPLE = TypeVar("MODEL_SAMPLE", bound=Mapping[str, Any])
# If RAW_SAMPLE is already a structured object, MODEL_SAMPLE and
# RAW_SAMPLE could be either the same. Otherwise, MODEL_SAMPLE is typically a structured representation of the type
# RAW_SAMPLE (i.e. when RAW_SAMPLE is an HtmlResponse and MODEL_SAMPLE a WebsiteSampleData, which is a dataset
# structure for representing an HtmlResponse)
# In simpler applications, MODEL_SAMPLE can also be the same as VECTORIZER_INPUT TypeVar(see below)

Target = NewType("Target", int)


class DataclassMappingMixin(collections.abc.Mapping):
    """
    A mixin that makes a dataclass behave like a read-only
    Mapping of its own fields.

    It accesses the '__dataclass_fields__' attribute provided
    by the @dataclass decorator.
    """

    __dataclass_fields__: ClassVar[Dict[str, Field]]

    def __getitem__(self, key: str) -> Any:
        """Access a field's value using dictionary syntax."""
        # Check that the key is a real field name
        if key not in self.__dataclass_fields__:
            raise KeyError(f"'{key}' is not a field of this dataclass.")

        # Return the attribute's value
        return getattr(self, key)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the field names."""
        return iter(self.__dataclass_fields__)

    def __len__(self) -> int:
        """Return the number of fields."""
        return len(self.__dataclass_fields__)


@dataclass
class RawDatasetSample(DataclassMappingMixin, Generic[RAW_SAMPLE]):
    payload: RAW_SAMPLE
    dataset_bucket: Optional[DatasetBucket] = None
    target: Optional[Target] = None


@dataclass
class ModelDatasetSample(DataclassMappingMixin, Generic[MODEL_SAMPLE]):
    payload: MODEL_SAMPLE
    dataset_bucket: DatasetBucket
    target: Target


# The vectorizer input. This is typically the features dict in many applications, but in special
# cases, like those with tokenizer, there is an intermediate step that converts MODEL_SAMPLE and RAW_SAMPLE to
# tokens before vectorization. So in cases with tokenizer, it will be a sequence of tokens.
VECTORIZER_INPUT = TypeVar("VECTORIZER_INPUT", contravariant=True)

# So, the data transformation flux alternatives will be as follows:
#
#  Source: Dataset <----- generate_dataset_samples() <----- Samples (sequence of RAW_SAMPLE)
#             |                                                         |
#             |                                                         |
#             E  <------- get_model_sample_from_raw_sample() <----- RAW_SAMPLE
#             |                                      (RAW_SAMPLE and E can eventually be the same type)
#             |
#      get_dataset()
#             |
# pandas.Dataframe, pandas.Series
#             |
# get_features_from_dataframe(), get_features_from_dataframe_row()
#             |                             |
#  Sequence[VECTORIZER_INPUT],      VECTORIZER_INPUT
#             |
#   vectorizer.transform()
#             |
# Sequence[Sequence[float]] (i.e. numpy range 2 darray)


class VectorizerProtocol(Generic[VECTORIZER_INPUT], Protocol):
    @abstractmethod
    def transform(self, vi: Sequence[VECTORIZER_INPUT]) -> Sequence[Sequence[float]]:
        ...

    @abstractmethod
    def fit(self, vi: Sequence[VECTORIZER_INPUT]):
        ...


# Vectorizer class
VECTORIZER = TypeVar("VECTORIZER", bound=VectorizerProtocol)


# low level classifier model type (SVC, RandomForestClassifier, etc)
M = TypeVar("M", bound=LowLevelModelProtocol)


class DatasetsPandas(Generic[MODEL_SAMPLE]):
    X_train: pd.DataFrame
    X_test: pd.Series
    X_validation: pd.Series
    Y_train: pd.DataFrame
    Y_test: pd.Series
    Y_validation: pd.Series

    @classmethod
    def from_datasetfilename(
        cls,
        filename: DatasetFilename[ModelDatasetSample[MODEL_SAMPLE]],
        features: Tuple[str, ...],
    ) -> Self:
        df = pd.read_json(filename, lines=True, compression="gzip")
        df = df['payload'].apply(pd.Series).assign(target=df["target"], dataset_bucket=df["dataset_bucket"])
        df = df[~df["target"].isnull()]

        df_train = df[df.dataset_bucket == "train"].drop("dataset_bucket", axis=1)
        df_test = df[df.dataset_bucket == "test"].drop("dataset_bucket", axis=1)
        df_validation = df[df.dataset_bucket == "validation"].drop("dataset_bucket", axis=1)

        df_X_train = df_train[list(features)]
        df_Y_train = df_train["target"]

        df_X_test = df_test[list(features)]
        df_Y_test = df_test["target"]

        df_X_validation = df_validation[list(features)]
        df_Y_validation = df_validation["target"]

        obj = cls()
        obj.X_train = df_X_train
        obj.X_test = df_X_test
        obj.X_validation = df_X_validation
        obj.Y_train = df_Y_train
        obj.Y_test = df_Y_test
        obj.Y_validation = df_Y_validation

        return obj


class ModelWithDataset(Generic[RAW_SAMPLE, MODEL_SAMPLE], ABC):
    datasets: DatasetsPandas[MODEL_SAMPLE] | None = None

    raw_dataset_source: CloudDatasetFilename[RawDatasetSample[RAW_SAMPLE]]
    scraped_samples: Dict[DatasetBucket, DatasetFilename[RawDatasetSample[RAW_SAMPLE]]] = dict()
    scraped_label: str

    FSHELPER: FSHelper | None = None
    dataset_repository: DatasetFilename[ModelDatasetSample[MODEL_SAMPLE]]
    features: Tuple[str, ...]

    project: str
    _self: Self | None = None

    def __new__(cls):
        """
        Ensure singleton per class
        """
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    @classmethod
    @abstractmethod
    def build_fshelper(cls, settings) -> FSHelper:
        ...

    @classmethod
    def _fshelper(cls) -> FSHelper:
        if cls.FSHELPER is None:
            settings = get_project_settings()
            cls.FSHELPER = cls.build_fshelper(settings)
        return cls.FSHELPER

    @classmethod
    def _check_model_dataset_sample(cls, dsample: ModelDatasetSample[MODEL_SAMPLE], idx: int = 0):
        keys = dsample.keys()
        assert "target" in keys, f"'target' key not in sample #{idx}."
        assert "dataset_bucket" in keys, f"dataset_bucket key not in sample #{idx}."
        bucket = dsample["dataset_bucket"]
        assert bucket in ("train", "test", "validation"), f"Invalid bucket for sample #{idx}: {bucket}"
        cls._check_model_sample(dsample["payload"])

    @classmethod
    def _check_model_sample(cls, sample: MODEL_SAMPLE, idx: int = 0):
        keys = set(sample.keys())
        missing_fields = set(cls.features).difference(keys)
        assert not missing_fields, f"Missing fields in sample #{idx}: {missing_fields}"

    @classmethod
    def _check_raw_dataset_sample(cls, rsample: RawDatasetSample[RAW_SAMPLE], idx: int = 0):
        assert "target" in rsample.keys(), f"'target' key not in sample #{idx}."
        assert "dataset_bucket" in rsample.keys(), f"dataset_bucket key not in sample #{idx}."
        bucket = rsample["dataset_bucket"]
        assert bucket in get_args(DatasetBucket), f"Invalid bucket for sample #{idx}: {bucket}"

    @classmethod
    def load_dataset(cls) -> DatasetsPandas[MODEL_SAMPLE]:
        dataset_local: DatasetFilename[ModelDatasetSample[MODEL_SAMPLE]] = cls.dataset_repository.local(cls.project)

        if cls._fshelper().exists(dataset_local):
            LOGGER.info(f"Found local copy of datasets {dataset_local}.")
        elif cls._fshelper().exists(cls.dataset_repository):
            LOGGER.info("Downloading datasets...")
            cls._fshelper().download_file(cls.dataset_repository, dataset_local)
        else:
            LOGGER.info("Generating datasets...")
            for idx, sample in enumerate(cls.generate_dataset_samples()):
                cls._check_model_dataset_sample(sample, idx)
                dataset_local.append(sample)
            cls._fshelper().upload_file(dataset_local, cls.dataset_repository)
        return DatasetsPandas.from_datasetfilename(dataset_local, cls.features)

    @classmethod
    def get_dataset(cls) -> DatasetsPandas[MODEL_SAMPLE]:
        if cls.datasets is None:
            cls.datasets = cls.load_dataset()
        return cls.datasets

    @classmethod
    def reset_datasets(cls):
        cls.delete_model_files(cls.dataset_repository)
        cls.datasets = None
        if hasattr(cls, "raw_dataset_source"):
            for fname in cls.scraped_samples.values():
                if cls._fshelper().exists(fname):
                    cls._fshelper().rm_file(fname)
                    LOGGER.info(f"Deleted {fname}")

    @classmethod
    def reset(cls):
        cls.reset_datasets()

    @classmethod
    def delete_model_files(cls, repository: Filename):
        for fname in (repository, repository.local(cls.project)):
            if cls._fshelper().exists(fname):
                cls._fshelper().rm_file(fname)
                LOGGER.info(f"Deleted {fname}")

    @classmethod
    def get_row_from_sample(cls, sample: RAW_SAMPLE) -> pd.Series:
        sd: MODEL_SAMPLE = cls.get_model_sample_from_raw_sample(sample)
        return pd.Series(sd)

    @classmethod
    @abstractmethod
    def get_model_sample_from_raw_sample(cls, sample: RAW_SAMPLE) -> MODEL_SAMPLE:
        ...

    @classmethod
    def append_sample(cls, sample: RawDatasetSample[RAW_SAMPLE]):
        """
        Add raw sample to the specified scraped dataset in cls.scraped_samples list.
        """
        cls._check_raw_dataset_sample(sample)
        dsample = dict(sample)
        cls.scraped_samples[dsample["dataset_bucket"]].append(RawDatasetSample(**dsample))

    @classmethod
    def rebalance_samples(cls, bucket: DatasetBucket):
        """
        Rebalance target sample dataset so all labels has similar count, by randomly removing
        excess of samples with same label.
        """

    @classmethod
    def generate_dataset_samples(cls) -> Generator[ModelDatasetSample[MODEL_SAMPLE], None, None]:
        """Generate samples from cls.scraped_samples in order create the dataset repository.
        This dataset must contain sample objects, each object containing
        the features field (as specified by cls.features attribute), 'the target'
        field the field `dataset_bucket`with a value being either "train", "validation" or "test".
        """
        if hasattr(cls, "raw_dataset_source"):
            idx = 0
            # for some reason, mypy is not understanding that raw_dataset_source yields RawDatasetSample
            # so we need to make explicit.
            sample: RawDatasetSample[RAW_SAMPLE]
            for sample in cls.raw_dataset_source:
                cls.append_sample(sample)
                idx += 1
        for bucket, scrapes_dataset in cls.scraped_samples.items():
            for rsample in scrapes_dataset:
                ms = cls.get_model_sample_from_raw_sample(rsample["payload"])
                yield ModelDatasetSample(payload=ms, dataset_bucket=bucket, target=rsample["target"])


class ModelWithVectorizer(
    Generic[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER], ModelWithDataset[RAW_SAMPLE, MODEL_SAMPLE]
):
    vectorizer_repository: VectorizerFilename
    vectorizer: VECTORIZER | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if hasattr(cls, "vectorizer_repository") and cls.vectorizer_repository is not None:
            assert cls.vectorizer is None, "model vectorizer must be initially None when you set vectorizer_repository"

    @classmethod
    @abstractmethod
    def instantiate_vectorizer(cls) -> VECTORIZER:
        ...

    @classmethod
    def load_vectorizer(cls) -> VECTORIZER:
        """
        Called only if cls.vectorizer is None
        """
        if not hasattr(cls, "vectorizer_repository"):
            LOGGER.info("Instantiating no trainable vectorizer")
            return cls.instantiate_vectorizer()

        vectorizer_local: VectorizerFilename = VectorizerFilename(cls.vectorizer_repository).local(cls.project)

        if cls._fshelper().exists(vectorizer_local):
            LOGGER.info(f"Found local copy of vectorizer model {vectorizer_local}.")
        elif cls._fshelper().exists(cls.vectorizer_repository):
            LOGGER.info("Downloading vectorizer model...")
            cls._fshelper().download_file(cls.vectorizer_repository, vectorizer_local)
        else:
            LOGGER.info("Training vectorizer...")
            vectorizer = cls.instantiate_vectorizer()
            datasets = cls.load_dataset()
            vectorizer.fit(tuple(cls.get_features_from_dataframe(datasets.X_train)))
            joblib.dump(vectorizer, vectorizer_local)
            cls._fshelper().upload_file(vectorizer_local, cls.vectorizer_repository)
        return joblib.load(vectorizer_local)

    @classmethod
    def get_vectorizer(cls) -> VECTORIZER:
        if cls.vectorizer is None:
            cls.vectorizer = cls.load_vectorizer()
        return cls.vectorizer

    @classmethod
    def reset(cls):
        if hasattr(cls, "vectorizer_repository"):
            cls.delete_model_files(cls.vectorizer_repository)
        cls.vectorizer = None
        super().reset()

    @classmethod
    @abstractmethod
    def get_features_from_dataframe_row(cls, row: pd.Series) -> Tuple[VECTORIZER_INPUT]:
        """
        The most common implementation is just:

            return (cast(VECTORIZER_INPUT, dict(row)),)

        where you replace VECTORIZER_INPUT bu the corresponding class.
        """

    @classmethod
    def get_features_from_dataframe(cls, df: pd.DataFrame) -> Generator[VECTORIZER_INPUT, None, None]:
        for _, row in df.iterrows():
            yield cls.get_features_from_dataframe_row(row)[0]


class ModelWithTokenizer(ModelWithDataset[RAW_SAMPLE, MODEL_SAMPLE]):
    tokenizer_repository: TokenizerFilename

    tokenizer: SentencePieceProcessor | None = None

    @classmethod
    def load_tokenizer(cls) -> SentencePieceProcessor:
        """
        - If exists a local copy of the tokenizer in the local datasets folder, load it
        - If not, and exist a repository copy of the tokenizer, download to its local copy into the local
          datasets folder, and load it.
        - If not, train the tokenizer using the dataset text, store it into the local dataset folder,
          upload the trained model to the repository, and load it.
        """
        tokenizer_local: TokenizerFilename = TokenizerFilename(cls.tokenizer_repository).local(cls.project)
        if cls._fshelper().exists(tokenizer_local):
            LOGGER.info(f"Found local copy of tokenizer model {tokenizer_local}.")
        elif cls._fshelper().exists(cls.tokenizer_repository):
            LOGGER.info("Downloading tokenizer model...")
            cls._fshelper().download_file(cls.tokenizer_repository, tokenizer_local)
        else:
            LOGGER.info("Training tokenizer model...")
            training_text_filename = Filename("sptokenizer_training_text.txt").local(cls.project)
            cls.load_dataset()
            cls.generate_training_text_filename(training_text_filename)
            train_tokenizer(training_text_filename, tokenizer_local)
            cls._fshelper().upload_file(tokenizer_local, cls.tokenizer_repository)
        return load_tokenizer_from_file(tokenizer_local)

    @classmethod
    @abstractmethod
    def generate_training_text_filename(cls, training_text_filename: Filename):
        ...

    @classmethod
    def get_tokenizer(cls) -> SentencePieceProcessor:
        if cls.tokenizer is None:
            cls.tokenizer = cls.load_tokenizer()
        return cls.tokenizer

    @classmethod
    def reset(cls):
        cls.delete_model_files(cls.tokenizer_repository)
        cls.tokenizer = None
        super().reset()


class ModelWithTfidfVectorizer(
    Generic[RAW_SAMPLE, MODEL_SAMPLE],
    ModelWithVectorizer[RAW_SAMPLE, MODEL_SAMPLE, str, TfidfVectorizer],
    ModelWithTokenizer[RAW_SAMPLE, MODEL_SAMPLE],
):
    vectorizer: TfidfVectorizer | None = None

    @classmethod
    def instantiate_vectorizer(cls) -> TfidfVectorizer:
        return TfidfVectorizer(min_df=10, max_df=0.7, ngram_range=(1, 3))


class ModelWithResponseSamplesTokenizer(ModelWithTfidfVectorizer[HtmlResponse, WebsiteSampleData]):
    converter: ResponseConverter | None = None

    @classmethod
    def get_converter(cls) -> ResponseConverter:
        assert cls.converter is not None, "Response Converter not initialized"
        return cls.converter

    @classmethod
    def generate_training_text_filename(cls, training_text_filename: Filename):
        extract_dataset_text_from_website_sampledata(
            (sample["payload"] for sample in cls.dataset_repository.local(cls.project)),
            training_text_filename,
            cls.get_converter(),
        )

    @classmethod
    def get_features_from_dataframe_row(cls, row: pd.Series) -> Tuple[str]:
        tokenizer = cls.get_tokenizer()
        converter = cls.get_converter()
        text: str = " ".join(converter.response_to_valid_text(row["body"]))
        tokens: List[str] = tokenizer.encode_as_pieces(text)
        return (" ".join(tokens),)

    @classmethod
    def get_model_sample_from_raw_sample(cls, sample: HtmlResponse) -> WebsiteSampleData:
        return build_sample_data_from_response(sample)


class TrainableModel(Generic[RAW_SAMPLE, MODEL_SAMPLE, M], ModelWithDataset[RAW_SAMPLE, MODEL_SAMPLE]):
    model_repository: ModelFilename
    model: M | None = None

    @classmethod
    def load_trained_model(cls) -> M:
        model_local: ModelFilename = ModelFilename(cls.model_repository).local(cls.project)
        if cls._fshelper().exists(model_local):
            LOGGER.info(f"Found local copy of model {model_local}.")
        elif cls._fshelper().exists(cls.model_repository):
            LOGGER.info("Downloading model...")
            cls._fshelper().download_file(cls.model_repository, model_local)
        else:
            LOGGER.info("Training classifier...")
            model = cls.train()
            joblib.dump(model, model_local)
            cls._fshelper().upload_file(model_local, cls.model_repository)
        return joblib.load(model_local)

    @classmethod
    def get_trained_model(cls) -> M:
        if cls.model is None:
            cls.model = cls.load_trained_model()
        return cls.model

    @classmethod
    @abstractmethod
    def train(cls) -> M:
        ...

    @classmethod
    @abstractmethod
    def instance_new_lowlevel_model(cls) -> M:
        ...

    @classmethod
    def reset(cls):
        """Remove datasets and model files, so a retrain will be forced."""
        cls.delete_model_files(cls.model_repository)
        cls.model = None
        super().reset()


class ClassifierModel(
    Generic[RAW_SAMPLE, MODEL_SAMPLE, M],
    TrainableModel[RAW_SAMPLE, MODEL_SAMPLE, M],
    ModelWithDataset[RAW_SAMPLE, MODEL_SAMPLE],
):
    @classmethod
    @abstractmethod
    def classify_from_row(cls, row: pd.Series, proba: int = -1) -> float:
        ...

    @classmethod
    def classify_sample(cls, sample: RAW_SAMPLE, proba: int = -1) -> float:
        row = cls.get_row_from_sample(sample)
        return cls.classify_from_row(row, proba)

    @classmethod
    def predict(cls, df: pd.DataFrame, proba: int = -1) -> pd.Series:
        return df.apply(partial(cls.classify_from_row, proba=proba), axis=1)

    @classmethod
    def predict_from_samples(cls, samples: List[RAW_SAMPLE], proba: int = -1) -> pd.Series:
        df = pd.DataFrame([cls.get_row_from_sample(s) for s in samples])
        return cls.predict(df, proba)

    @classmethod
    def evaluate(cls, proba: int = -1, proba_threshold: float = 0.5):
        def _stat(score_func, target, predicted):
            return str(round(score_func(target, predicted) * 100, 2)) + "%"

        def _print_confusion_matrix(target, predicted):
            cm = confusion_matrix(target, predicted)
            result = f"TN={cm[0, 0]} FP={cm[0, 1]}\n"
            result += f" FN={cm[1, 0]} TP={cm[1, 1]}"
            return result

        datasets = cls.get_dataset()
        predicted = cls.predict(datasets.X_train, proba)
        if proba >= 0:
            predicted = (predicted > proba_threshold).astype(numpy.int64)
        y_train = datasets.Y_train

        print("Train set scores")
        print("----------------")
        print("Recall:", _stat(recall_score, y_train, predicted))
        print("Precision:", _stat(precision_score, y_train, predicted))
        print("Accuracy:", _stat(accuracy_score, y_train, predicted))
        print("Roc Auc:", _stat(roc_auc_score, y_train, predicted))
        print("Confusion matrix:\n", _print_confusion_matrix(y_train, predicted))
        print()

        if not datasets.X_validation.empty:
            predicted = cls.predict(datasets.X_validation, proba)
            if proba >= 0:
                predicted = (predicted > proba_threshold).astype(numpy.int64)
            y_validation = datasets.Y_validation

            print("Validation set scores")
            print("---------------")
            print("Recall:", _stat(recall_score, y_validation, predicted))
            print("Precision:", _stat(precision_score, y_validation, predicted))
            print("Accuracy:", _stat(accuracy_score, y_validation, predicted))
            print("Roc Auc:", _stat(roc_auc_score, y_validation, predicted))
            print("Confusion matrix:\n", _print_confusion_matrix(y_validation, predicted))
            print()

        predicted = cls.predict(datasets.X_test, proba)
        if proba >= 0:
            predicted = (predicted > proba_threshold).astype(numpy.int64)
        y_test = datasets.Y_test

        print("Test set scores")
        print("---------------")
        print("Recall:", _stat(recall_score, y_test, predicted))
        print("Precision:", _stat(precision_score, y_test, predicted))
        print("Accuracy:", _stat(accuracy_score, y_test, predicted))
        print("Roc Auc:", _stat(roc_auc_score, y_test, predicted))
        print("Confusion matrix:\n", _print_confusion_matrix(y_test, predicted))


class ClassifierModelWithVectorizer(
    Generic[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER, M],
    ModelWithVectorizer[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER],
    ClassifierModel[RAW_SAMPLE, MODEL_SAMPLE, M],
    ModelWithDataset[RAW_SAMPLE, MODEL_SAMPLE],
):
    @classmethod
    def get_training_X_features(cls, X_train: pd.DataFrame) -> Sequence[VECTORIZER_INPUT]:
        return list(cls.get_features_from_dataframe(X_train))

    @classmethod
    def train(cls):
        vectorizer: VECTORIZER = cls.get_vectorizer()

        LOGGER.info("Training Random Forest classifier...")
        model: M = cls.instance_new_lowlevel_model()

        datasets = cls.load_dataset()

        features: Sequence[VECTORIZER_INPUT] = cls.get_training_X_features(datasets.X_train)
        vfeatures: Sequence[Sequence[float]] = vectorizer.transform(features)
        model.fit(vfeatures, datasets.Y_train)
        return model

    @classmethod
    def classify_from_row(cls, row: pd.Series, proba: int = -1) -> float:
        row = row[list(cls.features)]
        vectorizer: VECTORIZER = cls.get_vectorizer()
        model: M = cls.get_trained_model()
        X_features: Sequence[VECTORIZER_INPUT] = cls.get_features_from_dataframe_row(row)
        X_transformed: Sequence[Sequence[float]] = vectorizer.transform(X_features)
        if proba >= 0:
            return model.predict_proba(X_transformed)[0][proba]
        return model.predict(X_transformed)[0]


class SVMModelWithVectorizer(
    Generic[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER],
    ClassifierModelWithVectorizer[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER, SVC],
):
    gamma = 0.4
    C = 10
    kernel = "rbf"

    @classmethod
    def instance_new_lowlevel_model(cls) -> SVC:
        return SVC(kernel=cls.kernel, C=cls.C, gamma=cls.gamma)


class SVMModelWithTfidfResponseVectorizer(
    ModelWithResponseSamplesTokenizer,
    SVMModelWithVectorizer[WebsiteSampleData, HtmlResponse, str, TfidfVectorizer],
):
    pass


class RandomForestModelWithVectorizer(
    Generic[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER],
    ClassifierModelWithVectorizer[RAW_SAMPLE, MODEL_SAMPLE, VECTORIZER_INPUT, VECTORIZER, RandomForestClassifier],
):
    estimators = 100

    @classmethod
    def instance_new_lowlevel_model(cls) -> RandomForestClassifier:
        return RandomForestClassifier(n_estimators=cls.estimators)
