
from leftpad import left_pad
from tinyhtml import html, h


def welcome_page(name, size):
    return html(lang="en")(
        h("head")(
            h("meta", charset="utf-8"),
            h("style")(f'p{{font-size:{size}}}')
        ),
        h("body")(
            h("p")("Welcome to Knowledge Grid, " + name)
        )
    ).render()

def generate_page(input):
    return welcome_page(left_pad(input['name'], input['spaces']), input['size'])
