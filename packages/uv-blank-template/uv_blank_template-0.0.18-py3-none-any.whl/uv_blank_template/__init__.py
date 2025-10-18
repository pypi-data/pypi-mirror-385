import typer

app = typer.Typer(add_completion=False)


@app.command()
def main() -> int:
    print("Hello from uv-blank-template!")
    return 0
