import logging
import re
import warnings
from typing import Any

import pandas as pd
from scipy.stats._warnings_errors import FitError
from sdv.metadata import Metadata as SDV_Metadata
from sdv.single_table import (
    CopulaGANSynthesizer,
    CTGANSynthesizer,
    GaussianCopulaSynthesizer,
    TVAESynthesizer,
)
from sdv.single_table.base import BaseSingleTableSynthesizer

from petsard.exceptions import UnableToSynthesizeError, UnsupportedMethodError
from petsard.metadater.metadata import Schema
from petsard.metadater.metadater import SchemaMetadater
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


def schema_to_sdv(schema: Schema) -> dict[str, Any]:
    """轉換 PETsARD Schema 為 SDV (Synthetic Data Vault) 格式

    Args:
        schema: PETsARD Schema 物件

    Returns:
        dict: SDV metadata 格式的字典
    """
    sdv_metadata = {"columns": {}, "METADATA_SPEC_VERSION": "SINGLE_TABLE_V1"}

    for attr_name, attribute in schema.attributes.items():
        sdtype = _map_attribute_to_sdv_type(attribute)
        sdv_metadata["columns"][attr_name] = {"sdtype": sdtype}

    return sdv_metadata


def _map_attribute_to_sdv_type(attribute: Any) -> str:
    """將 PETsARD Attribute 對應到 SDV sdtype

    Args:
        attribute: PETsARD Attribute 物件或 dict

    Returns:
        str: SDV sdtype
    """
    # 處理 dict 和 Attribute 物件兩種情況
    if isinstance(attribute, dict):
        logical_type = attribute.get("logical_type")
        attr_type = attribute.get("type")
    else:
        logical_type = attribute.logical_type
        attr_type = attribute.type

    # 根據邏輯類型優先判斷
    if logical_type:
        logical = logical_type.lower()
        if logical in ["email", "phone"]:
            return "pii"
        elif logical == "category":
            return "categorical"
        elif logical in ["datetime", "date", "time"]:
            return "datetime"

    # 根據資料類型判斷
    if attr_type:
        if "int" in attr_type or "float" in attr_type:
            return "numerical"
        elif "bool" in attr_type:
            return "boolean"
        elif "datetime" in attr_type:
            return "datetime"

    # 預設為分類
    return "categorical"


class SDVSingleTableMap:
    """
    Mapping of SDV.
    """

    COPULAGAN: int = 1
    CTGAN: int = 2
    GAUSSIANCOPULA: int = 3
    TVAE: int = 4

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        # accept both of "sdv-" or "sdv-single_table-" prefix
        return cls.__dict__[re.sub(r"^(sdv-single_table-|sdv-)", "", method).upper()]


