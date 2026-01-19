def format_duration(total_seconds: int | float):
    """
    Returns audio duration in format (mm:ss) if it's less than hour else (hh:mm:ss).
    """
    total_seconds = int(total_seconds)
    secs_in_hr = 3600
    secs_in_min = 60

    hours, remainder = divmod(total_seconds, secs_in_hr)
    minutes, total_seconds = divmod(remainder, secs_in_min)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{total_seconds:02d}"

    return f"{minutes:02d}:{total_seconds:02d}"