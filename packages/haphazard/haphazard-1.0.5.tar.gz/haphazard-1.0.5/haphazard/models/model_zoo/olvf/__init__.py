"""
haphazard.models.model_zoo.olvf
-------------------------------
Wrapper over OLVF model for binary and multi-class classification.

Implements `RunOLVF` runner class and a `MultiClassWrapper` for handling
multi-class tasks using a One-vs-Rest strategy.
"""

import time
import copy
from typing import Any

import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from .olvf import OLVF
from ...base_model import BaseModel, BaseDataset
from ...model_zoo import register_model
from ....utils.seeding import seed_everything


class MultiClassWrapper:
    """
    Wraps a binary OLVF model to perform multi-class classification using
    the One-vs-Rest (OvR) strategy.

    Each class is handled by a separate copy of the base binary model.

    Attributes
    ----------
    num_classes : int
        Number of unique classes in the dataset.
    models : list[OLVF]
        Independent OLVF instances for each class.
    """

    def __init__(self, model_instance: OLVF, num_classes: int) -> None:
        """
        Initialize the One-vs-Rest wrapper.

        Parameters
        ----------
        model_instance : OLVF
            A fully initialized binary OLVF model instance.
        num_classes : int
            Total number of output classes.
        """
        self.num_classes: int = num_classes
        self.models: list[OLVF] = [copy.deepcopy(model_instance) for _ in range(num_classes)]

    def partial_fit(
        self,
        X: NDArray[np.float64],
        X_mask: NDArray[np.bool_],
        y_true: int,
    ) -> tuple[int, list[float]]:
        """
        Perform a single online update step for one instance.

        Parameters
        ----------
        X : NDArray[np.float64]
            Input feature vector, shape (n_features,).
        X_mask : NDArray[np.bool_]
            Binary mask for available features.
        y_true : int
            Ground-truth label in [0, num_classes).

        Returns
        -------
        tuple[int, list[float]]
            - Predicted class index.
            - Logits for each class, length `num_classes`.
        """
        logits = [0.0 for _ in range(self.num_classes)]

        for cls_idx, model in enumerate(self.models):
            binary_label = 1 if y_true == cls_idx else 0
            _, logit = model.partial_fit(X, X_mask, binary_label)
            logits[cls_idx] = float(logit)

        y_pred = int(np.argmax(logits))
        return y_pred, logits


@register_model("olvf")
class RunOLVF(BaseModel):
    """
    Runner class for OLVF model.

    Attributes
    ----------
    name : str
        Model name.
    tasks : set[str]
        Supported task types.
    deterministic : bool
        Whether model is deterministic.
    hyperparameters : set[str]
        Supported hyperparameters.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the OLVF runner class.

        Parameters
        ----------
        **kwargs
            Optional parameters forwarded to `BaseModel`.
        """
        self.name = "OLVF"
        self.tasks = {"classification"}
        self.deterministic = True
        self.hyperparameters = {"C", "C_bar", "B", "reg", "n_feat0"}

        super().__init__(**kwargs)

    def fit(
        self,
        dataset: BaseDataset,
        mask_params: dict[str, Any] | None = None,
        model_params: dict[str, Any] | None = None,
        seed: int = 42,
    ) -> dict[str, Any]:
        """
        Run the OLVF model on a dataset.

        Parameters
        ----------
        dataset : BaseDataset
            Dataset object with `.load_data()` and `.load_mask()`.
        mask_params : dict[str, Any] | None, optional
            Parameters for dataset mask generation.
        model_params : dict[str, Any] | None, optional
            Hyperparameters for OLVF model.
        seed : int, default=42
            Random seed for reproducibility.

        Returns
        -------
        dict[str, Any]
            Dictionary containing:
            - labels: Ground truth labels.
            - preds: Predicted labels.
            - logits: Model output logits or probabilities.
            - time_taken: Time taken for full dataset pass.
            - is_logit: Indicates whether scores are logits (True) or probabilities (False).
        """
        # --- Validate task ---
        if dataset.task not in self.tasks:
            raise ValueError(
                f"Model '{self.__class__.__name__}' does not support '{dataset.task}'. "
                f"Supported task(s): {self.tasks}"
            )

        mask_params = mask_params or {}
        model_params = model_params or {}

        # --- Load data ---
        x, y = dataset.load_data()
        mask = dataset.load_mask(**mask_params)

        # Set random seed and initialize base_model
        seed_everything(seed)
        base_model: OLVF = OLVF(**model_params)

        if dataset.task == "regression":
            raise NotImplementedError("Regression task not supported for OLVF.")

        elif dataset.task == "classification":
            if dataset.num_classes is None:
                raise ValueError(f"'{dataset.name}.num_classes' cannot be None for classification task.")
            
            if dataset.num_classes == 2:
                model: OLVF | MultiClassWrapper = base_model
            else:
                model = MultiClassWrapper(base_model, num_classes=dataset.num_classes)

            pred_list: list[int | float] = []
            logit_list: list[list[float] | float] = []

            # --- Train model ---
            start_time = time.perf_counter()

            for i in tqdm(
                range(dataset.n_samples),
                total=dataset.n_samples,
                desc="Running OLVF",
            ):
                xi, mi, yi = x[i], mask[i], y[i]
                pred, logit = model.partial_fit(xi, mi, int(yi))
                pred_list.append(pred)
                logit_list.append(logit)

            end_time = time.perf_counter()
            time_taken = end_time - start_time

            # --- Final formatting ---
            labels = np.asarray(y, dtype=np.int64)
            preds = np.asarray(pred_list, dtype=np.int64)
            logits = np.asarray(logit_list, dtype=np.float64)

            # --- Sanity checks ---
            if dataset.num_classes == 2:
                assert logits.ndim == 1, (
                    f"Expected logits to be 1D for binary classification, got {logits.shape}."
                )
            else:
                assert logits.ndim == 2, (
                    f"Expected logits to be 2D for multi-class classification, got {logits.shape}."
                )

            is_logit = True  # OLVF model returns logits

            return {
                "labels": labels,
                "preds": preds,
                "logits": logits,
                "time_taken": time_taken,
                "is_logit": is_logit,
            }

        # Fallback for unsupported task
        raise ValueError(f"Unknown task type: '{dataset.task}'")


__all__ = ["RunOLVF"]
