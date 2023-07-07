from typing import Optional

import typer

app = typer.Typer()


@app.command()
def hello(name: str, test: str):
    if name:
        typer.echo(f"Hello {name}1")
    else:
        typer.echo("Hello World!1")






#if __name__ == "__main__":
#    app()