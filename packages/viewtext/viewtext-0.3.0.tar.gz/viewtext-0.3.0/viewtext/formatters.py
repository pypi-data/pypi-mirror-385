"""
Formatter registry for text output formatting.

This module provides the FormatterRegistry class with built-in formatters
for text, numbers, prices, dates, relative times, and template strings.
"""

from datetime import datetime
from typing import Any, Callable


class FormatterRegistry:
    """
    Registry for value formatting functions.

    The formatter registry manages formatter functions that transform values
    into formatted strings. Includes built-in formatters for common use cases.

    Attributes
    ----------
    _formatters : dict[str, Callable]
        Internal dictionary mapping formatter names to functions

    Examples
    --------
    >>> registry = FormatterRegistry()
    >>> formatter = registry.get("price")
    >>> formatter(123.45, symbol="$", decimals=2)
    '$123.45'
    """

    def __init__(self) -> None:
        """Initialize the formatter registry with built-in formatters."""
        self._formatters: dict[str, Callable] = {}
        self._register_builtin_formatters()

    def _register_builtin_formatters(self) -> None:
        """Register all built-in formatters."""
        self.register("text", self._format_text)
        self.register("text_uppercase", self._format_text_uppercase)
        self.register("price", self._format_price)
        self.register("number", self._format_number)
        self.register("datetime", self._format_datetime)
        self.register("relative_time", self._format_relative_time)
        self.register("template", self._format_template)

    def register(self, name: str, formatter: Callable) -> None:
        """
        Register a formatter function.

        Parameters
        ----------
        name : str
            The formatter name to register
        formatter : Callable
            A callable that takes a value and keyword arguments and returns
            a formatted string

        Examples
        --------
        >>> registry = FormatterRegistry()
        >>> def custom_formatter(value, **kwargs):
        ...     return f"Custom: {value}"
        >>> registry.register("custom", custom_formatter)
        """
        self._formatters[name] = formatter

    def get(self, name: str) -> Callable:
        """
        Retrieve a registered formatter function.

        Parameters
        ----------
        name : str
            The formatter name to retrieve

        Returns
        -------
        Callable
            The formatter function

        Raises
        ------
        ValueError
            If the formatter name is not registered

        Examples
        --------
        >>> registry = FormatterRegistry()
        >>> formatter = registry.get("text")
        >>> formatter("hello", prefix=">> ")
        '>> hello'
        """
        if name not in self._formatters:
            raise ValueError(f"Unknown formatter: {name}")
        return self._formatters[name]

    @staticmethod
    def _format_text(value: Any, **kwargs: Any) -> str:
        """
        Format value as text with optional prefix and suffix.

        Parameters
        ----------
        value : Any
            The value to format
        **kwargs : Any
            prefix : str, optional
                String to prepend (default: "")
            suffix : str, optional
                String to append (default: "")

        Returns
        -------
        str
            Formatted text string

        Examples
        --------
        >>> FormatterRegistry._format_text("hello", prefix=">> ", suffix="!")
        '>> hello!'
        """
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        return f"{prefix}{str(value)}{suffix}"

    @staticmethod
    def _format_text_uppercase(value: Any, **kwargs: Any) -> str:
        """
        Format value as uppercase text.

        Parameters
        ----------
        value : Any
            The value to format
        **kwargs : Any
            Unused, provided for consistency

        Returns
        -------
        str
            Uppercase text string

        Examples
        --------
        >>> FormatterRegistry._format_text_uppercase("hello")
        'HELLO'
        """
        return str(value).upper()

    @staticmethod
    def _format_price(value: Any, **kwargs: Any) -> str:
        """
        Format value as a price with currency symbol.

        Parameters
        ----------
        value : Any
            The numeric value to format
        **kwargs : Any
            symbol : str, optional
                Currency symbol (default: "")
            decimals : int, optional
                Number of decimal places (default: 2)
            thousands_sep : str, optional
                Thousands separator (default: "")
            decimal_sep : str, optional
                Decimal separator (default: ".")
            symbol_position : str, optional
                "prefix" or "suffix" (default: "prefix")

        Returns
        -------
        str
            Formatted price string, or empty string if value is None

        Examples
        --------
        >>> FormatterRegistry._format_price(1234.56, symbol="$", decimals=2)
        '$1234.56'
        >>> FormatterRegistry._format_price(1234.56, symbol="€", decimals=2,
        ...                                  symbol_position="suffix")
        '1234.56€'
        >>> FormatterRegistry._format_price(1234567.89, symbol="€", decimals=2,
        ...                                  thousands_sep=".", decimal_sep=",")
        '€1.234.567,89'
        """
        symbol = kwargs.get("symbol", "")
        decimals = kwargs.get("decimals", 2)
        thousands_sep = kwargs.get("thousands_sep", "")
        decimal_sep = kwargs.get("decimal_sep", ".")

        if value is None:
            return ""

        try:
            num_val = float(value)
        except (ValueError, TypeError):
            return str(value)

        if thousands_sep or decimal_sep != ".":
            formatted = f"{num_val:,.{decimals}f}"
            if decimal_sep != ".":
                formatted = formatted.replace(".", "\x00")
            if thousands_sep:
                formatted = formatted.replace(",", thousands_sep)
            else:
                formatted = formatted.replace(",", "")
            if decimal_sep != ".":
                formatted = formatted.replace("\x00", decimal_sep)
        else:
            formatted = f"{num_val:.{decimals}f}"

        if symbol:
            symbol_position = kwargs.get("symbol_position", "prefix")
            if symbol_position == "suffix":
                return f"{formatted}{symbol}"
            else:
                return f"{symbol}{formatted}"

        return formatted

    @staticmethod
    def _format_number(value: Any, **kwargs: Any) -> str:
        """
        Format value as a number with optional prefix, suffix, and separators.

        Parameters
        ----------
        value : Any
            The numeric value to format
        **kwargs : Any
            prefix : str, optional
                String to prepend (default: "")
            suffix : str, optional
                String to append (default: "")
            decimals : int, optional
                Number of decimal places (default: 0)
            thousands_sep : str, optional
                Thousands separator (default: "")
            decimal_sep : str, optional
                Decimal separator (default: ".")

        Returns
        -------
        str
            Formatted number string, or empty string if value is None

        Examples
        --------
        >>> FormatterRegistry._format_number(1234567, thousands_sep=",")
        '1,234,567'
        >>> FormatterRegistry._format_number(23.456, decimals=1, suffix="°C")
        '23.5°C'
        >>> FormatterRegistry._format_number(1234567.89, decimals=2,
        ...                                   thousands_sep=".", decimal_sep=",")
        '1.234.567,89'
        """
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        decimals = kwargs.get("decimals", 0)
        thousands_sep = kwargs.get("thousands_sep", "")
        decimal_sep = kwargs.get("decimal_sep", ".")

        if value is None:
            return ""

        try:
            num_val = float(value)
        except (ValueError, TypeError):
            return str(value)

        if thousands_sep or decimal_sep != ".":
            formatted = f"{num_val:,.{decimals}f}"
            if decimal_sep != ".":
                formatted = formatted.replace(".", "\x00")
            if thousands_sep:
                formatted = formatted.replace(",", thousands_sep)
            else:
                formatted = formatted.replace(",", "")
            if decimal_sep != ".":
                formatted = formatted.replace("\x00", decimal_sep)
        else:
            formatted = f"{num_val:.{decimals}f}"

        return f"{prefix}{formatted}{suffix}"

    @staticmethod
    def _format_datetime(value: Any, **kwargs: Any) -> str:
        """
        Format value as a datetime string.

        Parameters
        ----------
        value : Any
            The datetime value to format (datetime, timestamp, or string)
        **kwargs : Any
            format : str, optional
                strftime format string (default: "%Y-%m-%d %H:%M:%S")

        Returns
        -------
        str
            Formatted datetime string, or empty string if value is None

        Examples
        --------
        >>> from datetime import datetime
        >>> dt = datetime(2023, 12, 25, 15, 30)
        >>> FormatterRegistry._format_datetime(dt, format="%Y-%m-%d")
        '2023-12-25'
        >>> FormatterRegistry._format_datetime(1703516400, format="%Y-%m-%d")
        '2023-12-25'
        """
        format_str = kwargs.get("format", "%Y-%m-%d %H:%M:%S")

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.strftime(format_str)
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime(format_str)
        elif isinstance(value, str):
            return value

        return str(value)

    @staticmethod
    def _format_relative_time(value: Any, **kwargs: Any) -> str:
        """
        Format value as a relative time string (e.g., "5m ago").

        Parameters
        ----------
        value : Any
            The time value in seconds
        **kwargs : Any
            format : str, optional
                "short" or "long" format (default: "short")

        Returns
        -------
        str
            Formatted relative time string, or empty string if value is None

        Examples
        --------
        >>> FormatterRegistry._format_relative_time(45, format="short")
        '45s ago'
        >>> FormatterRegistry._format_relative_time(3600, format="long")
        '1 hours ago'
        >>> FormatterRegistry._format_relative_time(86400, format="short")
        '1d ago'
        """
        format_type = kwargs.get("format", "short")

        if value is None:
            return ""

        try:
            seconds = int(value)
        except (ValueError, TypeError):
            return str(value)

        if seconds < 60:
            return (
                f"{seconds}s ago"
                if format_type == "short"
                else f"{seconds} seconds ago"
            )
        elif seconds < 3600:
            minutes = seconds // 60
            return (
                f"{minutes}m ago"
                if format_type == "short"
                else f"{minutes} minutes ago"
            )
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago" if format_type == "short" else f"{hours} hours ago"
        else:
            days = seconds // 86400
            return f"{days}d ago" if format_type == "short" else f"{days} days ago"

    @staticmethod
    def _format_template(value: Any, **kwargs: Any) -> str:
        """
        Format value using a template string with field substitution.

        Parameters
        ----------
        value : Any
            Dictionary containing field values
        **kwargs : Any
            template : str, optional
                Template string with {field} placeholders (default: "{}")
            fields : list[str], optional
                List of field paths to extract (default: [])

        Returns
        -------
        str
            Formatted template string, or error message if formatting fails

        Examples
        --------
        >>> value = {"name": "John", "age": 30}
        >>> FormatterRegistry._format_template(
        ...     value,
        ...     template="{name} is {age} years old",
        ...     fields=["name", "age"]
        ... )
        'John is 30 years old'
        """
        template = str(kwargs.get("template", "{}"))
        fields = kwargs.get("fields", [])

        if not isinstance(value, dict):
            return str(value)

        field_values: dict[str, Any] = {}
        for field_path in fields:
            val: Any = value
            for key in field_path.split("."):
                if isinstance(val, dict):
                    val = val.get(key)
                    if val is None:
                        break
                else:
                    val = None
                    break

            field_name = field_path.replace(".", "_")
            field_values[field_name] = val if val is not None else ""

        try:
            return str(template.format(**field_values))
        except (KeyError, ValueError) as e:
            return f"Template error: {e}"


_global_formatter_registry = FormatterRegistry()


def get_formatter_registry() -> FormatterRegistry:
    """
    Get the global formatter registry instance.

    Returns
    -------
    FormatterRegistry
        The global formatter registry

    Examples
    --------
    >>> from viewtext import get_formatter_registry
    >>> registry = get_formatter_registry()
    >>> formatter = registry.get("price")
    """
    return _global_formatter_registry
