import re


def vali(string):
    return bool(re.compile(r'^[0-9a-zA-Z_]+$').match(string))
