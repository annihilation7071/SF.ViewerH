from datetime import datetime
import os


path = os.path.join(os.getcwd(), f"logs/{datetime.now().strftime('%Y-%m-%d')}")
if os.path.exists(path) is False:
    os.makedirs(path)

date = None
files = set()


def start(file):
    global date

    if date is None:
        date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    text = (f"\n---------\n"
            f"SESSION START: {date}\n"
            f"---------\n")

    if file not in files:
        with open(os.path.join(path, file), 'a+', encoding="utf-8") as f:
            f.write(text)
        files.add(file)


def log(message, file: str = "log.txt"):

    if file.endswith(".txt") is False:
        file = file + ".txt"

    start(file)

    text = f"    <LOG: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}>    {message}\n"

    with open(os.path.join(path, "log.txt"), "a+", encoding="utf-8") as f:
        f.write(text)

    if file != "log.txt":
        with open(os.path.join(path, file), "a+", encoding="utf-8") as f:
            f.write(text)
