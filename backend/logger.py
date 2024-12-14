from datetime import datetime


def start():
    with open("log.txt", "a+", encoding="utf-8") as f:
        f.write(f"SESSION START: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n")


def log(message, file: str = "log.txt"):
    with open(file, "a+", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}: {message}\n")
