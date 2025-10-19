from typing import Iterable

import numpy as np

from brtp.math.sampling._deterministic import linspace


# =================================================================================================
#  Regular mean
# =================================================================================================
def mean(values: Iterable[int | float]) -> float:
    """compute arithmetic mean of provided values"""
    values = list(values)
    if len(values) == 0:
        return 0.0
    else:
        return float(np.mean(values))


def weighted_mean(values: Iterable[int | float], weights: Iterable[int | float]) -> float:
    """compute weighted arithmetic mean of provided values"""
    values = list(values)
    weights = list(weights)
    if len(values) == 0:
        return 0.0
    else:
        v = np.array(values)
        w = np.array(weights)
        return float(np.sum(w * v) / np.sum(w))


def ordered_weighted_mean(values: Iterable[int | float], power: float) -> float:
    """
    Compute ordered weighted geometric mean of provided values

    See eg: https://www.sciencedirect.com/science/article/abs/pii/S0020025524001889

    Step-wise procedure:
      - Sort values  (if power < 0, sort in reverse order)
      - Compute weights as w ~ (i+0.5)*abs(p), with i the index into the array
      - Compute weighted mean with these weights

    Depending on the power parameter, the 'center of gravity' of the weights will lie at a different quantile
    of the sorted values.

        power = -3.0        -> 20% quantile
        power = -2.0        -> 25% quantile
        power = -1.0        -> 33% quantile
        power =  0.0        -> 50% quantile (regular mean)
        power =  1.0        -> 66% quantile
        power =  2.0        -> 75% quantile
        power =  3.0        -> 80% quantile

    Hence, the net effect is that we compute the mean of the provided values, with emphasis on the
      larger values (power > 0) or smaller values (power < 0).
    """
    if power == 0:
        return mean(values)
    else:
        values = sorted(list(values), reverse=(power < 0))
        weights = np.array(
            linspace(
                min_value=0.0,
                max_value=1.0,
                n=len(values),
                inclusive=False,  # this makes sure that all weights are strictly positive
            )
        ) ** abs(power)
        return weighted_mean(values, weights)


# =================================================================================================
#  Geometric mean
# =================================================================================================
def geo_mean(values: Iterable[int | float]) -> float:
    """compute geometric mean of provided values"""
    values = list(values)
    if len(values) == 0:
        return 1.0
    if any(v == 0 for v in values):
        return 0.0
    else:
        return float(np.exp(np.mean(np.log(np.array(values)))))


def weighted_geo_mean(values: Iterable[int | float], weights: Iterable[int | float]) -> float:
    """compute weighted geometric mean of provided values"""
    values = list(values)
    weights = list(weights)
    if len(values) == 0:
        return 1.0
    if any((v == 0) and (w > 0) for w, v in zip(weights, values)):
        return 0.0
    else:
        # convert to numpy arrays
        v = np.array(values)
        w = np.array(weights) / sum(weights)  # normalized array of weights
        # prune v,w to only positive weights
        v = v[w != 0]
        w = w[w != 0]
        # compute weighted geometric mean
        return float(np.exp(np.sum(w * np.log(v))))


def ordered_weighted_geo_mean(values: Iterable[int | float], power: float) -> float:
    """
    Compute ordered weighted geometric mean of provided values

    See eg: https://www.sciencedirect.com/science/article/abs/pii/S0020025524001889

    Step-wise procedure:
      - Sort values  (if power < 0, sort in reverse order)
      - Compute weights as w ~ (i+0.5)*abs(p), with i the index into the array
      - Compute weighted geometric mean with these weights

    Depending on the power parameter, the 'center of gravity' of the weights will lie at a different quantile
    of the sorted values.

        power = -3.0        -> 20% quantile
        power = -2.0        -> 25% quantile
        power = -1.0        -> 33% quantile
        power =  0.0        -> 50% quantile (regular mean)
        power =  1.0        -> 66% quantile
        power =  2.0        -> 75% quantile
        power =  3.0        -> 80% quantile

    Hence, the net effect is that we compute the geometric mean of the provided values, with emphasis on the
      larger values (power > 0) or smaller values (power < 0).
    """
    if power == 0:
        return geo_mean(values)
    else:
        values = sorted(list(values), reverse=(power < 0))
        weights = np.array(
            linspace(
                min_value=0.0,
                max_value=1.0,
                n=len(values),
                inclusive=False,  # this makes sure that all weights are strictly positive
            )
        ) ** abs(power)
        print(values)
        print(weights)
        return weighted_geo_mean(values, weights)
