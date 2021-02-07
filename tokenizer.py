import re

from typing import NamedTuple


class Token(NamedTuple):
    type: str
    value: str


def tokenizer(code):
    token_spec = [
        ("URL", r"<https?://[\w/:%#\$&\?\(\)~\.=\+\-]+>"),
        ("USERNAME", r"<@[A-Z0-9]+>"),
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
                kind = value
        # print(kind, value)
        code_memo.append(Token(kind, value))
    print(code_memo)
    return code_memo


sample_in = """
<@U01LJNE6FC7> qr <https://google.com/>
"""

if __name__ == '__main__':
    tokenizer(sample_in)
