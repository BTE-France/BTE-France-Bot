from datetime import datetime


def log(message: str):
    date = datetime.now().strftime("%d/%m - %H:%M")
    print(f"[{date}] {message}")
