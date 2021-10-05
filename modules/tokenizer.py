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
        ("STUDENT_ID", r"C0[a-z0-9]{6}"),
        # これ以下は一般パターン
        ("ID", r"[A-Za-z]+"),
        ('NEWLINE', r'\n'),
        ('SKIP', r'[ \t]+'),
        ('WORD', r'[^ \t]+'),
    ]
    ID_spec = {"QR", "PING", "OJI", "OMIKUJI", "GAKUSEKI", "HELP"}
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
    code_memo = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ('NEWLINE', 'SKIP', 'MISMATCH'):
            continue
        elif kind == "ID":
            # IDパターン一覧にあるか
            if value.upper() in ID_spec:
                kind = value.upper()
            else:
                kind = "WORD"

        if len(value) > 1 and value[0] == "<" and value[-1] == ">":
            value = value[1:-1]

        # WORDの連続をまとめる
        if len(code_memo) > 0 and code_memo[-1].type == kind == "WORD":
            new_value = " ".join((code_memo[-1].value, value))
            code_memo[-1] = Token(kind, new_value)
        else:
            code_memo.append(Token(kind, value))
        # print(kind, value)

    return code_memo


def test():
    test_patterns = [
        {
            "in": "<@U01LJNE6FC7> qr <https://google.com/>",
            "out": ["USERNAME", "QR", "URL"]
        },
        {
            "in": "<@U01LJNE6FC7>    ping     192.2.0.1",
            "out": ["USERNAME", "PING", "IPv4"]
        },
        {
            "in": "<@U01LJNE6FC7>    oji     hello world あああ",
            "out": ["USERNAME", "OJI", "WORD"]
        },
        {
            "in": "<@U01LJNE6FC7>  gakuseki C0117123",
            "out": ["USERNAME", "GAKUSEKI", "STUDENT_ID"]
        }
    ]
    for tp in test_patterns:
        result = tokenizer(tp["in"])
        assert [r.type for r in result] == tp["out"], f"Err: {tp['in']}, {result}"


if __name__ == '__main__':
    test()
    # t = tokenizer("あいうえお <@U01LJNE6FC7> oji あいうえお hello")
