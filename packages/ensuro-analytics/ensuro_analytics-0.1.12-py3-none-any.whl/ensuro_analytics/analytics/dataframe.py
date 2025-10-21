"""Create pandas accessors for using analytics functions directly from pandas DataFrames.

This module provides functionality to create custom pandas accessors that allow
analytics functions to be called directly on DataFrame objects.
"""

import importlib
import pkgutil
import warnings
from pathlib import Path
from typing import Any, Callable

from pandas.api.extensions import register_dataframe_accessor

# Use pathlib to get the path of the current file and then find the "metrics" subdirectory
current_dir = Path(__file__).parent
metrics_dir = current_dir / "portfolio"

function_names = ["current_value", "time_series", "at_t"]


def create_accessor(module: Any, accessor_name: str) -> None:
    """Create a custom pandas accessor for a given module.

    This function creates a custom accessor class that wraps the analytics functions
    from the specified module, making them available as methods on pandas DataFrames.

    Args:
        module: The module containing the analytics functions.
        accessor_name: The name to register the accessor under.

    Raises:
        ValueError: If the DataFrame is missing required columns.
    """

    class CustomAccessor:
        """Custom accessor for pandas DataFrames.

        This class provides methods to access analytics functions directly from
        pandas DataFrame objects.

        Attributes:
            _obj: The pandas DataFrame this accessor is attached to.
        """

        def __init__(self, pandas_obj: Any) -> None:
            """Initialize the accessor.

            Args:
                pandas_obj: The pandas DataFrame to attach this accessor to.

            Raises:
                ValueError: If the DataFrame is missing required columns.
            """
            self._obj = pandas_obj
            # Ensure the DataFrame has the necessary columns
            if not all(col in self._obj.columns for col in module.REQUIRED_COLUMNS):
                raise ValueError(f"DataFrame must contain columns: {module.REQUIRED_COLUMNS}")

    def _create_method(func_name: str) -> Callable:
        """Create a method that wraps an analytics function.

        Args:
            func_name: Name of the function to wrap.

        Returns:
            A method that can be attached to the CustomAccessor class.
        """

        def method(self: Any, *args: Any, **kwargs: Any) -> Any:
            """Call the wrapped analytics function.

            Args:
                self: The CustomAccessor instance.
                *args: Positional arguments to pass to the function.
                **kwargs: Keyword arguments to pass to the function.

            Returns:
                The result of calling the analytics function.
            """
            subset = self._obj[list(module.REQUIRED_COLUMNS)]
            func = getattr(module, func_name)
            return func(subset, *args, **kwargs)

        return method

    # This loop ensures each function gets its own scope with the correct func_name
    for name in function_names:
        method = _create_method(name)
        method.__name__ = name
        setattr(CustomAccessor, name, method)

    register_dataframe_accessor(accessor_name)(CustomAccessor)


def create_ensuro_accessors() -> None:
    """Create accessors for all analytics modules in the portfolio package.

    This function iterates through all modules in the portfolio package and
    creates pandas accessors for each one. It suppresses warnings about
    accessor registration.
    """
    # Catch warning "UserWaning: registration of accessor ..."
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", category=UserWarning, message="registration of accessor")
        # Iterate through the metrics and create new modules
        for _, module_name, _ in pkgutil.iter_modules([str(metrics_dir)]):
            module = importlib.import_module(f".portfolio.{module_name}", __package__)
            create_accessor(module, module_name)
