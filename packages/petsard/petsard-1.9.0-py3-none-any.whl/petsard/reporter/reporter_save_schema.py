"""
ReporterSaveSchema - 輸出指定 source 模組所使用的 schema yaml 檔
"""

import logging
from typing import Any

import yaml

from petsard.exceptions import ConfigError
from petsard.reporter.reporter_base import BaseReporter, RegexPatterns


class ReporterSaveSchema(BaseReporter):
    """
    Schema 輸出報告器

    此 reporter 會根據 source 參數指定的模組，輸出對應的 schema 資訊到 YAML 檔案。
    可用於追蹤和記錄各個處理階段的資料結構變化。
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): 配置字典。
                - method (str): 報告方法（必須為 'SAVE_SCHEMA'）
                - source (str | List[str]): 資料來源模組名稱
                    支援的模組：'Loader', 'Splitter', 'Preprocessor', 'Synthesizer',
                               'Postprocessor', 'Constrainer'
                - output (str, optional): 輸出檔案名稱前綴，預設為 'petsard'
                - yaml_output (bool, optional): 是否輸出 YAML 檔案，預設為 False
                - properties (str | List[str], optional): 要輸出的屬性名稱，預設為所有屬性
                    支援的屬性：'type', 'category', 'dtype', 'nullable', 'unique_count',
                               'min', 'max', 'mean', 'std', 'categories'
                    注意：
                    - 'type': schema 定義的類型（如 'str', 'int', 'float64'）
                    - 'category': schema 中的 category 標記（True/False/None）
                    - 'dtype': 實際 pandas dtype（如 'float64', 'object'）

        Raises:
            ConfigError: 如果配置中缺少 'source' 欄位，或 source/properties 格式不正確
        """
        super().__init__(config)

        # source 應該是字串或字串列表: Union[str, List[str]]
        if "source" not in self.config:
            raise ConfigError("Configuration must include 'source' field")
        elif not isinstance(self.config["source"], str | list) or (
            isinstance(self.config["source"], list)
            and not all(isinstance(item, str) for item in self.config["source"])
        ):
            raise ConfigError("'source' must be a string or list of strings")

        # 將 source 轉換為列表（如果是字串）
        if isinstance(self.config["source"], str):
            self.config["source"] = [self.config["source"]]

        # 處理 properties 參數
        if "properties" in self.config:
            if isinstance(self.config["properties"], str):
                self.config["properties"] = [self.config["properties"]]
            elif not isinstance(self.config["properties"], list) or not all(
                isinstance(item, str) for item in self.config["properties"]
            ):
                raise ConfigError("'properties' must be a string or list of strings")

        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    def create(self, data: dict) -> dict[str, Any]:
        """
        處理資料並提取 schema 資訊

        Args:
            data (dict): 資料字典，由 ReporterOperator.set_input() 生成
                格式參考 BaseReporter._verify_create_input()
                可能包含 'metadata' key，其中包含各模組的 Schema

        Returns:
            dict[str, Any]: 處理後的 schema 資料字典
                key: 完整實驗名稱
                value: Schema 物件
        """
        # 提取並存儲 metadata（如果有）
        if "metadata" in data:
            self._metadata_dict = data.pop("metadata")
            self._logger.debug(
                f"Received metadata for {len(self._metadata_dict)} modules"
            )
        else:
            self._metadata_dict = {}

        # 驗證輸入資料
        self._verify_create_input(data)

        processed_schemas = {}

        # 遍歷所有資料項目
        for full_expt_tuple, df in data.items():
            if df is None:
                continue

            # 檢查最後的模組是否在 source 列表中
            # full_expt_tuple 格式: ('Loader', 'default', 'Preprocessor', 'scaler')
            if len(full_expt_tuple) >= 2:
                last_module = full_expt_tuple[-2]
                last_expt_name = full_expt_tuple[-1]

                # 移除可能的後綴 "_[xxx]" 以匹配 source
                clean_expt_name = RegexPatterns.POSTFIX_REMOVAL.sub("", last_expt_name)

                # 檢查模組名稱或實驗名稱是否在 source 中
                if (
                    last_module in self.config["source"]
                    or clean_expt_name in self.config["source"]
                ):
                    # 生成完整實驗名稱
                    full_expt_name = "_".join(
                        [
                            f"{full_expt_tuple[i]}[{full_expt_tuple[i + 1]}]"
                            for i in range(0, len(full_expt_tuple), 2)
                        ]
                    )
                    processed_schemas[full_expt_name] = df

        self._logger.info(f"已處理 {len(processed_schemas)} 個模組的 schema 資訊")
        return processed_schemas

    def report(self, processed_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        生成並保存 schema 報告

        預設輸出 CSV 格式（攤平的表格），每個 source 一行
        可選輸出 YAML 格式（yaml_output=True）

        Args:
            processed_data (dict[str, Any] | None): 處理後的資料
                key: 實驗名稱
                value: pandas DataFrame（用於推斷 schema）

        Returns:
            dict[str, Any]: 已保存的 schema 資料
        """
        if not processed_data:
            self._logger.warning("沒有資料可處理，跳過 schema 報告生成")
            return {}

        saved_schemas = {}
        flattened_rows = []

        for expt_name, df in processed_data.items():
            if df is None:
                self._logger.debug(f"跳過空資料: {expt_name}")
                continue

            try:
                # 嘗試獲取對應的 metadata
                metadata = self._get_metadata_for_expt(expt_name)

                # 從 DataFrame 推斷 schema，並傳入 metadata
                schema_dict = self._infer_schema_from_dataframe(df, metadata)
                saved_schemas[expt_name] = schema_dict

                # 攤平整個 source 的 schema 為單一行
                row = self._flatten_source_schema(expt_name, schema_dict)
                flattened_rows.append(row)

                # 可選：保存為 YAML 檔案
                if self.config.get("yaml_output", False):
                    output_filename = f"{self.config['output']}_schema_{expt_name}.yaml"
                    self._save_schema_to_yaml(schema_dict, output_filename)
                    self._logger.info(f"已保存 YAML schema 到 {output_filename}")

            except Exception as e:
                self._logger.error(f"處理 {expt_name} 時發生錯誤: {e}")
                continue

        # 預設輸出：summary CSV（包含 source 名稱在檔名中）
        if flattened_rows:
            import pandas as pd

            df_output = pd.DataFrame(flattened_rows)

            # 生成包含所有 source 模組名稱的檔名（類似 save_data 的做法）
            source_names = "-".join(self.config["source"])
            csv_filename = f"{self.config['output']}_schema_{source_names}_summary.csv"
            df_output.to_csv(csv_filename, index=False, encoding="utf-8")
            self._logger.info(f"已保存 schema summary 到 {csv_filename}")

        return saved_schemas

    def _get_metadata_for_expt(self, expt_name: str):
        """
        獲取實驗名稱對應的 metadata

        Args:
            expt_name: 實驗名稱

        Returns:
            Schema 或 None
        """
        # 從 processed_data 中獲取 metadata（如果 Reporter 有傳遞）
        if hasattr(self, "_metadata_dict"):
            # expt_name 格式: "Loader[default]_Preprocessor[v1]"
            # 需要解析出模組名稱
            if "_" in expt_name:
                parts = expt_name.split("_")
                # 取最後一個模組
                last_module = parts[-1].split("[")[0]
            else:
                last_module = expt_name.split("[")[0]

            return self._metadata_dict.get(last_module)
        return None

    def _infer_schema_from_dataframe(self, df, metadata=None) -> dict[str, Any]:
        """
        從 DataFrame 推斷 schema 結構

        Args:
            df: pandas DataFrame
            metadata: Schema metadata (optional)

        Returns:
            dict: schema 字典，包含欄位資訊
        """
        schema = {"columns": {}, "shape": {"rows": len(df), "columns": len(df.columns)}}

        # 取得要輸出的屬性列表
        properties = self.config.get("properties", None)

        # 為每個欄位記錄資訊
        for col in df.columns:
            col_info = {}

            # 從 metadata 獲取 type 和 category（schema 定義的類型）
            schema_type = None
            schema_category = None
            if (
                metadata
                and hasattr(metadata, "attributes")
                and col in metadata.attributes
            ):
                schema_type = metadata.attributes[col].type
                schema_category = metadata.attributes[col].category

            # 基本屬性
            if properties is None or "type" in properties:
                if schema_type:
                    col_info["type"] = schema_type

            if properties is None or "category" in properties:
                # 輸出 category，即使是 None 或 False 也要顯示
                col_info["category"] = schema_category

            if properties is None or "dtype" in properties:
                col_info["dtype"] = str(df[col].dtype)
            if properties is None or "nullable" in properties:
                col_info["nullable"] = bool(df[col].isna().any())
            if properties is None or "unique_count" in properties:
                col_info["unique_count"] = int(df[col].nunique())

            # 如果是數值型別，添加統計資訊
            if df[col].dtype.kind in "biufc":  # bool, int, unsigned int, float, complex
                # 檢查是否需要任何統計屬性
                stats_needed = (
                    properties is None
                    or "min" in properties
                    or "max" in properties
                    or "mean" in properties
                    or "std" in properties
                )

                if stats_needed and not df[col].isna().all():
                    statistics = {}

                    # 根據資料型別決定統計值的精度
                    if df[col].dtype.kind in "biu":  # bool, int, unsigned int
                        # 整數型別：四捨五入為整數
                        if properties is None or "min" in properties:
                            statistics["min"] = int(round(df[col].min()))
                        if properties is None or "max" in properties:
                            statistics["max"] = int(round(df[col].max()))
                        if properties is None or "mean" in properties:
                            statistics["mean"] = int(round(df[col].mean()))
                        if properties is None or "std" in properties:
                            statistics["std"] = int(round(df[col].std()))
                    else:  # float, complex
                        # 浮點數型別：偵測資料精度並限制小數位數
                        decimal_places = self._detect_decimal_places(df[col])
                        if properties is None or "min" in properties:
                            statistics["min"] = round(
                                float(df[col].min()), decimal_places
                            )
                        if properties is None or "max" in properties:
                            statistics["max"] = round(
                                float(df[col].max()), decimal_places
                            )
                        if properties is None or "mean" in properties:
                            statistics["mean"] = round(
                                float(df[col].mean()), decimal_places
                            )
                        if properties is None or "std" in properties:
                            statistics["std"] = round(
                                float(df[col].std()), decimal_places
                            )

                    if statistics:
                        col_info["statistics"] = statistics
                elif stats_needed:
                    # 全部為 NA 的情況
                    statistics = {}
                    if properties is None or "min" in properties:
                        statistics["min"] = None
                    if properties is None or "max" in properties:
                        statistics["max"] = None
                    if properties is None or "mean" in properties:
                        statistics["mean"] = None
                    if properties is None or "std" in properties:
                        statistics["std"] = None
                    if statistics:
                        col_info["statistics"] = statistics

            # 如果是物件類型（通常是字串），記錄樣本值
            elif (df[col].dtype == "object" or df[col].dtype.name == "category") and (
                properties is None or "categories" in properties
            ):
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 10:  # 只有少量唯一值時才記錄
                    col_info["categories"] = [str(v) for v in unique_values]

            schema["columns"][str(col)] = col_info

        return schema

    def _detect_decimal_places(self, series, max_check: int = 100) -> int:
        """
        偵測浮點數欄位的小數位數

        Args:
            series: pandas Series（浮點數型別）
            max_check: 最多檢查的資料筆數（預設100）

        Returns:
            int: 小數位數（最多6位）
        """
        non_null = series.dropna()
        if len(non_null) == 0:
            return 2  # 預設2位小數

        decimal_places = 0
        # 只檢查前 max_check 個值以提高效率
        for val in non_null.head(max_check):
            # 轉換為字串並檢查小數位數
            val_str = f"{val:.10f}".rstrip("0").rstrip(".")
            if "." in val_str:
                decimal_places = max(decimal_places, len(val_str.split(".")[1]))

        # 限制最多6位小數
        return min(decimal_places, 6) if decimal_places > 0 else 2

    def _save_schema_to_yaml(self, schema_dict: dict, filename: str) -> None:
        """
        將 schema 字典保存為 YAML 檔案

        Args:
            schema_dict: schema 字典
            filename: 輸出檔案名稱
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump(
                    schema_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            self._logger.debug(f"Schema 已寫入檔案: {filename}")
        except Exception as e:
            self._logger.error(f"寫入 YAML 檔案時發生錯誤: {e}")
            raise

    def _flatten_source_schema(self, source: str, schema_dict: dict) -> dict:
        """
        將整個 source 的 schema 攤平為單一 row

        一個 source 變成一行，所有欄位的所有屬性攤平成列
        例如: source, age_dtype, age_nullable, age_min, age_max, income_dtype, ...

        Args:
            source: 來源實驗名稱
            schema_dict: 完整的 schema 字典

        Returns:
            dict: 攤平的 row 資料，source 是第一個欄位
        """
        row = {"source": source}

        # 遍歷所有欄位
        for column_name, column_info in schema_dict["columns"].items():
            # 第一層屬性
            for key, value in column_info.items():
                if key == "statistics" and isinstance(value, dict):
                    # 第二層：statistics (如 min, max, mean)
                    for stat_key, stat_value in value.items():
                        row[f"{column_name}_{stat_key}"] = stat_value
                elif key == "categories" and isinstance(value, list):
                    # 類別值列表，轉為字串
                    row[f"{column_name}_categories"] = "|".join(str(v) for v in value)
                elif not isinstance(value, (dict, list)):
                    # 其他簡單類型 (dtype, nullable, unique_count 等)
                    row[f"{column_name}_{key}"] = value

        return row
