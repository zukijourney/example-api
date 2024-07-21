import typer
import os

app = typer.Typer()

@app.command()
def start_server(workers: int = 1, environment: str = "dev"):
    """Starts the API server."""

    os.system(f"""
        python -B -m granian api:app
        --interface asginl
        --port {8000 if environment == 'dev' else 5000}
        --log-level debug
        --workers {workers}
    """.replace("\n", " "))

if __name__ in ["__main__", "__init__"]:
    app()