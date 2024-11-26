import os

RANK_DICT = {
    "admin": "Admin",
    "dev": "Développeur",
    "helper": "Helper",
    "archiviste": "Archiviste",
    "ingenieur": "Ingénieur",
    "architecte": "Architecte",
    "contremaitre": "Contremaître",
    "macon": "Maçon",
    "builder": "Builder",
    "debutant": "Débutant",
    "default": "Visiteur",
}

RANK_EMOTE_DICT = {
    "admin": "<:admin:1289875079563575377>",
    "dev": "<:developpeur:1289872707122630708>",
    "helper": "<:support:1289872539509723147>",
    "archiviste": "<:archiviste:1289872538205425714>",
    "ingenieur": "<:ingenieur:1289872536880021527>",
    "architecte": "<:architecte:1289872534900310068>",
    "contremaitre": "<:contremaitre:1289872533176455220>",
    "macon": "<:macon:1289872531947520045>",
    "builder": "<:builder:1289872528734687256>",
    "debutant": "<:debutant:1289872527685980172>",
    "default": "<:visiteur:1289872530277924915>",
}


def escape_minecraft_username_markdown(string: str) -> str:
    return string.replace("_", r"\_").replace("*", r"\*")  # Escape markdown symbols that could be present in players' names


def format_byte_size(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_env(var_name):
    if not (env_var := os.getenv(var_name)):
        raise Exception(f"{var_name} environment variable not found!")
    return env_var
