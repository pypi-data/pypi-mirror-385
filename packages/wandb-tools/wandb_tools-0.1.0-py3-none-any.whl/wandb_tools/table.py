"""WandB experiment results table generation module.

This module provides the ResultTable class for creating formatted tables from WandB experiment runs,
with support for filtering, grouping, and customization of metrics display.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import wandb
from pandas.core.groupby import DataFrameGroupBy


class ResultTable:
    """A class for creating experiment result tables from WandB runs.

    This class provides functionality to:
    - Connect to WandB API and retrieve experiment runs
    - Filter runs using MongoDB query syntax
    - Generate basic experiment result tables with automatic hyperparameter grouping
    - Generate multi-setting comparison tables
    - Customize metric display format and hyperparameter grouping
    """

    def __init__(
        self,
        wandb_project: str,
        wandb_entity: Optional[str] = None,
        wandb_api_key: Optional[str] = None,
        wandb_base_url: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        metric_names: Optional[List[str]] = None,
        metric_round_digit: int = 3,
        metric_percentize: Optional[List[str]] = None,
        hparam_exclude: Optional[List[str]] = None,
        hparam_include: Optional[List[str]] = None,
    ):
        """Initialize ResultTable with WandB connection and configuration.

        Args:
            wandb_project: WandB project name
            wandb_entity: WandB entity name. If None, uses WANDB_ENTITY env var or defaults to "sinopac"
            wandb_api_key: WandB API key. If None, uses WANDB_API_KEY env var (required)
            wandb_base_url: WandB base URL. If None, uses WANDB_BASE_URL env var or defaults to "https://api.wandb.ai"
            filters: MongoDB query syntax filters for runs
            metric_names: List of metrics to display. Can include regex patterns
            metric_round_digit: Number of decimal places for metrics
            metric_percentize: List of metrics to convert to percentages. Can include regex patterns
            hparam_exclude: Hyperparameters to exclude from grouping and display in result tables
            hparam_include: Hyperparameters to force include in grouping

        Raises:
            ValueError: If no runs match the filter criteria
        """
        # Set up WandB configuration
        self.wandb_project = wandb_project
        self.wandb_entity = wandb_entity or os.getenv("WANDB_ENTITY", "sinopac")
        self.wandb_base_url = wandb_base_url or os.getenv("WANDB_BASE_URL", "https://api.wandb.ai")

        # Handle API key
        api_key = wandb_api_key or os.getenv("WANDB_API_KEY")
        if not api_key:
            raise ValueError(
                "WandB API key is required. Provide it via wandb_api_key parameter or WANDB_API_KEY environment variable."
            )

        # Initialize WandB API
        os.environ["WANDB_API_KEY"] = api_key
        os.environ["WANDB_BASE_URL"] = self.wandb_base_url
        self.api = wandb.Api()

        # Set up filtering
        self.filters = filters or {}
        # Always add finished state unless explicitly specified
        if "state" not in self.filters:
            self.filters["state"] = "finished"

        # Set up metric configuration
        self.metric_names = metric_names
        self.metric_round_digit = metric_round_digit
        self.metric_percentize = metric_percentize or []

        # Set up hyperparameter configuration
        self.hparam_exclude = hparam_exclude or []
        self.hparam_include = hparam_include or []

        # Load and validate runs
        self.runs = self._load_runs()

    def generate(self) -> pd.DataFrame:
        """Generate basic experiment results table.

        Returns:
            DataFrame with hyperparameter combinations as index and metrics as columns.
            Values are formatted as 'mean ± std' or single values.

        Raises:
            ValueError: If no varying hyperparameters found for grouping
        """
        # Extract data from runs
        df = self._extract_run_data()

        # Get metrics to display
        metrics_to_show = self._filter_metrics(df)

        # Get varying hyperparameters for grouping
        grouping_params = self._get_grouping_hyperparams(df)

        # Group by hyperparameters
        grouped = self._group_runs(df, grouping_params)

        # Build result table
        result_rows = []

        for group_key, group_df in grouped:
            row = {}

            # Add hyperparameter values to row
            if isinstance(group_key, tuple):
                for param_name, param_value in zip(grouping_params, group_key):
                    row[param_name] = param_value
            else:
                row[grouping_params[0]] = group_key

            # Add metrics
            for metric in metrics_to_show:
                col_name = f"summary.{metric}"
                if col_name in group_df.columns:
                    values = group_df[col_name].tolist()
                    row[metric] = self._format_stat_value(values, metric)
                else:
                    row[metric] = "N/A"

            # Add metadata columns
            row["n_runs"] = len(group_df)

            # Always add runtime hours using direct _runtime calculation
            hours_values = self._get_runtime_hours(group_df)
            row["hours"] = self._format_stat_value(hours_values, "hours")

            result_rows.append(row)

        # Create result DataFrame
        result_df = pd.DataFrame(result_rows)

        ## Set index to hyperparameters
        if grouping_params:
            result_df.set_index(grouping_params, inplace=True)
        else:
            result_df.reset_index(drop=True, inplace=True)

        ## Adjust column names for percentized metrics
        renamed_cols = {}
        for col in metrics_to_show:
            if self._need_percentization(col):
                renamed_cols[col] = f"{col}(%)"
        if renamed_cols:
            result_df.rename(columns=renamed_cols, inplace=True)

        return result_df

    def generate_multisetting(self, setting_param: str) -> pd.DataFrame:
        """Generate multi-setting comparison table.

        Args:
            setting_param: Name of hyperparameter to use as column headers (settings)

        Returns:
            DataFrame with multi-level index (hyperparams + metrics) and settings as columns

        Raises:
            ValueError: If setting parameter not found in run configurations
        """
        # Extract data from runs
        df = self._extract_run_data()

        # Check if setting parameter exists
        setting_col = f"config.{setting_param}"
        if setting_col not in df.columns:
            raise ValueError(f"Setting parameter '{setting_param}' not found in run configurations")

        # Get metrics to display
        metrics_to_show = self._filter_metrics(df)

        # Get unique setting values
        setting_values = sorted(df[setting_col].unique())

        # Get varying hyperparameters (excluding the setting parameter)
        all_varying_params = self._get_grouping_hyperparams(df)
        varying_params = [p for p in all_varying_params if p != setting_param]

        # Group by non-setting hyperparameters
        grouped = self._group_runs(df, varying_params)

        # Build result structure
        result_data = {}

        for group_key, group_df in grouped:
            # Create row identifier
            row_id: tuple = group_key

            # For each metric
            for metric in metrics_to_show + ["n_runs", "hours"]:
                # Determine metric column name
                if self._need_percentization(metric):
                    metric_col_name = f"{metric}(%)"  # Rename metrics with percentize suffix
                else:
                    metric_col_name = metric

                # Create metric row index
                metric_row_id = row_id + (metric_col_name,)

                # Initialize row with NaN for all settings
                result_data[metric_row_id] = {setting: "N/A" for setting in setting_values}

                # Calculate average value of each setting for this metric
                setting_avgs = {setting: None for setting in setting_values}

                # For each setting value
                for setting_val in setting_values:
                    setting_df = group_df[group_df[setting_col] == setting_val]

                    if len(setting_df) == 0:
                        continue

                    if metric == "n_runs":
                        values = [len(setting_df)]
                    elif metric == "hours":
                        values = self._get_runtime_hours(setting_df)
                    else:
                        metric_col = f"summary.{metric}"
                        if metric_col in setting_df.columns:
                            values = setting_df[metric_col].tolist()
                        else:
                            continue

                    # Format the values for this setting
                    formatted_val = self._format_stat_value(values, metric)
                    result_data[metric_row_id][setting_val] = formatted_val

                    # Add to overall average calculation
                    if all(pd.notna(v) for v in values):
                        setting_avgs[setting_val] = sum(values) / len(values)

                # Calculate average across all settings
                setting_avgs = list(setting_avgs.values())
                if any(a is None for a in setting_avgs):
                    result_data[metric_row_id]["Avg."] = "N/A"
                else:
                    avg = sum(setting_avgs) / len(setting_avgs)
                    avg_formatted = self._format_stat_value([avg], metric)
                    result_data[metric_row_id]["Avg."] = avg_formatted

        # Convert to DataFrame
        result_df = pd.DataFrame.from_dict(result_data, orient="index")

        # Create proper multi-level index
        index_names = varying_params + ["Metric"]
        result_df.index = pd.MultiIndex.from_tuples(result_df.index, names=index_names)

        # Reorder columns: Avg. first, then settings
        cols = ["Avg."] + setting_values
        result_df = result_df[cols]

        return result_df

    def _load_runs(self) -> List[Any]:
        """Load runs from WandB API with applied filters.

        Returns:
            List of WandB run objects

        Raises:
            ValueError: If failed to load runs from WandB
        """
        # Get runs from API using filters
        runs = list(
            self.api.runs(
                path=f"{self.wandb_entity}/{self.wandb_project}",
                filters=self.filters,
            )
        )

        if not runs:
            raise ValueError(
                f"No runs found matching the filter criteria in project {self.wandb_entity}/{self.wandb_project}"
            )

        # Fix wandb bugs
        for run in runs:
            run.load_full_data()
            if isinstance(run._attrs.get("summaryMetrics", {}), str):
                # Load summaryMetrics from JSON string if necessary
                run._attrs["summaryMetrics"] = json.loads(run._attrs["summaryMetrics"])
            if isinstance(run._attrs.get("config", {}), str):
                # Load config from JSON string if necessary
                run._attrs["config"] = {k: v["value"] for k, v in json.loads(run._attrs["config"]).items()}

        return runs

    def _need_percentization(self, metric_name: str) -> bool:
        """Check if a metric name matches any pattern in metric_percentize using regex fullmatch.

        Args:
            metric_name: The name of the metric to check

        Returns:
            True if the metric name matches any pattern in metric_percentize, False otherwise
        """
        for pattern in self.metric_percentize:
            if re.fullmatch(pattern, metric_name):
                return True
        return False

    def _extract_run_data(self) -> pd.DataFrame:
        """Extract hyperparameters and metrics from runs into a DataFrame.

        Returns:
            DataFrame with run data including config and summary metrics
        """
        data = []

        for run in self.runs:
            row = {}

            # Extract hyperparameters
            for key, value in run.config.items():
                if key.startswith("_"):
                    continue
                # Make sure config value hashable
                if isinstance(value, list):
                    value = str(sorted(value))
                row[f"config.{key}"] = value

            # Extract summary metrics
            for key, value in run.summary.items():
                if not key.startswith("_"):  # Skip internal WandB fields
                    row[f"summary.{key}"] = value

            # Add run metadata
            row["run_id"] = run.id
            row["run_name"] = run.name
            row["state"] = run.state
            row["runtime"] = run.summary["_runtime"]

            data.append(row)

        return pd.DataFrame(data)

    def _get_grouping_hyperparams(self, df: pd.DataFrame) -> List[str]:
        """Identify hyperparameters that vary across runs, respecting exclusions.

        Args:
            df: DataFrame with extracted run data

        Returns:
            List of hyperparameter names that vary across runs, sorted by number of unique values.
            Excludes parameters in hparam_exclude and includes parameters in hparam_include.
        """
        varying_params = []

        for col in df.columns:
            if col.startswith("config."):
                param_name = col[7:]  # Remove 'config.' prefix
                if param_name in self.hparam_exclude:
                    continue

                # Check if this parameter has more than one unique value
                ## Count and check unique values
                unique_vals = df[col].nunique()
                if unique_vals > 1:
                    varying_params.append(param_name)

        # Add force-included parameters
        for param in self.hparam_include:
            if param not in varying_params and f"config.{param}" in df.columns:
                varying_params.append(param)

        # Sort by number of unique values (fewer values first)
        def sort_key(param: str) -> int:
            return df[f"config.{param}"].nunique()

        varying_params.sort(key=sort_key)

        return varying_params

    def _group_runs(
        self,
        df: pd.DataFrame,
        grouping_params: List[str],
    ) -> DataFrameGroupBy | List[tuple[tuple, pd.DataFrame]]:
        """Group runs by specified hyperparameters.

        Args:
            df: DataFrame with extracted run data
            grouping_params: List of hyperparameter names to group by
        Returns:
            Grouped DataFrame object
        """
        if not grouping_params:
            return [(tuple(), df)]
        grouping_cols = [f"config.{param}" for param in grouping_params]
        return df.groupby(grouping_cols)

    def _filter_metrics(self, df: pd.DataFrame) -> List[str]:
        """Get list of metrics to display based on metric_names configuration.

        Args:
            df: DataFrame with extracted run data

        Returns:
            List of metric names to display
        """
        available_metrics = [col[8:] for col in df.columns if col.startswith("summary.")]

        if not self.metric_names:
            return available_metrics

        filtered_metrics = []
        for pattern in self.metric_names:
            # Use regex matching for metric names
            for metric in available_metrics:
                if re.match(pattern, metric) and metric not in filtered_metrics:
                    filtered_metrics.append(metric)

        filtered_metrics = sorted(filtered_metrics)

        return filtered_metrics

    def _get_runtime_hours(self, group_df: pd.DataFrame) -> List[float]:
        """Get runtime in hours for a group of runs.

        Args:
            group_df: DataFrame containing run data for a group

        Returns:
            List of runtime values in hours
        """
        return (group_df.runtime / 3600.0).tolist()

    def _format_stat_value(self, values: List[float], metric_name: str) -> str:
        """Format statistical values (mean ± std or single value) for display.

        Args:
            values: List of numeric values
            metric_name: Name of the metric for formatting rules

        Returns:
            Formatted string representation of the statistics
        """
        # Remove None/NaN values
        if any(pd.isna(v) for v in values):
            return "N/A"

        if len(values) == 1:
            val = values[0]
            if self._need_percentization(metric_name):
                return f"{val * 100:.1f}"
            elif metric_name == "hours":
                return f"{val:.1f}"
            else:
                return f"{val:.{self.metric_round_digit}f}"

        mean_val = np.mean(values)
        std_val = np.std(values, ddof=1)  # Bessel's correction

        if self._need_percentization(metric_name):
            mean_formatted = f"{mean_val * 100:.1f}"
            std_formatted = f"{std_val * 100:.1f}"
        elif metric_name == "hours":
            mean_formatted = f"{mean_val:.1f}"
            std_formatted = f"{std_val:.1f}"
        else:
            mean_formatted = f"{mean_val:.{self.metric_round_digit}f}"
            std_formatted = f"{std_val:.{self.metric_round_digit}f}"

        return f"{mean_formatted} ± {std_formatted}"


def _safe_nunique(values: pd.Series) -> int:
    """Compute the number of unique values in a Series, handling unhashable types.

    Args:
        values: Pandas Series containing the values to evaluate
    Returns:
        Number of unique values
    """
    if isinstance(values[0], list):
        values = values.apply(lambda l: str(sorted(l)))
    return values.nunique()
