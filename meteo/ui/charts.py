import plotext as plt

from meteo.models.weather import WeatherReport


def display_charts(report: WeatherReport) -> None:
    """Visualizza grafico temperature e precipitazioni nel terminale."""
    _display_temperature_chart(report)
    _display_precipitation_chart(report)


def _display_temperature_chart(report: WeatherReport) -> None:
    dates = [day.date.strftime('%d/%m/%Y') for day in report.forecast]
    max_temps = [day.temp_max for day in report.forecast]
    min_temps = [day.temp_min for day in report.forecast]

    plt.clf()
    plt.theme('dark')
    plt.plot(dates, max_temps, label='Max °C', color='red', marker='braille')
    plt.plot(dates, min_temps, label='Min °C', color='blue', marker='braille')
    plt.title(f'🌡️  Temperature — {report.location.name}')
    plt.xlabel('Data')
    plt.ylabel('°C')
    plt.show()


def _display_precipitation_chart(report: WeatherReport) -> None:
    dates = [day.date.strftime('%d/%m/%Y') for day in report.forecast]
    precipitation = [day.precipitation for day in report.forecast]

    plt.clf()
    plt.theme('dark')
    plt.bar(dates, precipitation, label='Precipitazioni mm', color='blue')
    plt.title(f'🌧️  Precipitazioni — {report.location.name}')
    plt.xlabel('Data')
    plt.ylabel('mm')
    plt.show()
