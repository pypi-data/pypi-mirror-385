from datetime import datetime


def format_utc_timestamp(timestamp: float, format: str = "%Y-%m-%d") -> str:
    """
    Convert a UTC timestamp to a formatted date string.

    Args:
        timestamp (float): UTC timestamp to convert
        format (str, optional): Date format string. Defaults to "%Y-%m-%d".

    Returns:
        str: Formatted date string
    """
    return datetime.utcfromtimestamp(timestamp).strftime(format)
