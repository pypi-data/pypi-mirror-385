import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError


class EvaluationScoreGranularityMap(Enum):
    """
    Mapping of the granularity of evaluation score.
    評估分數粒度映射 Evaluation score granularity mapping
    """

    GLOBAL = auto()
    COLUMNWISE = auto()
    PAIRWISE = auto()
    DETAILS = auto()
    TREE = auto()

    @classmethod
    def map(cls, granularity: str) -> int:
        """
        Get suffixes mapping int value.

        Args:
            granularity (str): The granularity of evaluator score.

        Returns:
            (int): The method code.

        Raises:
            KeyError: If the granularity is not recognized.
        """
        try:
            return cls[granularity.upper()].value
        except KeyError:
            # Fallback for backward compatibility
            if hasattr(cls, granularity.upper()):
                return getattr(cls, granularity.upper()).value
            raise KeyError(f"Unknown granularity: {granularity}") from None


@dataclass
class EvaluatorInputConfig(BaseConfig):
    """
    Configuration for the input data of evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
        data (pd.DataFrame, optional): The data used for evaluation.
        ori (pd.DataFrame, optional): The original data (legacy, use base instead).
        syn (pd.DataFrame, optional): The synthetic data (legacy, use target instead).
        base (pd.DataFrame, optional): The base/reference data for comparison.
        target (pd.DataFrame, optional): The target data to compare against base.
        control (pd.DataFrame, optional): The control data.
        major_key (str, optional): The major key of the data.
    """

    data: pd.DataFrame = None
    ori: pd.DataFrame = None
    syn: pd.DataFrame = None
    base: pd.DataFrame = None
    target: pd.DataFrame = None
    control: pd.DataFrame = None
    major_key: str = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing EvaluatorInputDataConfig")

        # Handle backward compatibility: map base/target to ori/syn if needed
        if self.base is not None and self.ori is None:
            self.ori = self.base
            self._logger.debug("Mapped 'base' to 'ori' for backward compatibility")
        if self.target is not None and self.syn is None:
            self.syn = self.target
            self._logger.debug("Mapped 'target' to 'syn' for backward compatibility")

    def verify_required_inputs(self, required_input_keys: str | list[str]) -> None:
        """
        Verify if the required inputs are provided.

        Args:
            required_input_keys (str | list[str]): The required input keys.

        Raises:
            ConfigError: If the required inputs are not provided.
        """
        error_msg: str = None

        # 1. Check input keys type
        if isinstance(required_input_keys, str):
            required_input_keys = [required_input_keys]

        if "Undefined" in required_input_keys:
            error_msg = "The required inputs are not defined."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # 2. Check if no major_key been given
        if self.major_key is None:
            # Support both legacy (ori/data) and new (base) naming
            valid_major_keys = {"ori", "data", "base"}
            if not set(required_input_keys).intersection(valid_major_keys):
                error_msg = (
                    "There's mulitple keys in input, but no 'ori', 'data', or 'base' for aligning dtypes. "
                    f"Got keys: {required_input_keys}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)
            # Priority: base > ori > data
            if "base" in required_input_keys:
                self.major_key = "base"
            elif "ori" in required_input_keys:
                self.major_key = "ori"
            else:
                self.major_key = "data"

        # 3. Verify input keys
        missing: list[str] = []
        invalid: list[str] = []

        for key in required_input_keys:
            if key not in self.__dict__ or self.__dict__[key] is None:
                missing.append(key)
            elif not isinstance(self.__dict__[key], pd.DataFrame):
                invalid.append(key)

        if missing or invalid:
            error_parts = []
            if missing:
                error_parts.append(f"Missing required inputs: {missing}")
            if invalid:
                error_parts.append(f"Invalid inputs (not DataFrame): {invalid}")

            error_msg = ". ".join(error_parts)
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if len(required_input_keys) > 1:
            reference_data: pd.DataFrame = getattr(self, self.major_key)
            reference_columns: set = set(reference_data.columns)

            # Note: Schema metadata creation removed as it was not being used
            # If needed in the future, use: SchemaMetadater.from_data(reference_data)

            other_keys: list[str] = [
                key for key in required_input_keys if key != self.major_key
            ]

            # 4. Check column difference
            column_mismatches: dict[str, list[str]] = {}
            other_key_columns: list[str] = []
            for other_key in other_keys:
                other_key_columns = set(getattr(self, other_key).columns)

                # Find differences
                missing_cols = reference_columns - other_key_columns
                extra_cols = other_key_columns - reference_columns

                if missing_cols or extra_cols:
                    column_mismatches[other_key] = {
                        "missing": list(missing_cols),
                        "extra": list(extra_cols),
                    }

            if column_mismatches:
                error_msg = (
                    f"Column name mismatch between dataframes: {column_mismatches}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # 5. Check dtype consistency - do not auto-align at evaluator level
            # Data type alignment should be handled at earlier stages (e.g., in Executor)
            dtype_mismatches = {}

            try:
                reference_dtypes = dict(
                    zip(
                        reference_data.columns,
                        reference_data.dtypes.astype(str),
                        strict=True,
                    )
                )
            except ValueError as e:
                error_msg = (
                    f"Data structure inconsistency in reference data '{self.major_key}': "
                    f"columns count ({len(reference_data.columns)}) does not match "
                    f"dtypes count ({len(reference_data.dtypes)}). {str(e)}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

            for other_key in other_keys:
                other_data = getattr(self, other_key)
                try:
                    other_dtypes = dict(
                        zip(
                            other_data.columns,
                            other_data.dtypes.astype(str),
                            strict=True,
                        )
                    )
                except ValueError as e:
                    error_msg = (
                        f"Data structure inconsistency in '{other_key}' data: "
                        f"columns count ({len(other_data.columns)}) does not match "
                        f"dtypes count ({len(other_data.dtypes)}). {str(e)}"
                    )
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg) from e

                mismatched_columns = []
                for col in reference_columns:
                    if reference_dtypes[col] != other_dtypes[col]:
                        mismatched_columns.append(
                            {
                                "column": col,
                                "reference_dtype": reference_dtypes[col],
                                f"{other_key}_dtype": other_dtypes[col],
                            }
                        )

                if mismatched_columns:
                    dtype_mismatches[other_key] = mismatched_columns

            if dtype_mismatches:
                error_msg = (
                    f"Data type mismatches detected between '{self.major_key}' and other datasets. "
                    f"Please ensure data types are aligned before evaluation using Executor or other preprocessing steps. "
                    f"Mismatches: {dtype_mismatches}"
                )
                self._logger.error(error_msg)
                raise ValueError(error_msg)


@dataclass
class EvaluatorScoreConfig(BaseConfig):
    """
    Configuration for the scoring result of evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
    """

    available_scores_granularity: list[str]

    def __post_init__(self):
        super().__post_init__()

        # Check the granularity validity
        for granularity in self.available_scores_granularity:
            try:
                _ = EvaluationScoreGranularityMap.map(granularity)
            except KeyError:
                error_msg: str = f"Non-default granularity '{granularity}' is used."
                self._logger.info(error_msg)

    def _verify_scores_granularity(self, scores: dict[str, Any]) -> None:
        """
        Verify the granularity of the scores.

        Args:
            scores (dict[str, Any]): The scores to be verified.

        Raises:
            ConfigError: If the granularity is not valid.
        """
        error_msg: str = None

        if not isinstance(scores, dict):
            error_msg = "Scores should be a dictionary."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # find out key in scores but not in available_scores_granularity
        unexpected_keys: set = set(scores.keys()) - set(
            self.available_scores_granularity
        )
        # find out key in available_scores_granularity but not in scores
        missing_keys = set(self.available_scores_granularity) - set(scores.keys())

        if unexpected_keys or missing_keys:
            if unexpected_keys:
                error_msg += f"Unexpected granularity levels in scores: {', '.join(unexpected_keys)}. "
            if missing_keys:
                error_msg += (
                    f"Missing granularity levels in scores: {', '.join(missing_keys)}."
                )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)


class BaseEvaluator(ABC):
    """
    Base class for all evaluator/describer engine implementations.
    These engines are used by the main Evaluator/Describer to perform the actual data evaluating.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["Undefined"]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - eval_method (str): The method of how you evaluating data.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): A dictionary containing the configuration settings.
            _impl (Any): The evaluator object.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        if not isinstance(config, dict):
            error_msg: str = "The config parameter must be a dictionary."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if "eval_method" not in config:
            error_msg: str = (
                "The 'eval_method' parameter is required for the synthesizer."
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        self.config: dict = config
        self._impl: Any = None

    @abstractmethod
    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame])
                The dictionary contains necessary information.

                data = {
                    'ori': pd.DataFrame    # Original data used for synthesis
                    'syn': pd.DataFrame    # Synthetic data generated from 'ori'
                    'control: pd.DataFrame # Original data but NOT used for synthesis
                }

                Note:
                    1. Control is required in Anonymeter and MLUtility.
                    2. So it is recommended to split your original data before synthesizing it.
                        (We recommend to use our Splitter!)

        Returns:
            (dict[str, pd.DataFrame]): The evaluated report.
        """
        error_msg: str = "The '_eval' method must be implemented in the derived class."
        self._logger.error(error_msg)
        raise NotImplementedError(error_msg)

    def eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Create the Describer/Evaluator.

        Args:
            data (dict): same as _eval() method.

        Returns:
            (dict[str, pd.DataFrame]): same as _eval() method.
        """
        data_params: EvaluatorInputConfig = EvaluatorInputConfig.from_dict(data)

        # Verify the required inputs
        data_params.verify_required_inputs(self.REQUIRED_INPUT_KEYS)

        merged_config: dict = data_params.get_params(
            param_configs=[
                {attr: {"action": "INCLUDE"}} for attr in self.REQUIRED_INPUT_KEYS
            ]
        )
        self._logger.debug(f"Merged config keys: {list(merged_config.keys())}")

        # Evaluate the data
        self._logger.info(f"Evaluating {self.__class__.__name__}")
        evaluated_report: dict[str, pd.DataFrame] = self._eval(merged_config)
        self._logger.info(f"Successfully evaluating {self.__class__.__name__}")

        return evaluated_report
