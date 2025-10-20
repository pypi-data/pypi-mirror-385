"""Data models for transformation operations in the ingestion framework.

This module defines the data models and configuration structures used for
representing transformation operations. It includes:

- Base models for transformation function arguments
- Data classes for structuring transformation configuration
- Utility methods for parsing and validating transformation parameters
- Constants for standard configuration keys

These models serve as the configuration schema for the Transform components
and provide a type-safe interface between configuration and implementation.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic import Field

from samara import BaseModel
from samara.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)


class ArgsModel(BaseModel, ABC):
    """Abstract base class for transformation function arguments.

    Serves as the foundation for all argument containers used by
    transformation functions in the framework. Each concrete subclass
    should implement type-specific argument handling for different
    transformation operations.

    All transformation argument models should inherit from this class
    to ensure a consistent interface throughout the framework.
    """


ArgsT = TypeVar("ArgsT", bound=ArgsModel)
FunctionNameT = TypeVar("FunctionNameT", bound=str)


class FunctionModel(BaseModel, Generic[ArgsT], ABC):
    """
    Model specification for transformation functions.

    This class represents the configuration for a transformation function,
    including its name and arguments.

    Args:
        function: Name of the transformation function to execute
        arguments: Arguments model specific to the transformation function
    """

    arguments: ArgsT

    @abstractmethod
    def transform(self) -> Callable:
        """Create a callable transformation function based on the model.

        This method should implement the logic to create a function that
        can be called to transform data according to the model configuration.

        Returns:
            A callable function that applies the transformation to data.
        """


FunctionModelT = TypeVar("FunctionModelT", bound=FunctionModel)


class TransformModel(BaseModel, Generic[FunctionModelT], ABC):
    """
    Model for data transformation operations.

    This model configures transformation operations for data processing,
    including the identifier, upstream source, and transformation options.

    Args:
        id: Identifier for this transformation operation
        upstream_id: Identifier(s) of the upstream component(s) providing data
        functions: List of transformation functions to apply
        options: Transformation options as key-value pairs

    Examples:
        >>> df = spark.createDataFrame(data=[("Alice", 27), ("Bob", 32),], schema=["name", "age"])
        >>> dict = {"function_type": "cast", "arguments": {"columns": {"age": "StringType",}}}
        >>> transform = TransformFunction.from_dict(dict=dict[str, Any])
        >>> df = df.transform(func=transform).printSchema()
        root
        |-- name: string (nullable = true)
        |-- age: string (nullable = true)
    """

    id_: str = Field(..., alias="id", description="Identifier for this transformation operation", min_length=1)
    upstream_id: str = Field(..., description="Identifier(s) of the upstream component(s) providing data", min_length=1)
    functions: list[FunctionModelT] = Field(..., description="List of transformation functions to apply")
