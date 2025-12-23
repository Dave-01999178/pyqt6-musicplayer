def format_duration(seconds: int | float):
    """
    Returns audio duration in format (mm:ss) if it's less than hour else (hh:mm:ss).
    """
    int_total_duration = int(seconds)
    secs_in_hr = 3600
    secs_in_min = 60

    hours, remainder = divmod(int_total_duration, secs_in_hr)
    minutes, seconds = divmod(remainder, secs_in_min)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"