/* =========================================
   CONSTANTS
   ========================================= */
const GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search';
const WEATHER_URL   = 'https://api.open-meteo.com/v1/forecast';

/* =========================================
   WEATHER CODES — WMO standard
   ========================================= */
const WEATHER_CODES = {
  0:  { en: 'Clear sky',              it: 'Cielo sereno',              es: 'Cielo despejado',            icon: '☀️'  },
  1:  { en: 'Mainly clear',           it: 'Prevalentemente sereno',    es: 'Mayormente despejado',       icon: '🌤️' },
  2:  { en: 'Partly cloudy',          it: 'Parzialmente nuvoloso',     es: 'Parcialmente nublado',       icon: '⛅'  },
  3:  { en: 'Overcast',               it: 'Nuvoloso',                  es: 'Nublado',                    icon: '☁️'  },
  45: { en: 'Fog',                    it: 'Nebbia',                    es: 'Niebla',                     icon: '🌫️' },
  48: { en: 'Icy fog',                it: 'Nebbia con brina',          es: 'Niebla helada',              icon: '🌫️' },
  51: { en: 'Light drizzle',          it: 'Pioggerella leggera',       es: 'Llovizna ligera',            icon: '🌦️' },
  53: { en: 'Moderate drizzle',       it: 'Pioggerella moderata',      es: 'Llovizna moderada',          icon: '🌦️' },
  55: { en: 'Dense drizzle',          it: 'Pioggerella fitta',         es: 'Llovizna densa',             icon: '🌧️' },
  61: { en: 'Light rain',             it: 'Pioggia leggera',           es: 'Lluvia ligera',              icon: '🌧️' },
  63: { en: 'Moderate rain',          it: 'Pioggia moderata',          es: 'Lluvia moderada',            icon: '🌧️' },
  65: { en: 'Heavy rain',             it: 'Pioggia forte',             es: 'Lluvia fuerte',              icon: '🌧️' },
  71: { en: 'Light snow',             it: 'Neve leggera',              es: 'Nieve ligera',               icon: '🌨️' },
  73: { en: 'Moderate snow',          it: 'Neve moderata',             es: 'Nieve moderada',             icon: '❄️'  },
  75: { en: 'Heavy snow',             it: 'Neve forte',                es: 'Nieve fuerte',               icon: '❄️'  },
  77: { en: 'Snow grains',            it: 'Granuli di neve',           es: 'Gránulos de nieve',          icon: '🌨️' },
  80: { en: 'Light showers',          it: 'Rovesci leggeri',           es: 'Aguaceros ligeros',          icon: '🌦️' },
  81: { en: 'Moderate showers',       it: 'Rovesci moderati',          es: 'Aguaceros moderados',        icon: '🌧️' },
  82: { en: 'Violent showers',        it: 'Rovesci violenti',          es: 'Aguaceros violentos',        icon: '⛈️'  },
  85: { en: 'Light snow showers',     it: 'Rovesci di neve leggeri',   es: 'Aguaceros de nieve ligeros', icon: '🌨️' },
  86: { en: 'Heavy snow showers',     it: 'Rovesci di neve forti',     es: 'Aguaceros de nieve fuertes', icon: '❄️'  },
  95: { en: 'Thunderstorm',           it: 'Temporale',                 es: 'Tormenta',                   icon: '⛈️'  },
  96: { en: 'Thunderstorm w/ hail',   it: 'Temporale con grandine',    es: 'Tormenta con granizo',       icon: '⛈️'  },
  99: { en: 'Heavy thunderstorm',     it: 'Temporale, grandine forte', es: 'Tormenta con granizo fuerte',icon: '⛈️'  },
};

function getWeatherInfo(code, lang) {
  const entry = WEATHER_CODES[code] || {
    en: 'Unknown', it: 'Sconosciuto', es: 'Desconocido', icon: '❓'
  };
  return { desc: entry[lang] || entry.en, icon: entry.icon };
}

/* =========================================
   STATE — last fetched data for re-render on lang change
   ========================================= */
let lastLocation = null;
let lastWeatherData = null;

