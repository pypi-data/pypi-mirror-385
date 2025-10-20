from .fn import get_in


class BetterDict(dict):
    get_in = get_in
