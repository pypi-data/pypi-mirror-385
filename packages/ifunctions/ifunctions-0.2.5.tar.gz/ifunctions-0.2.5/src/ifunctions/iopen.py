IOPEN_BUFFER = 65536
IOPEN_ENCODE = "utf-8"


def iopen(path, data=None, append=False):
    if data is None:
        return file_read(path)
    if append:
        return file_append(path, data)
    return file_write(path, data)


def file_read(path):
    with open(path, "r", encoding=IOPEN_ENCODE, buffering=IOPEN_BUFFER) as f:
        return f.read()


def file_write(path, data: str):
    with open(path, "w", encoding=IOPEN_ENCODE, buffering=IOPEN_BUFFER) as f:
        return f.write(data)


def file_append(path, data: str):
    with open(path, "a", encoding=IOPEN_ENCODE, buffering=IOPEN_BUFFER) as f:
        return f.write(data)


def url_get(path): ...
def url_post(path, data: dict): ...