/* =========================================
   DOM ELEMENTS
   ========================================= */
const cityInput        = document.getElementById('city-input');
const searchBtn        = document.getElementById('search-btn');
const cityInputA       = document.getElementById('city-input-a');
const cityInputB       = document.getElementById('city-input-b');
const compareBtn       = document.getElementById('compare-btn');
const loadingEl        = document.getElementById('loading');
const errorEl          = document.getElementById('error-msg');
const resultSection    = document.getElementById('result-section');
const currentWeatherEl = document.getElementById('current-weather');
const forecastEl       = document.getElementById('forecast-container');
const compareSection   = document.getElementById('compare-section');
const compareCardsEl   = document.getElementById('compare-cards');
const hamburger        = document.getElementById('hamburger');
const navLinks         = document.getElementById('nav-links');

/* =========================================
   HELPERS
   ========================================= */
function getLang() {
  return localStorage.getItem('lang') || 'en';
}

function t(key, vars = {}) {
  const lang = getLang();
  let text = (translations[lang] && translations[lang][key]) || translations['en'][key] || key;
  Object.entries(vars).forEach(([k, v]) => {
    text = text.replace(`{${k}}`, v);
  });
  return text;
}

function setLoading(state) {
  loadingEl.classList.toggle('hidden', !state);
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove('hidden');
}

function hideError() {
  errorEl.classList.add('hidden');
}

function hideResult() {
  resultSection.classList.add('hidden');
}

function hideCompare() {
  compareSection.classList.add('hidden');
}

/* =========================================
   MODE TOGGLE
   ========================================= */
let currentMode = 'search';

function setMode(mode) {
  currentMode = mode;

  document.getElementById('mode-search').classList.toggle('active', mode === 'search');
  document.getElementById('mode-compare').classList.toggle('active', mode === 'compare');
  document.getElementById('panel-search').classList.toggle('hidden', mode !== 'search');
  document.getElementById('panel-compare').classList.toggle('hidden', mode !== 'compare');

  hideError();
  hideResult();
  hideCompare();
}

function hideCompare() {
  compareSection.classList.add('hidden');
}

/* =========================================
   EVENT LISTENERS
   ========================================= */
searchBtn.addEventListener('click', handleSearch);
compareBtn.addEventListener('click', handleCompare);

cityInput.addEventListener('keydown', e => {
  if (e.key === 'Enter') handleSearch();
});

[cityInputA, cityInputB].forEach(input => {
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') handleCompare();
  });
});

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active');
  navLinks.classList.toggle('open');
  hamburger.setAttribute('aria-expanded', navLinks.classList.contains('open'));
});

navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navLinks.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  });
});

/* =========================================
   MAIN FLOW — single city
   ========================================= */
