import warnings
from collections import Counter

import pandas as pd
from scipy.stats import chisquare, ks_2samp


def compute_kstest(real_data, synthetic_data):
    """Compare two continuous columns using a Kolmogorov–Smirnov test.

    Kolmogorov-Smirnov test based metric.
    This function uses the two-sample Kolmogorov–Smirnov test to compare
    the distributions of the two continuous columns using the empirical CDF.
    It returns 1 minus the KS Test D statistic, which indicates the maximum
    distance between the expected CDF and the observed CDF values.
    As a result, the output value is 1.0 if the distributions are identical
    and 0.0 if they are completely different.

    Args:
        real_data (Union[numpy.ndarray, pandas.Series]):
            The values from the real dataset.
        synthetic_data (Union[numpy.ndarray, pandas.Series]):
            The values from the synthetic dataset.
    Returns:
        float:
            1 minus the Kolmogorov–Smirnov D statistic.
    """
    real_data = pd.Series(real_data)
    synthetic_data = pd.Series(synthetic_data)
    statistic, _ = ks_2samp(real_data, synthetic_data)

    return 1.0 - statistic


def get_frequencies(real, synthetic):
    """Get percentual frequencies for each possible real categorical value.

    Given two iterators containing categorical data, this transforms it into
    observed/expected frequencies which can be used for statistical tests. It
    adds a regularization term to handle cases where the synthetic data contains
    values that don't exist in the real data.
    Args:
        real (list):
            A list of hashable objects.
        synthetic (list):
            A list of hashable objects.
    Returns:
        tuple[list, list]:
            The observed and expected frequencies (as a percent).
    """
    f_obs, f_exp = [], []
    real, synthetic = Counter(real), Counter(
        synthetic
    )  # Just counts the values of the recurrent values
    for value in synthetic:
        if value not in real:
            warnings.warn(f"Unexpected value {value} in synthetic data.")
            real[
                value
            ] += 1e-6  # Regularization to prevent NaN. If there are values that actually do not exists

    for value in real:
        f_obs.append(
            synthetic[value] / sum(synthetic.values())
        )  # Calculates the frequencies
        f_exp.append(real[value] / sum(real.values()))

    return f_obs, f_exp


def compute_cstest(real_data, synthetic_data):
    """Compare two discrete columns using a Chi-Squared test.

    This metric uses the Chi-Squared test to compare the distributions
    of the two categorical columns. It returns the resulting p-value so that
    a small value indicates that we can reject the null hypothesis (i.e. and
    suggests that the distributions are different).

    Args:
        real_data (Union[numpy.ndarray, pandas.Series]):
            The values from the real dataset.
        synthetic_data (Union[numpy.ndarray, pandas.Series]):
            The values from the synthetic dataset.
    Returns:
        float:
            The Chi-Squared test p-value
    """
    f_obs, f_exp = get_frequencies(real_data, synthetic_data)
    if len(f_obs) == len(f_exp) == 1:
        pvalue = 1.0
    else:
        _, pvalue = chisquare(f_obs, f_exp)

    return pvalue
