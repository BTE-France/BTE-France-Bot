def escape_minecraft_username_markdown(string: str) -> str:
    return string.replace("_", r"\_").replace(
        "*", r"\*"
    )  # Escape markdown symbols that could be present in players' names
