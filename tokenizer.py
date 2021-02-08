import re

from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str


def tokenizer(code):
    token_spec = [
        ("URL", r"<https?://[\w/:%#\$&\?\(\)~\.=\+\-]+>"),
        ("USERNAME", r"<@[A-Z0-9]+>"),
        ("IPv4", r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}"),
        ("ID", r"[A-Za-z]+"),
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    ID_spec = {"QR", "PING"}
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    code_memo = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ('NEWLINE', 'SKIP', 'MISMATCH'):
            continue
        elif kind == "ID":
            if value.upper() in ID_spec:
                kind = value.upper()
        if value[0] == "<" and value[-1] == ">":
            value = value[1:-1]
        code_memo.append(Token(kind, value))
        # print(kind, value)

    # print(code_memo)
    return code_memo


if __name__ == '__main__':
    test_patterns = [
        {
            "in": "<@U01LJNE6FC7> qr <https://google.com/>",
            "out": ["USERNAME", "QR", "URL"]
        },
        {
            "in": "<@C011712375>    ping     192.2.0.1",
            "out": ["USERNAME", "PING", "IPv4"]
        }
    ]
    for tp in test_patterns:
        result = tokenizer(tp["in"])
        assert [r.type for r in result] == tp["out"]
