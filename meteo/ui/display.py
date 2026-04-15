from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from meteo.models.weather import WeatherReport
from meteo.ui.weather_codes import get_description, get_icon

console = Console(legacy_windows=False)


def display_report(report: WeatherReport) -> None:
    """Visualizza il report meteo: header, meteo attuale e previsioni."""
    _display_header(report)
    _display_current(report)
    _display_forecast_table(report)


def _display_header(report: WeatherReport) -> None:
    icon = get_icon(report.current.weather_code)
    desc = get_description(report.current.weather_code)
    console.print(
        Panel(
            f'[bold cyan]{icon}{report.location.name},'
            f' {report.location.country}[/bold cyan]\n'
            f'[dim]{desc}[/dim]',
            title='[bold white]🌍 Meteo App[/bold white]',
            border_style='cyan',
            padding=(1, 4),
        )
    )


def _display_current(report: WeatherReport) -> None:
    c = report.current
    panels = [
        Panel(
            f'[bold yellow]{c.temperature}°C[/bold yellow]\n'
            f'[dim]Percepita: {c.apparent_temperature}°C[/dim]',
            title='🌡️  Temperatura',
            border_style='yellow',
        ),
        Panel(
            f'[bold blue]{c.humidity}%[/bold blue]',
            title='💧 Umidità',
            border_style='blue',
        ),
        Panel(
            f'[bold green]{c.wind_speed} km/h[/bold green]',
            title='💨 Vento',
            border_style='green',
        ),
    ]
    console.print(Columns(panels, equal=True, expand=True))


def _display_forecast_table(report: WeatherReport) -> None:
    table = Table(
        title='📅  Previsioni 7 giorni',
        box=box.ROUNDED,
        border_style='cyan',
        show_lines=True,
        title_style='bold cyan',
    )
    table.add_column('Data',       style='cyan',  no_wrap=True)
    table.add_column('Condizioni', justify='left')
    table.add_column('Max',        justify='right', style='bold red')
    table.add_column('Min',        justify='right', style='bold blue')
    table.add_column('Pioggia',    justify='right', style='blue')

    for day in report.forecast:
        icon = get_icon(day.weather_code)
        desc = get_description(day.weather_code)
        table.add_row(
            day.date.strftime('%a %d %b'),
            f'{icon}{desc}',
            f'{day.temp_max}°C',
            f'{day.temp_min}°C',
            f'{day.precipitation:.1f} mm',
        )

    console.print(table)


def display_comparison(reports: list[WeatherReport]) -> None:
    """Visualizza il meteo attuale di più città in una tabella affiancata."""
    table = Table(
        title='🌍  Confronto meteo tra città',
        box=box.ROUNDED,
        border_style='cyan',
        show_lines=True,
        title_style='bold cyan',
    )
    table.add_column('Metrica', style='bold white', no_wrap=True)
    for report in reports:
        label = f'{report.location.name}\n[dim]{report.location.country}[/dim]'
        table.add_column(label, justify='center')

    rows = [
        ('🌡️  Temperatura',   lambda r: f'[bold yellow]{r.current.temperature}°C[/bold yellow]'),
        ('🌡️  Percepita',     lambda r: f'[dim]{r.current.apparent_temperature}°C[/dim]'),
        ('💧 Umidità',        lambda r: f'[bold blue]{r.current.humidity}%[/bold blue]'),
        ('💨 Vento',          lambda r: f'[bold green]{r.current.wind_speed} km/h[/bold green]'),
        ('🌤️  Condizioni',    lambda r: f'{get_icon(r.current.weather_code)}{get_description(r.current.weather_code)}'),
    ]
    for label, fmt in rows:
        table.add_row(label, *[fmt(r) for r in reports])

    console.print(table)
