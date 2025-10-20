"""Base predictor class that all predictors inherit from.

This module defines the `BasePredictor` abstract base class, which establishes
a common interface and functionality for all predictors in the library, such as
detectors, segmenters, and classifiers.

Example:
    >>> from culicidaelab.core.settings import Settings
    >>> from culicidaelab.predictors.detector import MosquitoDetector
    >>> settings = Settings()
    >>> with MosquitoDetector(settings) as detector:
    ...     predictions = detector.predict("path/to/image.jpg")
    ...     detector.visualize(predictions)
"""

import io
import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generic, TypeVar, Union

import numpy as np
from PIL import Image
from fastprogress.fastprogress import progress_bar

from culicidaelab.core.base_inference_backend import BaseInferenceBackend
from culicidaelab.core.config_models import PredictorConfig
from culicidaelab.core.settings import Settings

logger = logging.getLogger(__name__)

ImageInput = Union[np.ndarray, str, Path, Image.Image, bytes, io.BytesIO]
"""Type hint for image inputs, which can be a path, numpy array, or PIL image."""

InputDataType = TypeVar("InputDataType")
"""Generic type for the input data of a predictor."""

PredictionType = TypeVar("PredictionType")
"""Generic type for the prediction output of a predictor."""

GroundTruthType = TypeVar("GroundTruthType")
"""Generic type for the ground truth data used in evaluation."""


