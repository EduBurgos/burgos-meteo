from concurrent.futures import ThreadPoolExecutor, as_completed

import typer
from rich.console import Console

from meteo.exceptions import (
    ApiError, ApiResponseError, CityNotFoundError,
    InvalidCityInputError, MeteoError, NetworkError)
from meteo.services.weather_service import WeatherService
from meteo.ui.charts import display_charts
from meteo.ui.display import display_comparison, display_report

app = typer.Typer(
    name='meteo',
    help='Visualizza meteo attuale e previsioni per qualsiasi città.',
    add_completion=False,
)

console = Console(legacy_windows=False)
_service = WeatherService()


@app.command()
def weather(
    city: str = typer.Argument(..., help="Nome della città (es. 'Roma')"),
    no_charts: bool = typer.Option(
        False, '--no-charts', help='Disabilita i grafici'),
    no_cache: bool = typer.Option(
        False, '--no-cache', help='Ignora la cache e recupera dati freschi'),
) -> None:
    """Mostra meteo attuale, previsioni 7 giorni e grafici."""
    try:
        status_msg = (
            f'[bold cyan]Recupero dati per '
            f'[italic]{city}[/italic]...[/bold cyan]')
        with console.status(status_msg):
            report = _service.get_report(city, use_cache=not no_cache)

        display_report(report)

        if not no_charts:
            display_charts(report)

    except InvalidCityInputError as exc:
        console.print(f'\n[bold red]✗ Input non valido:[/bold red] {exc}')
        raise typer.Exit(code=1)
    except CityNotFoundError as exc:
        console.print(f'\n[bold red]✗ Città non trovata:[/bold red] {exc}')
        raise typer.Exit(code=1)
    except NetworkError as exc:
        console.print(f'\n[bold red]✗ Errore di rete:[/bold red] {exc}')
        raise typer.Exit(code=1)
    except ApiError as exc:
        console.print(f'\n[bold red]✗ Errore API:[/bold red] {exc}')
        raise typer.Exit(code=1)
    except ApiResponseError as exc:
        console.print(
            f'\n[bold red]✗ Risposta inattesa:[/bold red] {exc}')
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(
            f'\n[bold red]✗ Errore imprevisto:[/bold red] {exc}')
        raise typer.Exit(code=1)


@app.command()
def compare(
    cities: list[str] = typer.Argument(
        ..., help="Nomi delle città da confrontare (es. Roma Milano Napoli)"),
    no_cache: bool = typer.Option(
        False, '--no-cache', help='Ignora la cache e recupera dati freschi'),
) -> None:
    """Confronta il meteo attuale di più città affiancate."""
    if len(cities) < 2:
        console.print('[bold red]✗ Specifica almeno due città da confrontare.[/bold red]')
        raise typer.Exit(code=1)

    reports = []
    errors = []

    def fetch(city: str):
        return city, _service.get_report(city, use_cache=not no_cache)

    with console.status('[bold cyan]Recupero dati in corso...[/bold cyan]'):
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(fetch, city): city for city in cities}
            for future in as_completed(futures):
                city = futures[future]
                try:
                    _, report = future.result()
                    reports.append(report)
                except (InvalidCityInputError, CityNotFoundError) as exc:
                    errors.append(f'[yellow]{city}[/yellow]: {exc}')
                except MeteoError as exc:
                    errors.append(f'[yellow]{city}[/yellow]: {exc}')

    for msg in errors:
        console.print(f'[bold red]✗[/bold red] {msg}')

    if len(reports) < 2:
        console.print('[bold red]✗ Dati insufficienti per il confronto.[/bold red]')
        raise typer.Exit(code=1)

    reports.sort(key=lambda r: r.location.name)
    display_comparison(reports)


if __name__ == '__main__':
    app()