class SDVSingleTableSynthesizer(BaseSynthesizer):
    """
    Factory class for SDV synthesizer.
    """

    SDV_SINGLETABLE_MAP: dict[int, BaseSynthesizer] = {
        SDVSingleTableMap.COPULAGAN: CopulaGANSynthesizer,
        SDVSingleTableMap.CTGAN: CTGANSynthesizer,
        SDVSingleTableMap.GAUSSIANCOPULA: GaussianCopulaSynthesizer,
        SDVSingleTableMap.TVAE: TVAESynthesizer,
    }

    def __init__(self, config: dict, metadata: Schema = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (Schema, optional): The metadata object.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _impl (BaseSingleTableSynthesizer): The synthesizer object if metadata is provided.
        """
        super().__init__(config, metadata)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing {self.__class__.__name__} with config: {config}"
        )

        # If metadata is provided, initialize the synthesizer in the init method.
        if metadata is not None:
            self._logger.debug(
                "Metadata provided, initializing synthesizer in __init__"
            )
            # Convert Schema to SDV format using local function
            sdv_metadata_dict = schema_to_sdv(metadata)
            # Create SDV Metadata object from the dictionary
            # Suppress the "No table name was provided" warning and log it instead
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings(
                    "always", message="No table name was provided.*"
                )
                sdv_metadata = SDV_Metadata.load_from_dict(sdv_metadata_dict)
                # Log any warnings as debug messages
                for warning in w:
                    self._logger.debug(f"SDV Metadata: {warning.message}")
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=sdv_metadata
            )
            self._logger.info("Synthesizer initialized with provided metadata")
        else:
            self._logger.debug(
                "No metadata provided, synthesizer will be initialized during fit"
            )

    def _initialize_impl(self, metadata: SDV_Metadata) -> BaseSingleTableSynthesizer:
        """
        Initialize the synthesizer.

        Args:
            metadata (Metadata): The metadata of the data.

        Returns:
            (BaseSingleTableSynthesizer): The SDV synthesizer

        Raises:
            UnsupportedMethodError: If the synthesizer method is not supported.
        """

        self._logger.debug(
            f"Initializing synthesizer with method: {self.config['syn_method']}"
        )
        try:
            method_code = SDVSingleTableMap.map(self.config["syn_method"])
            self._logger.debug(f"Mapped method code: {method_code}")
            synthesizer_class: Any = self.SDV_SINGLETABLE_MAP[method_code]
            self._logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")
        except KeyError:
            error_msg: str = (
                f"Unsupported synthesizer method: {self.config['syn_method']}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from None

        # Prepare initialization parameters
        init_params = {
            "metadata": metadata,
            "enforce_rounding": True,  # Apply to all synthesizer types
        }

        # Add enforce_min_max_values only for TVAE and GaussianCopula
        if method_code in [SDVSingleTableMap.TVAE, SDVSingleTableMap.GAUSSIANCOPULA]:
            init_params["enforce_min_max_values"] = True
            self._logger.debug(
                f"Adding enforce_min_max_values=True for {synthesizer_class.__name__}"
            )

        # catch warnings during synthesizer initialization:
        # "We strongly recommend saving the metadata using 'save_to_json' for replicability in future SDV versions."
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            synthesizer: BaseSingleTableSynthesizer = synthesizer_class(**init_params)

            for warning in w:
                self._logger.debug(f"Warning during fit: {warning.message}")

        self._logger.debug(
            f"Successfully created {synthesizer_class.__name__} instance"
        )
        return synthesizer

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _impl should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.

        Attributes:
            _impl (BaseSingleTableSynthesizer): The synthesizer object been fitted.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't fit the data. See Issue 454.
        """
        self._logger.info(f"Fitting synthesizer with data shape: {data.shape}")

        # If metadata is not provided, initialize the synthesizer in the fit method.
        if not hasattr(self, "_impl") or self._impl is None:
            self._logger.debug("Initializing synthesizer in _fit method")
            # Create Schema from data and convert to SDV metadata
            schema = SchemaMetadater.from_data(data)
            sdv_metadata_dict = schema_to_sdv(schema)
            # Create SDV Metadata object from the dictionary
            # Suppress the "No table name was provided" warning and log it instead
            with warnings.catch_warnings(record=True) as w:
                warnings.filterwarnings(
                    "always", message="No table name was provided.*"
                )
                sdv_metadata = SDV_Metadata.load_from_dict(sdv_metadata_dict)
                # Log any warnings as debug messages
                for warning in w:
                    self._logger.debug(f"SDV Metadata: {warning.message}")
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=sdv_metadata
            )
            self._logger.info("Synthesizer initialized from data")

        try:
            self._logger.debug("Fitting synthesizer with data")
            self._impl.fit(data)
            self._logger.info("Successfully fitted synthesizer with data")
        except FitError as ex:
            error_msg: str = f"The synthesizer couldn't fit the data. FitError: {ex}."
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't synthesize the data.
        """
        num_rows = self.config["sample_num_rows"]
        self._logger.info(f"Sampling {num_rows} rows from synthesizer")

        batch_size: int = None
        if "batch_size" in self.config:
            self._logger.debug(f"Using batch size: {batch_size}")
            batch_size = int(self.config["batch_size"])

        try:
            synthetic_data = self._impl.sample(
                num_rows=num_rows,
                batch_size=batch_size,
            )
            self._logger.info(f"Successfully sampled {len(synthetic_data)} rows")
            self._logger.debug(f"Generated data shape: {synthetic_data.shape}")
            # Precision rounding is now handled by the base class
            return synthetic_data
        except Exception as ex:
            error_msg: str = f"SDV synthesizer couldn't sample the data: {ex}"
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex
