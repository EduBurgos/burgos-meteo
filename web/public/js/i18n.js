/* =========================================
   TRANSLATIONS — Burgos Meteo
   ========================================= */
const translations = {
  en: {
    nav_portfolio:      '← Portfolio',
    hero_title:         'Weather Forecast',
    hero_sub:           'Search for any city in the world',
    search_placeholder: 'Enter a city name...',
    search_btn:         'Search',
    mode_search:        'Search',
    mode_compare:       'Compare',
    compare_city1:      'First city...',
    compare_city2:      'Second city...',
    compare_btn:        'Compare',
    loading:            'Loading...',
    feels_like:         'Feels like',
    humidity:           'Humidity',
    wind:               'Wind',
    forecast_title:     '7-Day Forecast',
    today:              'Today',
    footer_powered:     'Powered by',
    error_not_found:    "City \"{city}\" not found. Try a different name.",
    error_network:      'Network error. Check your connection.',
    error_api:          'Error fetching weather data. Try again later.',
  },
  it: {
    nav_portfolio:      '← Portfolio',
    hero_title:         'Previsioni Meteo',
    hero_sub:           'Cerca qualsiasi città nel mondo',
    search_placeholder: 'Inserisci il nome di una città...',
    search_btn:         'Cerca',
    mode_search:        'Cerca',
    mode_compare:       'Confronta',
    compare_city1:      'Prima città...',
    compare_city2:      'Seconda città...',
    compare_btn:        'Confronta',
    loading:            'Caricamento...',
    feels_like:         'Percepita',
    humidity:           'Umidità',
    wind:               'Vento',
    forecast_title:     'Previsioni 7 giorni',
    today:              'Oggi',
    footer_powered:     'Powered by',
    error_not_found:    "Città \"{city}\" non trovata. Prova con un altro nome.",
    error_network:      'Errore di rete. Controlla la connessione.',
    error_api:          'Errore nel recupero dei dati meteo. Riprova più tardi.',
  },
  es: {
    nav_portfolio:      '← Portfolio',
    hero_title:         'Pronóstico del Tiempo',
    hero_sub:           'Busca cualquier ciudad del mundo',
    search_placeholder: 'Introduce el nombre de una ciudad...',
    search_btn:         'Buscar',
    mode_search:        'Buscar',
    mode_compare:       'Comparar',
    compare_city1:      'Primera ciudad...',
    compare_city2:      'Segunda ciudad...',
    compare_btn:        'Comparar',
    loading:            'Cargando...',
    feels_like:         'Sensación',
    humidity:           'Humedad',
    wind:               'Viento',
    forecast_title:     'Pronóstico 7 días',
    today:              'Hoy',
    footer_powered:     'Powered by',
    error_not_found:    "Ciudad \"{city}\" no encontrada. Prueba con otro nombre.",
    error_network:      'Error de red. Comprueba tu conexión.',
    error_api:          'Error al obtener datos meteorológicos. Inténtalo más tarde.',
  }
};

/* =========================================
   I18N ENGINE
   ========================================= */
function setLang(lang) {
  if (!translations[lang]) {
    lang = 'en';
  }
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = translations[lang][key] ?? translations['en'][key];
    if (text !== undefined) el.innerHTML = text;
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    const text = translations[lang][key] ?? translations['en'][key];
    if (text !== undefined) el.placeholder = text;
  });

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.toLowerCase() === lang);
  });

  // Re-render weather if a result is visible
  if (typeof rerenderWeather === 'function') rerenderWeather();
}

/* =========================================
   INIT — runs on page load
   ========================================= */
const savedLang = localStorage.getItem('lang') || 'en';
setLang(savedLang);
