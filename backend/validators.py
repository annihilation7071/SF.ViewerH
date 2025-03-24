import re


def http_proxy(s: str) -> bool:
    math = re.fullmatch(r"^http(s)?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$", s)
    return True if math else False


def cookies(s: str) -> bool:
    matn = re.fullmatch(r"([a-zA-Z_\.\d\-\|]*=[a-zA-Z_\.\d\-\|]*)(; )?", s)
    return True if matn else False