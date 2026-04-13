from datetime import time


def normalize_time(value: str | None) -> str | None:
    if not value:
        return None

    candidate = value.strip()
    if candidate == "24:00":
        return "23:59"

    parts = candidate.split(":")
    if len(parts) != 2:
        return None

    hour = int(parts[0])
    minute = int(parts[1])
    parsed = time(hour=hour, minute=minute)
    return parsed.strftime("%H:%M")