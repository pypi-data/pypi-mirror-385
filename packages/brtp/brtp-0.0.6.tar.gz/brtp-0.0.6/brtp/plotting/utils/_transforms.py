from __future__ import annotations

import math
from abc import ABC, abstractmethod

import numpy as np


# =================================================================================================
#  Base Class
# =================================================================================================
class Transform(ABC):
    """
    Base class that implements a plotting scale transform, transforming user scale <-> figure scale.
        user scale:   the scale that the user sees and can use to define plotting coordinates (e.g. in a Canvas class)
        figure scale: the scale that is actually used for plotting (e.g. in matplotlib figures)

    We define both forward (user -> figure) and backward (figure -> user) transforms.
    """

    def __init__(self, user_range: tuple[float, float], figure_range: tuple[float, float], reverse: bool = False):
        """
        Constructor for Transform base class.

        :param user_range: (user_min, user_max), with user_min < user_max
        :param figure_range: (fig_min, fig_max), with fig_min < fig_max
        :param reverse: (bool, default=True) if True, the transform reverses the order of values
        """
        self._user_range = user_range
        self._figure_range = figure_range
        self._reverse = reverse

    # -------------------------------------------------------------------------
    #  Main API
    # -------------------------------------------------------------------------
    def user_range(self) -> tuple[float, float]:
        """Get the user scale range (user_min, user_max), with user_min < user_max, even if is_reverse() is True."""
        return self._user_range

    def figure_range(self) -> tuple[float, float]:
        """
        Get the figure scale range (fig_min, fig_max), with fig_min < fig_max, even if is_reverse() is True.
        """
        return self._figure_range

    def is_reverse(self) -> bool:
        """Return True if the transform reverses the order of values, False otherwise."""
        return self._reverse

    def __call__(self, v_user: float | list[float] | np.ndarray) -> float | list[float] | np.ndarray:
        """
        Forward transform (user value -> figure value).
        Can be applied to float, list of floats, or numpy array, with the return type identical to the input type.
        """

        # --- input type handling ---
        is_scalar = isinstance(v_user, (int, float))
        is_list = isinstance(v_user, list)

        if is_list:
            v_user = np.array(v_user)
        elif is_scalar:
            v_user = np.array([v_user])

        # --- forward transform ---
        v_fig = self._forward(v_user)

        # --- reverse flag handling ---
        if self._reverse:
            v_fig = self._figure_range[1] - (v_fig - self._figure_range[0])

        # --- output type handling ---
        if is_scalar:
            return float(v_fig[0])
        elif is_list:
            return [float(v) for v in v_fig]
        else:
            return v_fig

    def inv(self, v_fig: float | list[float] | np.ndarray) -> float | list[float] | np.ndarray:
        """
        Backward (inverse) transform (figure value -> user value).
        Can be applied to float, list of floats, or numpy array, with the return type identical to the input type.
        """

        # --- input type handling ---
        is_scalar = isinstance(v_fig, (int, float))
        is_list = isinstance(v_fig, list)

        if is_list:
            v_fig = np.array(v_fig)
        elif is_scalar:
            v_fig = np.array([v_fig])

        # --- reverse flag handling ---
        if self._reverse:
            v_fig = self._figure_range[1] - (v_fig - self._figure_range[0])

        # --- backward transform ---
        v_user = self._backward(v_fig)

        # --- output type handling ---
        if is_scalar:
            return float(v_user[0])
        elif is_list:
            return [float(v) for v in v_user]
        else:
            return v_user

    # -------------------------------------------------------------------------
    #  Abstract API
    # -------------------------------------------------------------------------
    @abstractmethod
    def _forward(self, v_user: np.ndarray) -> np.ndarray:
        """Forward transform (user scale -> figure scale), irrespective of reverse flag"""
        raise NotImplementedError()

    @abstractmethod
    def _backward(self, v_fig: np.ndarray) -> np.ndarray:
        """Backward (inverse) transform (figure scale -> user scale), irrespective of reverse flag"""
        raise NotImplementedError()

    @abstractmethod
    def is_linear(self) -> bool:
        """Return True if the transform is linear, False otherwise."""
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    #  Factory methods
    # -------------------------------------------------------------------------
    @classmethod
    def linear(
        cls, user_range: tuple[float, float], figure_range: tuple[float, float], reverse: bool = False
    ) -> TransformLinear:
        return TransformLinear(user_range, figure_range, reverse)

    @classmethod
    def log(
        cls, user_range: tuple[float, float], figure_range: tuple[float, float], reverse: bool = False
    ) -> TransformLog:
        return TransformLog(user_range, figure_range, reverse)


# =================================================================================================
#  LINEAR
# =================================================================================================
class TransformLinear(Transform):
    def __init__(self, user_range: tuple[float, float], figure_range: tuple[float, float], reverse: bool = False):
        super().__init__(user_range, figure_range, reverse)

        # compute c0, c1 such that ...
        #    v_fig = c0 + (c1 * v_user)
        self._c1 = (figure_range[1] - figure_range[0]) / (user_range[1] - user_range[0])
        self._c0 = figure_range[0] - (user_range[0] * self._c1)

        # compute c0_inv, c1_inv such that ...
        #    v_user = c0_inv + (c1_inv * v_fig)
        self._c1_inv = 1.0 / self._c1
        self._c0_inv = user_range[0] - (figure_range[0] * self._c1_inv)

    def _forward(self, v_user: np.ndarray) -> np.ndarray:
        return self._c0 + (self._c1 * v_user)

    def _backward(self, v_fig: np.ndarray) -> np.ndarray:
        return self._c0_inv + (self._c1_inv * v_fig)

    def is_linear(self) -> bool:
        return True


# =================================================================================================
#  LOGARITHMIC
# =================================================================================================
class TransformLog(Transform):
    def __init__(self, user_range: tuple[float, float], figure_range: tuple[float, float], reverse: bool = False):
        super().__init__(user_range, figure_range, reverse)

        # compute c0, c1 such that ...
        #    v_fig = c0 + (c1 * log(v_user))
        self._c1 = (figure_range[1] - figure_range[0]) / (math.log(user_range[1]) - math.log(user_range[0]))
        self._c0 = figure_range[0] - (math.log(user_range[0]) * self._c1)

        # compute c0_inv, c1_inv such that ...
        #    log(v_user) = c0_inv + (c1_inv * v_fig)
        self._c1_inv = 1.0 / self._c1
        self._c0_inv = math.log(user_range[0]) - (figure_range[0] * self._c1_inv)

    def _forward(self, v_user: np.ndarray) -> np.ndarray:
        return self._c0 + (self._c1 * np.log(v_user))

    def _backward(self, v_fig: np.ndarray) -> np.ndarray:
        return np.exp(self._c0_inv + (self._c1_inv * v_fig))

    def is_linear(self) -> bool:
        return False