async function handleSearch() {
  const city = cityInput.value.trim();
  if (!city) return;

  setLoading(true);
  hideError();
  hideResult();
  hideCompare();

  try {
    lastLocation = await geocode(city);
    lastWeatherData = await fetchWeather(lastLocation);
    renderWeather(lastLocation, lastWeatherData);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

/* =========================================
   MAIN FLOW — compare two cities
   ========================================= */
let lastCompareData = null;

async function handleCompare() {
  const cityA = cityInputA.value.trim();
  const cityB = cityInputB.value.trim();
  if (!cityA || !cityB) return;

  setLoading(true);
  hideError();
  hideResult();
  hideCompare();

  try {
    // Fetch both cities in parallel
    const [locA, locB] = await Promise.all([geocode(cityA), geocode(cityB)]);
    const [dataA, dataB] = await Promise.all([fetchWeather(locA), fetchWeather(locB)]);

    lastCompareData = [{ location: locA, data: dataA }, { location: locB, data: dataB }];
    renderCompare(lastCompareData);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

/* Called by i18n.js when language changes */
function rerenderWeather() {
  if (currentMode === 'search' && lastLocation && lastWeatherData) {
    renderWeather(lastLocation, lastWeatherData);
  }
  if (currentMode === 'compare' && lastCompareData) {
    renderCompare(lastCompareData);
  }
}

/* =========================================
   API CALLS
   ========================================= */
async function geocode(city) {
  const url = new URL(GEOCODING_URL);
  url.searchParams.set('name', city);
  url.searchParams.set('count', '1');
  url.searchParams.set('language', getLang());
  url.searchParams.set('format', 'json');

  let resp;
  try {
    resp = await fetch(url, { mode: 'cors' });
  } catch {
    throw new Error(t('error_network'));
  }
  if (!resp.ok) throw new Error(t('error_api'));

  const data = await resp.json();
  if (!data.results || data.results.length === 0) {
    throw new Error(t('error_not_found', { city }));
  }

  const r = data.results[0];
  return {
    name:      r.name,
    country:   r.country || '',
    latitude:  r.latitude,
    longitude: r.longitude,
    timezone:  r.timezone || 'auto',
  };
}

async function fetchWeather(location) {
  const url = new URL(WEATHER_URL);
  url.searchParams.set('latitude',     location.latitude);
  url.searchParams.set('longitude',    location.longitude);
  url.searchParams.set('current',      'temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code');
  url.searchParams.set('daily',        'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code');
  url.searchParams.set('timezone',     location.timezone);
  url.searchParams.set('forecast_days','7');

  let resp;
  try {
    resp = await fetch(url, { mode: 'cors' });
  } catch {
    throw new Error(t('error_network'));
  }
  if (!resp.ok) throw new Error(t('error_api'));

  return resp.json();
}

/* =========================================
   RENDER
   ========================================= */
function renderWeather(location, data) {
  const lang    = getLang();
  const current = data.current;
  const daily   = data.daily;

  const { desc, icon } = getWeatherInfo(current.weather_code, lang);

  /* --- Current weather card --- */
  currentWeatherEl.innerHTML = `
    <div class="current-card">
      <div class="current-location">
        <h2>${location.name}${location.country ? `, ${location.country}` : ''}</h2>
        <p class="current-time">${formatDateTime(current.time, lang)}</p>
      </div>
      <div class="current-main">
        <div class="current-icon">${icon}</div>
        <div>
          <div class="current-temp">${Math.round(current.temperature_2m)}°C</div>
          <div class="current-desc">${desc}</div>
        </div>
      </div>
      <div class="current-details">
        <div class="detail-chip">
          <span>🌡️</span>
          <span class="detail-label">${t('feels_like')}</span>
          <span class="detail-value">${Math.round(current.apparent_temperature)}°C</span>
        </div>
        <div class="detail-chip">
          <span>💧</span>
          <span class="detail-label">${t('humidity')}</span>
          <span class="detail-value">${current.relative_humidity_2m}%</span>
        </div>
        <div class="detail-chip">
          <span>💨</span>
          <span class="detail-label">${t('wind')}</span>
          <span class="detail-value">${Math.round(current.wind_speed_10m)} km/h</span>
        </div>
      </div>
    </div>
  `;

  /* --- 7-day forecast --- */
  const cards = daily.time.map((dateStr, i) => {
    const { desc: dayDesc, icon: dayIcon } = getWeatherInfo(daily.weather_code[i], lang);
    const precip = daily.precipitation_sum[i] || 0;
    return `
      <div class="forecast-card">
        <div class="forecast-day">${formatDay(dateStr, lang)}</div>
        <div class="forecast-icon">${dayIcon}</div>
        <div class="forecast-desc">${dayDesc}</div>
        <div class="forecast-temps">
          <span class="temp-max">${Math.round(daily.temperature_2m_max[i])}°</span>
          <span class="temp-min">${Math.round(daily.temperature_2m_min[i])}°</span>
        </div>
        ${precip > 0 ? `<div class="forecast-precip">💧 ${precip.toFixed(1)} mm</div>` : ''}
      </div>
    `;
  }).join('');

  forecastEl.innerHTML = `
    <h3 class="forecast-title">${t('forecast_title')}</h3>
    <div class="forecast-cards">${cards}</div>
  `;

  resultSection.classList.remove('hidden');
}

/* =========================================
   RENDER — compare two cities
   ========================================= */
function renderCompare(results) {
  const lang = getLang();
  const [a, b] = results;

  const tempA = Math.round(a.data.current.temperature_2m);
  const tempB = Math.round(b.data.current.temperature_2m);
  const humA  = a.data.current.relative_humidity_2m;
  const humB  = b.data.current.relative_humidity_2m;
  const windA = Math.round(a.data.current.wind_speed_10m);
  const windB = Math.round(b.data.current.wind_speed_10m);

  compareCardsEl.innerHTML = [
    buildCompareCard(a.location, a.data, lang, { temp: tempA, hum: humA, wind: windA }, { temp: tempB, hum: humB, wind: windB }),
    buildCompareCard(b.location, b.data, lang, { temp: tempB, hum: humB, wind: windB }, { temp: tempA, hum: humA, wind: windA }),
  ].join('');

  compareSection.classList.remove('hidden');
}

function buildCompareCard(location, data, lang, mine, other) {
  const { desc, icon } = getWeatherInfo(data.current.weather_code, lang);

  const tempClass = mine.temp > other.temp ? 'worse' : mine.temp < other.temp ? 'better' : '';
  const humClass  = mine.hum  < other.hum  ? 'better' : mine.hum > other.hum  ? 'worse'  : '';
  const windClass = mine.wind < other.wind ? 'better' : mine.wind > other.wind ? 'worse'  : '';

  const maxToday = Math.round(data.daily.temperature_2m_max[0]);
  const minToday = Math.round(data.daily.temperature_2m_min[0]);

  return `
    <div class="compare-card">
      <div class="city-name">📍 ${location.name}${location.country ? `, ${location.country}` : ''}</div>
      <div class="condition">${icon}</div>
      <div class="big-temp">${mine.temp}°C</div>
      <div class="condition-text">${desc}</div>
      <div class="compare-stat">
        <span class="stat-label">🌡️ ${t('feels_like')}</span>
        <span class="stat-val">${Math.round(data.current.apparent_temperature)}°C</span>
      </div>
      <div class="compare-stat">
        <span class="stat-label">💧 ${t('humidity')}</span>
        <span class="stat-val ${humClass}">${mine.hum}%</span>
      </div>
      <div class="compare-stat">
        <span class="stat-label">💨 ${t('wind')}</span>
        <span class="stat-val ${windClass}">${mine.wind} km/h</span>
      </div>
      <div class="compare-stat">
        <span class="stat-label">📅 Max / Min</span>
        <span class="stat-val">
          <span class="temp-max">${maxToday}°</span>
          /
          <span class="temp-min">${minToday}°</span>
        </span>
      </div>
      <hr class="compare-divider">
      <div class="compare-forecast">
        ${data.daily.time.map((dateStr, i) => {
          const { icon: dayIcon } = getWeatherInfo(data.daily.weather_code[i], lang);
          return `
            <div class="compare-day">
              <div class="compare-day-label">${formatDay(dateStr, lang)}</div>
              <div class="compare-day-icon">${dayIcon}</div>
              <div class="compare-day-temps">
                <span class="temp-max">${Math.round(data.daily.temperature_2m_max[i])}°</span>
                <span class="temp-min">${Math.round(data.daily.temperature_2m_min[i])}°</span>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

function formatDateTime(iso, lang) {
  const locale = { en: 'en-US', it: 'it-IT', es: 'es-ES' }[lang] || 'en-US';
  const date = new Date(iso);
  return date.toLocaleDateString(locale, {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
  });
}

function formatDay(dateStr, lang) {
  // Add noon time to avoid UTC-offset day shifts
  const date   = new Date(dateStr + 'T12:00:00');
  const today  = new Date();
  const locale = { en: 'en-US', it: 'it-IT', es: 'es-ES' }[lang] || 'en-US';

  if (date.toDateString() === today.toDateString()) return t('today');

  return date.toLocaleDateString(locale, { weekday: 'short', day: 'numeric', month: 'short' });
}