class BasePredictor(Generic[InputDataType, PredictionType, GroundTruthType], ABC):
    """Abstract base class for all predictors.

    This class defines the common interface for all predictors (e.g., detector,
    segmenter, classifier). It relies on the main Settings object for
    configuration and a backend for model execution.

    Attributes:
        settings (Settings): The main settings object for the library.
        predictor_type (str): The key for this predictor in the configuration
            (e.g., 'classifier').
        backend (BaseInferenceBackend): An object that inherits from
            BaseInferenceBackend for model loading and inference.
    """

    def __init__(
        self,
        settings: Settings,
        predictor_type: str,
        backend: BaseInferenceBackend,
        load_model: bool = False,
    ):
        """Initializes the predictor.

        Args:
            settings (Settings): The main Settings object for the library.
            predictor_type (str): The key for this predictor in the configuration
                (e.g., 'classifier').
            backend (BaseInferenceBackend): An object that inherits from
                BaseInferenceBackend for model loading and inference.
            load_model (bool): If True, loads the model immediately upon
                initialization.
        """
        self.settings = settings
        self.predictor_type = predictor_type
        self.backend = backend
        self._config: PredictorConfig = self._get_predictor_config()
        self._logger = logging.getLogger(
            f"culicidaelab.predictor.{self.predictor_type}",
        )

        if load_model:
            self.load_model()

    def __call__(self, input_data: InputDataType, **kwargs: Any) -> Any:
        """Convenience method that calls `predict()`.

        This allows the predictor instance to be called as a function.

        Args:
            input_data (InputDataType): The input data for the prediction.
            **kwargs (Any): Additional arguments to pass to the `predict` method.

        Returns:
            Any: The result of the prediction.
        """
        if not self.backend.is_loaded:
            self.load_model()
        return self.predict(input_data, **kwargs)

    def __enter__(self):
        """Context manager entry.

        Loads the model if it is not already loaded.

        Returns:
            BasePredictor: The predictor instance.
        """
        if not self.backend.is_loaded:
            self.load_model()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.

        This default implementation does nothing, but can be overridden to handle
        resource cleanup.
        """
        pass

    @property
    def config(self) -> PredictorConfig:
        """Get the predictor configuration Pydantic model.

        Returns:
            PredictorConfig: The configuration object for this predictor.
        """
        return self._config

    @property
    def model_loaded(self) -> bool:
        """Check if the model is loaded.

        Returns:
            bool: True if the model is loaded, False otherwise.
        """
        return self.backend.is_loaded

    @contextmanager
    def model_context(self):
        """A context manager for temporary model loading.

        Ensures the model is loaded upon entering the context and unloaded
        upon exiting if it was not loaded before. This is useful for managing
        memory in pipelines.

        Yields:
            BasePredictor: The predictor instance itself.

        Example:
            >>> with predictor.model_context():
            ...     predictions = predictor.predict(data)
        """
        was_loaded = self.backend.is_loaded
        try:
            if not was_loaded:
                self.load_model()
            yield self
        finally:
            if not was_loaded and self.backend.is_loaded:
                self.unload_model()

    def evaluate(
        self,
        ground_truth: GroundTruthType,
        prediction: PredictionType | None = None,
        input_data: InputDataType | None = None,
        **predict_kwargs: Any,
    ) -> dict[str, float]:
        """Evaluate a prediction against a ground truth.

        Either `prediction` or `input_data` must be provided. If `prediction`
        is provided, it is used directly. If `prediction` is None, `input_data`
        is used to generate a new prediction.

        Args:
            ground_truth (GroundTruthType): The ground truth annotation.
            prediction (PredictionType, optional): A pre-computed prediction.
            input_data (InputDataType, optional): Input data to generate a
                prediction from, if one isn't provided.
            **predict_kwargs (Any): Additional arguments passed to the `predict`
                method.

        Returns:
            dict[str, float]: Dictionary containing evaluation metrics for a
            single item.

        Raises:
            ValueError: If neither `prediction` nor `input_data` is provided.
        """
        if prediction is None:
            if input_data is not None:
                prediction = self.predict(input_data, **predict_kwargs)
            else:
                raise ValueError(
                    "Either 'prediction' or 'input_data' must be provided.",
                )
        return self._evaluate_from_prediction(
            prediction=prediction,
            ground_truth=ground_truth,
        )

    def evaluate_batch(
        self,
        ground_truth_batch: Sequence[GroundTruthType],
        predictions_batch: Sequence[PredictionType] | None = None,
        input_data_batch: Sequence[InputDataType] | None = None,
        num_workers: int = 1,
        show_progress: bool = False,
        **predict_kwargs: Any,
    ) -> dict[str, Any]:
        """Evaluate on a batch of items using parallel processing.

        Either `predictions_batch` or `input_data_batch` must be provided.

        Args:
            ground_truth_batch (Sequence[GroundTruthType]): List of corresponding
                ground truth annotations.
            predictions_batch (Sequence[PredictionType], optional): A pre-computed
                list of predictions.
            input_data_batch (Sequence[InputDataType], optional): List of input data
                to generate predictions from.
            num_workers (int): Number of parallel workers for calculating metrics.
            show_progress (bool): Whether to show a progress bar.
            **predict_kwargs (Any): Additional arguments passed to `predict_batch`.

        Returns:
            dict[str, Any]: Dictionary containing aggregated evaluation metrics.

        Raises:
            ValueError: If the number of predictions does not match the number
                of ground truths, or if required inputs are missing.
        """
        if predictions_batch is None:
            if input_data_batch is not None:
                predictions_batch = self.predict_batch(
                    input_data_batch,
                    show_progress=show_progress,
                    **predict_kwargs,
                )
            else:
                raise ValueError(
                    "Either 'predictions_batch' or 'input_data_batch' must be provided.",
                )

        if len(predictions_batch) != len(ground_truth_batch):
            raise ValueError(
                f"Number of predictions ({len(predictions_batch)}) must match "
                f"number of ground truths ({len(ground_truth_batch)}).",
            )

        per_item_metrics = self._calculate_metrics_parallel(
            predictions_batch,
            ground_truth_batch,
            num_workers,
            show_progress,
        )
        aggregated_metrics = self._aggregate_metrics(per_item_metrics)
        final_report = self._finalize_evaluation_report(
            aggregated_metrics,
            predictions_batch,
            ground_truth_batch,
        )
        return final_report

    def get_model_info(self) -> dict[str, Any]:
        """Gets information about the loaded model.

        Returns:
            dict[str, Any]: A dictionary containing details about the model, such
            as architecture, path, etc.
        """
        return {
            "predictor_type": self.predictor_type,
            "model_loaded": self.backend.is_loaded,
            "config": self.config.model_dump(),
        }

    def load_model(self) -> None:
        """Delegates model loading to the configured backend."""
        if not self.backend.is_loaded:
            self._logger.info(
                f"Loading model for {self.predictor_type} using {self.backend.__class__.__name__}",
            )
            try:
                self.backend.load_model()
                self._logger.info(f"Successfully loaded model for {self.predictor_type}")
            except Exception as e:
                self._logger.error(f"Failed to load model for {self.predictor_type}: {e}")
                raise RuntimeError(f"Failed to load model for {self.predictor_type}: {e}") from e

    def predict(
        self,
        input_data: InputDataType,
        **kwargs: Any,
    ) -> PredictionType:
        """Makes a prediction on a single input data sample.

        Args:
            input_data (InputDataType): The input data (e.g., an image as a NumPy
                array) to make a prediction on.
            **kwargs (Any): Additional predictor-specific arguments.

        Returns:
            PredictionType: The prediction result, with a format specific to the
            predictor type.

        Raises:
            RuntimeError: If the model is not loaded before calling this method.
        """
        if not self.backend.is_loaded:
            try:
                self.load_model()
            except Exception as e:
                raise RuntimeError(f"Failed to load model: {e}") from e

        image = self._load_and_validate_image(input_data)

        raw_output = self.backend.predict(image, **kwargs)

        return self._convert_raw_to_prediction(raw_output)

    def predict_batch(
        self,
        input_data_batch: Sequence[InputDataType],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> list[PredictionType]:
        """Makes predictions on a batch of inputs by delegating to the backend.

        Args:
            input_data_batch (Sequence[InputDataType]): A sequence of inputs.
            show_progress (bool): If True, displays a progress bar.
            **kwargs (Any): Additional arguments for the backend's `predict_batch`.

        Returns:
            list[PredictionType]: A list of prediction results.
        """
        if not input_data_batch:
            return []

        if not self.backend.is_loaded:
            self.load_model()

        raw_predictions = self.backend.predict_batch(list(input_data_batch), **kwargs)
        final_predictions = [self._convert_raw_to_prediction(raw_pred) for raw_pred in raw_predictions]
        return final_predictions

    def unload_model(self) -> None:
        """Unloads the model to free memory."""
        if self.backend.is_loaded:
            self.backend.unload_model()
            self._logger.info(f"Unloaded model for {self.predictor_type}")

    @abstractmethod
    def _evaluate_from_prediction(
        self,
        prediction: PredictionType,
        ground_truth: GroundTruthType,
    ) -> dict[str, float]:
        """The core metric calculation logic for a single item.

        This method must be implemented by subclasses to define how a prediction
        is evaluated against a ground truth.

        Args:
            prediction (PredictionType): Model prediction.
            ground_truth (GroundTruthType): Ground truth annotation.

        Returns:
            dict[str, float]: Dictionary containing evaluation metrics.
        """
        pass

    @abstractmethod
    def _convert_raw_to_prediction(self, raw_prediction: Any) -> PredictionType:
        """Converts raw backend output to a structured prediction model.

        Subclasses MUST implement this to convert raw output (e.g., a numpy array)
        from the backend into the final Pydantic prediction model.

        Args:
            raw_prediction (Any): The raw output from the inference backend.

        Returns:
            PredictionType: The structured prediction object.
        """
        pass

    @abstractmethod
    def visualize(
        self,
        input_data: InputDataType,
        predictions: PredictionType,
        save_path: str | Path | None = None,
    ) -> np.ndarray:
        """Visualizes the predictions on the input data.

        Args:
            input_data (InputDataType): The original input data (e.g., an image).
            predictions (PredictionType): The prediction result obtained from
                the `predict` method.
            save_path (str | Path, optional): An optional path to save the
                visualization to a file.

        Returns:
            np.ndarray: A NumPy array representing the visualized image.
        """
        pass

    def _aggregate_metrics(
        self,
        metrics_list: list[dict[str, float]],
    ) -> dict[str, float]:
        """Aggregates metrics from multiple evaluations.

        Calculates the mean and standard deviation for each metric across a list
        of evaluation results.

        Args:
            metrics_list (list[dict[str, float]]): A list of metric dictionaries.

        Returns:
            dict[str, float]: A dictionary with aggregated metrics (mean, std).
        """
        if not metrics_list:
            return {}

        valid_metrics = [m for m in metrics_list if m]
        if not valid_metrics:
            self._logger.warning("No valid metrics found for aggregation")
            return {}

        all_keys = {k for m in valid_metrics for k in m.keys()}
        aggregated = {}
        for key in all_keys:
            values = [m[key] for m in valid_metrics if key in m]
            if values:
                aggregated[f"{key}_mean"] = float(np.mean(values))
                aggregated[f"{key}_std"] = float(np.std(values))

        aggregated["count"] = len(valid_metrics)
        return aggregated

    def _calculate_metrics_parallel(
        self,
        predictions: Sequence[PredictionType],
        ground_truths: Sequence[GroundTruthType],
        num_workers: int = 4,
        show_progress: bool = True,
    ) -> list[dict[str, float]]:
        """Calculates metrics for individual items in parallel.

        Args:
            predictions (Sequence[PredictionType]): A sequence of predictions.
            ground_truths (Sequence[GroundTruthType]): A sequence of ground truths.
            num_workers (int): The number of threads to use.
            show_progress (bool): Whether to display a progress bar.

        Returns:
            list[dict[str, float]]: A list of metric dictionaries, one for each item.
        """
        per_item_metrics = []

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_idx = {
                executor.submit(
                    self._evaluate_from_prediction,
                    predictions[i],
                    ground_truths[i],
                ): i
                for i in range(len(predictions))
            }

            iterator = as_completed(future_to_idx)
            if show_progress:
                iterator = progress_bar(
                    iterator,
                    total=len(future_to_idx),
                )
            for future in iterator:
                try:
                    per_item_metrics.append(future.result())
                except Exception as e:
                    idx = future_to_idx.get(future, "unknown")
                    self._logger.error(
                        f"Error calculating metrics for item {idx}: {e}",
                    )
                    per_item_metrics.append({})
        return per_item_metrics

    def _finalize_evaluation_report(
        self,
        aggregated_metrics: dict[str, float],
        predictions: Sequence[PredictionType],
        ground_truths: Sequence[GroundTruthType],
    ) -> dict[str, Any]:
        """Optional hook to post-process the final evaluation report.

        This method can be overridden by subclasses to add more details to the
        final report.

        Args:
            aggregated_metrics (dict[str, float]): The aggregated metrics.
            predictions (Sequence[PredictionType]): The list of predictions.
            ground_truths (Sequence[GroundTruthType]): The list of ground truths.

        Returns:
            dict[str, Any]: The finalized evaluation report.
        """
        return aggregated_metrics

    def _get_predictor_config(self) -> PredictorConfig:
        """Gets the configuration for this predictor.

        Returns:
            PredictorConfig: A Pydantic `PredictorConfig` model for this
            predictor instance.

        Raises:
            ValueError: If the configuration is invalid or not found.
        """
        config = self.settings.get_config(f"predictors.{self.predictor_type}")
        if not isinstance(config, PredictorConfig):
            raise ValueError(
                f"Configuration for predictor '{self.predictor_type}' not found or is invalid.",
            )
        return config

    def _load_and_validate_image(self, input_data: InputDataType) -> Image.Image:
        """Loads and validates an input image from various formats.

        Args:
            input_data: input data type (numpy array, file path, PIL Image, bytes,
                or io.BytesIO).

        Returns:
            A validated PIL Image in RGB format.

        Raises:
            ValueError: If input format is invalid or image cannot be loaded.
            FileNotFoundError: If image file path does not exist.
            TypeError: If the input type is not supported.
        """
        if isinstance(input_data, (str, Path)):
            image_path = Path(input_data)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            try:
                image = Image.open(image_path).convert("RGB")
                return image
            except Exception as e:
                raise ValueError(f"Cannot load image from {image_path}: {e}")

        elif isinstance(input_data, Image.Image):
            return input_data.convert("RGB")

        elif isinstance(input_data, np.ndarray):
            if input_data.ndim != 3 or input_data.shape[2] != 3:
                raise ValueError(
                    f"Expected 3D RGB image, got shape: {input_data.shape}",
                )
            if input_data.dtype == np.uint8:
                return Image.fromarray(input_data)
            elif input_data.dtype in [np.float32, np.float64]:
                if input_data.max() > 1.0 or input_data.min() < 0.0:
                    raise ValueError("Float images must be in range [0, 1]")
                return Image.fromarray((input_data * 255).astype(np.uint8))
            else:
                raise ValueError(f"Unsupported numpy dtype: {input_data.dtype}")

        elif isinstance(input_data, bytes):
            try:
                return Image.open(io.BytesIO(input_data)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Cannot load image from bytes: {e}")

        elif isinstance(input_data, io.BytesIO):
            try:
                return Image.open(input_data).convert("RGB")
            except Exception as e:
                raise ValueError(f"Cannot load image from BytesIO stream: {e}")

        else:
            raise TypeError(
                f"Unsupported input type: {type(input_data)}. "
                f"Expected np.ndarray, str, pathlib.Path, PIL.Image.Image, bytes, or io.BytesIO",
            )

    def _prepare_batch_images(
        self,
        input_data_batch: Sequence[InputDataType],
    ) -> tuple[list[Image.Image], list[int]]:
        """Prepares and validates a batch of images for processing.

        Args:
            input_data_batch: A sequence of input images.

        Returns:
            A tuple of (valid_images, valid_indices) where valid_indices
            tracks the original position of each valid image.
        """
        valid_images = []
        valid_indices = []
        for idx, input_data in enumerate(input_data_batch):
            try:
                image = self._load_and_validate_image(input_data)
                valid_images.append(image)
                valid_indices.append(idx)
            except Exception as e:
                self._logger.warning(f"Skipping image at index {idx}: {e}")
        return valid_images, valid_indices
