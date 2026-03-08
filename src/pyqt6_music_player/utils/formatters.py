def format_duration(duration: int | float) -> str:
    """Convert seconds to (HH:MM:SS) format string.

    Args:
        duration: Duration in seconds.

    Returns:
        Formatted time string in HH:MM:SS format (e.g., "01:23:45").

    """
    duration = int(duration)
    secs_in_hr = 3600
    secs_in_min = 60

    hours, remainder = divmod(duration, secs_in_hr)
    minutes, seconds = divmod(remainder, secs_in_min)


    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
