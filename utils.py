from base64 import b64encode, b64decode


def encode(string):
    return b64encode(string.encode()).decode()


def decode(string):
    return b64decode(string.encode()).decode()
