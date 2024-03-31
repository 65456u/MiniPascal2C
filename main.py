import lark


def main():
    parser = lark.Lark(r"""
        start: "hello" NAME "!"

        %import common.CNAME -> NAME
        %import common.WS
        %ignore WS
    """)
    print(parser.parse("hello World!").pretty())
    return 0


main()
