# 🌤️ Burgos Meteo

App meteo con interfaccia CLI ricca e web app responsive.
Progetto d'esame — Python Developer Course.

---

## Funzionalità

- **Ricerca meteo** per qualsiasi città nel mondo
- **Previsioni 7 giorni** con temperatura, precipitazioni e condizioni
- **Confronto tra città** — meteo di due città affiancato
- **Cache locale** — i dati vengono salvati per 1 ora per evitare chiamate ripetute
- **Grafici nel terminale** — temperature e precipitazioni con plotext
- **Web app responsive** — stessa funzionalità accessibile da browser (PC e mobile)
- **Interfaccia multilingua** — EN / IT / ES (solo web app)

---

## Struttura del progetto

```
meteo/
  cli.py                  # Entry point CLI (Typer)
  cache.py                # Cache locale JSON (TTL 1 ora)
  exceptions.py           # Gerarchia eccezioni personalizzate
  validators.py           # Validazione input utente
  models/
    location.py           # Modello Location (Pydantic)
    weather.py            # Modelli CurrentWeather, DailyForecast, WeatherReport
  repositories/
    geocoding_repository.py   # Chiamata API geocoding Open-Meteo
    weather_repository.py     # Chiamata API meteo Open-Meteo
  services/
    weather_service.py    # Coordina geocoding, meteo e cache
  ui/
    display.py            # Tabelle e pannelli (Rich)
    charts.py             # Grafici terminale (Plotext)
    weather_codes.py      # Mapping codici WMO → descrizione + emoji
tests/                    # Suite di test (pytest)
web/                      # Web app (HTML/CSS/JS)
  public/
    index.html
    css/style.css
    js/i18n.js
    js/app.js
  firebase.json
main.py                   # Entry point con fix encoding UTF-8 Windows
pyproject.toml
```

---

## Tecnologie utilizzate

### CLI (Python)
| Libreria | Scopo | Licenza |
|---|---|---|
| `httpx` | Chiamate HTTP all'API | BSD-3-Clause |
| `pydantic` | Validazione e modelli dati | MIT |
| `rich` | Tabelle e output colorato nel terminale | MIT |
| `plotext` | Grafici nel terminale | MIT |
| `typer` | Interfaccia CLI | MIT |
| `pytest` | Test | MIT |

### Web app (Frontend)
| Tecnologia | Scopo |
|---|---|
| HTML / CSS / JS vanilla | Interfaccia web — nessun framework |
| Firebase Hosting | Deploy e hosting statico |

### API esterna
| Servizio | Scopo | Costo |
|---|---|---|
| [Open-Meteo](https://open-meteo.com) | Dati meteo e geocoding | **Gratuito** — no API key |

---

## Installazione e utilizzo (CLI)

### Requisiti
- Python 3.11+
- pip

### Setup
```bash
# Clona il repository
git clone https://github.com/EduBurgos/burgos-meteo.git
cd burgos-meteo

# Crea ambiente virtuale e installa dipendenze
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

pip install -e .
```

### Comandi CLI
```bash
# Meteo di una città
meteo weather Roma

# Meteo senza grafici
meteo weather Roma --no-charts

# Dati freschi (ignora cache)
meteo weather Roma --no-cache

# Confronto tra due o più città
meteo compare Roma Milano

# Aiuto
meteo --help
```

### Web app
Apri `web/public/index.html` nel browser oppure visita la versione online:
👉 **[burgos-meteo su Firebase](#)** *(link da aggiornare dopo il deploy)*

---

## Test

```bash
# Esegui tutti i test
pytest

# Con dettaglio
pytest -v

# Con coverage
pytest --cov=meteo
```

### Cosa coprono i test

| File | Cosa testa |
|---|---|
| `test_validators.py` | Validazione input: città valide, caratteri non permessi, lunghezza |
| `test_models.py` | Modelli Pydantic: costruzione, validazione tipi |
| `test_geocoding_repository.py` | Chiamata API geocoding, mock HTTP, gestione errori |
| `test_weather_repository.py` | Chiamata API meteo, parsing risposta, errori di rete |
| `test_weather_service.py` | Coordinamento service, integrazione con cache |
| `test_compare.py` | Comando compare, fetch parallelo, errori parziali |
| `test_weather_codes.py` | Mapping codici WMO → descrizione e emoji |

---

## Gestione degli errori

Il codice gestisce esplicitamente i seguenti scenari:

| Errore | Comportamento |
|---|---|
| Città non trovata | Messaggio chiaro all'utente |
| Timeout di rete | Errore con indicazione di controllare la connessione |
| Risposta API malformata | Eccezione specifica `ApiResponseError` |
| Cache corrotta o manomessa | Cache miss silenzioso, i dati vengono ri-scaricati |
| Input non valido | Validazione prima di qualsiasi chiamata di rete |

---

## Sicurezza e licenze

### Licenze
Tutte le dipendenze utilizzano licenze **MIT o BSD-3-Clause** — permissive, open source, compatibili con uso personale, didattico e commerciale.

I dati meteo di Open-Meteo sono rilasciati sotto **CC BY 4.0** (Creative Commons Attribution). Per uso non-commerciale è completamente gratuito.

### Privacy
- L'app **non raccoglie né trasmette dati personali**
- L'unico input è il nome di una città (dato pubblico)
- La cache locale (`~/.meteo_cache.json`) contiene solo dati meteo, nessun dato utente
- Nessuna telemetria, tracking o analytics

### Sicurezza del codice
- Input utente validato prima di qualsiasi uso (`validators.py`)
- Chiamate HTTP con **`verify=True` esplicito** (verifica certificati SSL)
- Cache con gestione delle eccezioni di Pydantic per resistere a file corrotti
- Timeout configurato su tutte le chiamate HTTP

---

## Uso responsabile dell'intelligenza artificiale

Questo progetto è stato sviluppato con il supporto di **Claude Code (Anthropic)** come assistente AI.

### Come è stato utilizzato l'AI
- Suggerimento di pattern architetturali (Repository + Service layer)
- Supporto nella scrittura di codice boilerplate (modelli Pydantic, gestione eccezioni)
- Revisione della qualità del codice (sicurezza, licenze, privacy)
- Generazione della struttura della web app (HTML/CSS/JS)

### Responsabilità e revisione
- **Tutto il codice generato è stato letto, compreso e validato** prima di essere accettato
- Le decisioni architetturali principali sono state prese autonomamente
- I test sono stati scritti per verificare che il comportamento del codice corrisponda alle aspettative
- Le vulnerabilità di sicurezza identificate (cache non validata, `verify` SSL implicito) sono state corrette consapevolmente

### Principi seguiti
- L'AI è stata usata come **strumento di supporto**, non come sostituto della comprensione
- Il codice non viene accettato senza capirne il funzionamento
- Le API e le librerie usate sono state scelte e verificate indipendentemente

---

## Autore

**Eduardo Burgos Romero**
[burgosweb.net](https://burgosweb.net) · [GitHub](https://github.com/EduBurgos)

---

## Licenza

Progetto open source rilasciato sotto licenza **MIT**.
