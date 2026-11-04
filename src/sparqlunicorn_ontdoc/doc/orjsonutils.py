import orjson


def _encode_options(indent=None, sort_keys=False):
    options = orjson.OPT_NON_STR_KEYS
    if indent is not None:
        if indent <= 2:
            options |= orjson.OPT_INDENT_2
        elif indent <= 4:
            options |= orjson.OPT_INDENT_4
        else:
            raise ValueError("orjson supports JSON indentation up to 4 spaces")
    if sort_keys:
        options |= orjson.OPT_SORT_KEYS
    return options


def dumps(value, *, indent=None, separators=None, sort_keys=False):
    if separators not in (None, (",", ":")):
        raise ValueError("orjson only supports compact JSON separators")
    return orjson.dumps(value, option=_encode_options(indent, sort_keys)).decode("utf-8")


def dump(value, file, *, indent=None, separators=None, sort_keys=False):
    file.write(dumps(value, indent=indent, separators=separators, sort_keys=sort_keys))


def loads(value):
    return orjson.loads(value)


def load(file):
    return loads(file.read())
