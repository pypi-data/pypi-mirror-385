"""
haphazard.data.base_dataset
---------------------------
Abstract base class for datasets.

All datasets must inherit from `BaseDataset` and 
implement both `__init__()` and `read_data()` methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal, Callable
from functools import wraps

import numpy as np
from numpy.typing import NDArray

from .mask import create_mask, MaskScheme


# -------------------------------------------------------------------------
# Type Definitions
# -------------------------------------------------------------------------
HaphazardType = Literal["controlled", "intrinsic"]
TaskType = Literal["classification", "regression"]


# -------------------------------------------------------------------------
# Utility: decorator for runtime validation of read_data outputs
# -------------------------------------------------------------------------
def validate_read_data_outputs(
    func: Callable[..., tuple[NDArray, NDArray]]
) -> Callable[..., tuple[NDArray, NDArray]]:
    """
    Decorator to validate that the output of `read_data()` matches the expected format.

    Parameters
    ----------
    func : Callable[..., tuple[NDArray, NDArray]]
        The function to be wrapped, expected to return `(x, y)`.

    Returns
    -------
    Callable[..., tuple[NDArray, NDArray]]
        Wrapped function that validates the output before returning.
    """

    @wraps(func)
    def wrapper(self, base_path: str = "./") -> tuple[NDArray, NDArray]:
        output = func(self, base_path)

        # Validate that output is a tuple of length 2
        if not isinstance(output, tuple):
            raise TypeError(f"{func.__name__} must return a tuple, got {type(output)}")
        if len(output) != 2:
            raise ValueError(f"{func.__name__} must return a tuple of length 2, got {len(output)}")

        x, y = output

        # Validate types
        if not isinstance(x, np.ndarray):
            raise TypeError(f"Features x must be a numpy ndarray, got {type(x)}")
        if not isinstance(y, np.ndarray):
            raise TypeError(f"Targets y must be a numpy ndarray, got {type(y)}")

        # Validate shapes
        if x.ndim != 2:
            raise ValueError(f"Features x must be 2D, got shape {x.shape}")
        if y.ndim != 1:
            raise ValueError(f"Targets y must be 1D, got shape {y.shape}")
        if x.shape[0] != y.shape[0]:
            raise ValueError(
                f"Number of samples mismatch: X has {x.shape[0]}, y has {y.shape[0]}"
            )

        return x, y

    return wrapper


# -------------------------------------------------------------------------
# Base Dataset Class
# -------------------------------------------------------------------------
class BaseDataset(ABC):
    """
    Abstract base class for all dataset classes.

    Attributes
    ----------
    name : str
        Name of the dataset.
    haphazard_type : HaphazardType
        Indicates whether the dataset's haphazardness is "controlled" or "intrinsic".
    task : TaskType
        Type of learning task ("classification" or "regression").
    n_features : int
        Number of features in the dataset.
    n_samples : int
        Number of samples in the dataset.
    num_classes : int or None
        Number of output classes if `task='classification'`, otherwise None.

    Notes
    -----
    - All dataset implementations must inherit from this class.
    - Derived classes must implement `__init__()` and `read_data()` methods.
    """

    # --- Required metadata fields ---
    name: str
    haphazard_type: HaphazardType
    task: TaskType
    n_features: int
    n_samples: int
    num_classes: int | None

    # -------------------------------------------------------------------------
    @abstractmethod
    def __init__(self, base_path: str = "./", **kwargs: Any) -> None:
        """
        Initialize the dataset and load data from disk.

        Parameters
        ----------
        base_path : str, default="./"
            Path to the directory containing the raw data.
        **kwargs : Any
            Additional keyword arguments passed to the dataset loader.

        Notes
        -----
        The initializer must accept `base_path` and arbitrary `**kwargs`.
        """
        self.x, self.y = self.read_data(base_path=base_path)

        # Dynamically assign attributes
        self.n_samples, self.n_features = self.x.shape
        if self.task == "regression":
            self.num_classes = None
        elif not getattr(self, "num_classes", None):
            self.num_classes = len(np.unique(self.y))

        required_attrs = ["name", "task", "haphazard_type"]
        for attr in required_attrs:
            if not hasattr(self, attr):
                raise AttributeError(
                    f"{self.__class__.__name__} must define attribute '{attr}' "
                    "before calling super().__init__()."
                )

    # -------------------------------------------------------------------------
    @abstractmethod
    @validate_read_data_outputs
    def read_data(self, base_path: str = "./") -> tuple[NDArray, NDArray]:
        """
        Read the raw dataset file into memory.

        Parameters
        ----------
        base_path : str, default="./"
            Path to the directory containing the raw data.

        Returns
        -------
        x : NDArray
            Feature matrix of shape (n_samples, n_features).
        y : NDArray
            Target vector of shape (n_samples,).

        Raises
        ------
        NotImplementedError
            If not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `read_data` method.")

    # -------------------------------------------------------------------------
    def load_mask(
        self,
        scheme: MaskScheme,
        *,
        availability_prob: float = 0.5,
        num_chunks: int = 5,
        seed: int = 42,
    ) -> NDArray[np.bool_]:
        """
        Validate, create, and return a mask for the dataset.

        Parameters
        ----------
        scheme : MaskScheme
            Determines how the mask is generated
            - "intrinsic" : Marks NaNs in the data as missing features.
            - "probabilistic" : Each feature independently observed with probability `availability_prob`.
            - "sudden" : Features become available progressively across chunks of instances.
            - "obsolete" : Features become unavailable progressively across chunks of instances.
            - "reappearing" : Two disjoint feature subsets alternately appear across chunks.
        availability_prob : float, default=0.5
            Probability that a feature is observed (used only for "probabilistic" scheme).
        num_chunks : int, default=5
            Number of chunks for chunk-based schemes.
        seed : int, default=42
            Seed for reproducibility. Passing explicitly is discouraged.

        Returns
        -------
        mask : NDArray[np.bool_]
            Boolean mask of shape (n_samples, n_features), where `True` indicates an available feature.
        """
        mask = create_mask(
            self.x,
            scheme,
            availability_prob=availability_prob,
            num_chunks=num_chunks,
            seed=seed,
        )
        return mask

    # -------------------------------------------------------------------------
    def load_data(self) -> tuple[NDArray, NDArray]:
        """
        Return the dataset's feature array and labels/targets array.

        Returns
        -------
        tuple[NDArray, NDArray]
            Tuple containing `(x, y)` already loaded in memory.
        """
        return self.x, self.y

    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a string representation of the dataset.

        Returns
        -------
        : str
            A string summarizing the dataset's metadata and load status.
        """
        data_status = "loaded" if hasattr(self, "x") and self.x is not None else "unloaded"
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"task='{self.task}', "
            f"haphazard_type='{self.haphazard_type}', "
            f"samples={self.n_samples}, "
            f"features={self.n_features}, "
            f"num_classes={self.num_classes}, "
            f"data={data_status})"
        )
