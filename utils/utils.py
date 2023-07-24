def escape_minecraft_username_markdown(string: str) -> str:
    return string.replace("_", r"\_").replace(
        "*", r"\*"
    )  # Escape markdown symbols that could be present in players' names


def format_byte_size(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
