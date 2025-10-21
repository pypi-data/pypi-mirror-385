import itertools
from typing import Callable, Optional

import numpy as np
import pandas as pd
from scipy import stats
from ydata_profiling.config import Settings
from ydata_profiling.model.correlations import Auto
from ydata_profiling.model.pandas.discretize_pandas import DiscretizationType, Discretizer


def _cramers_corrected_stat(confusion_matrix: pd.DataFrame, correction: bool) -> float:
    """Calculate the Cramer's V corrected stat for two variables.

    Args:
        confusion_matrix: Crosstab between two variables.
        correction: Should the correction be applied?

    Returns:
        The Cramer's V corrected stat for the two variables.
    """
    # Modified
    if confusion_matrix.empty:
        return 0
    chi2 = stats.chi2_contingency(confusion_matrix, correction=correction)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r = confusion_matrix.shape[0]
    k = confusion_matrix.shape[1] if len(confusion_matrix.shape) > 1 else 1

    # Deal with NaNs later on
    with np.errstate(divide="ignore", invalid="ignore"):
        phi2corr = max(0.0, phi2 - ((k - 1.0) * (r - 1.0)) / (n - 1.0))
        rcorr = r - ((r - 1.0) ** 2.0) / (n - 1.0)
        kcorr = k - ((k - 1.0) ** 2.0) / (n - 1.0)
        rkcorr = min((kcorr - 1.0), (rcorr - 1.0))
        if rkcorr == 0.0:
            corr = 1.0
        else:
            corr = np.sqrt(phi2corr / rkcorr)
    return corr


def _pairwise_spearman(col_1: pd.Series, col_2: pd.Series) -> float:
    return col_1.corr(col_2, method="spearman")


def _pairwise_cramers(col_1: pd.Series, col_2: pd.Series) -> float:
    return _cramers_corrected_stat(pd.crosstab(col_1, col_2), correction=True)


@Auto.compute.register(Settings, pd.DataFrame, dict)
def pandas_auto_compute(
    config: Settings, df: pd.DataFrame, summary: dict
) -> Optional[pd.DataFrame]:
    threshold = config.categorical_maximum_correlation_distinct
    numerical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Numeric", "TimeSeries"} and value["n_distinct"] > 1
    ]
    categorical_columns = [
        key
        for key, value in summary.items()
        if value["type"] in {"Categorical", "Boolean"}
        and 1 < value["n_distinct"] <= threshold
    ]

    if len(numerical_columns + categorical_columns) <= 1:
        return None

    categorical_columns = sorted(categorical_columns)
    df_discretized = Discretizer(
        DiscretizationType.UNIFORM, n_bins=config.correlations["auto"].n_bins
    ).discretize_dataframe(df)
    columns_tested = sorted(numerical_columns + categorical_columns)
    correlation_matrix = pd.DataFrame(
        np.ones((len(columns_tested), len(columns_tested))),
        index=columns_tested,
        columns=columns_tested,
    )
    for col_1_name, col_2_name in itertools.combinations(columns_tested, 2):

        method = (
            _pairwise_spearman
            if col_1_name and col_2_name not in categorical_columns
            else _pairwise_cramers
        )

        def f(col_name: str, method: Callable) -> pd.Series:
            return (
                df_discretized
                if col_name in numerical_columns and method is _pairwise_cramers
                else df
            )

        score = method(
            f(col_1_name, method)[col_1_name], f(
                col_2_name, method)[col_2_name]
        )
        (
            correlation_matrix.loc[col_1_name, col_2_name],
            correlation_matrix.loc[col_2_name, col_1_name],
        ) = (score, score)

    return correlation_matrix
