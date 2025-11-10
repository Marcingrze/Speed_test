# Internet Speed Test Tool

Narzędzie do testowania prędkości połączenia internetowego z zaawansowaną obsługą błędów, konfiguracją i walidacją wyników.

## 📋 Opis

To jest profesjonalne narzędzie do testowania prędkości internetu napisane w Pythonie, które wykorzystuje serwis speedtest.net do pomiaru:
- Prędkości pobierania (download)
- Prędkości wysyłania (upload)  
- Opóźnienia (ping/latencja)

### ✨ Główne funkcjonalności

- **Zaawansowana obsługa błędów** - automatyczne ponowne próby przy przejściowych problemach sieciowych
- **Elastyczna konfiguracja** - wszystkie parametry można dostosować przez plik JSON
- **Walidacja wyników** - inteligentne ostrzeżenia o nieprawdopodobnych wynikach
- **Progresywne informacje** - szczegółowe informacje o postępie testów
- **Sprawdzenie łączności** - wstępna weryfikacja połączenia internetowego
- **Przyjazny interfejs** - czytelny wyświetlacz wyników z formatowaniem

## 🚀 Szybki start

### Wymagania systemowe

- Python 3.6+
- Połączenie internetowe
- Środowisko wirtualne (zalecane)

### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone <repository-url>
cd Speed_test
```

2. **Aktywuj środowisko wirtualne**
```bash
source ebv/bin/activate
```

3. **Zainstaluj zależności**
```bash
pip install -r requirements.txt
```

### Podstawowe użycie

```bash
# Uruchom test z domyślną konfiguracją
python sp.py

# Utwórz plik konfiguracyjny do dostosowania
python sp.py --create-config
```

## ⚙️ Konfiguracja

### Utworzenie pliku konfiguracyjnego

```bash
python sp.py --create-config
```

To utworzy plik `speedtest_config.json` z domyślnymi ustawieniami.

### Dostępne opcje konfiguracji

```json
{
  "bits_to_mbps": 1000000,                    // Konwersja bitów na Mbps
  "connectivity_check_timeout": 10,           // Timeout sprawdzenia łączności (s)
  "speedtest_timeout": 60,                    // Timeout głównego testu (s)
  "max_retries": 3,                          // Maksymalna liczba ponownych prób
  "retry_delay": 2,                          // Opóźnienie między próbami (s)
  "max_typical_speed_gbps": 1,               // Próg typowej prędkości (Gbps)
  "max_reasonable_speed_gbps": 10,           // Maksymalna rozsądna prędkość (Gbps)
  "max_typical_ping_ms": 1000,               // Próg typowego pingu (ms)
  "max_reasonable_ping_ms": 10000,           // Maksymalny rozsądny ping (ms)
  "show_detailed_progress": true             // Szczegółowe informacje o postępie
}
```

## 📊 Przykład użycia

### Standardowe uruchomienie

```bash
$ python sp.py

Internet Speed Test Tool
-------------------------
Using default configuration (create speedtest_config.json to customize).
Checking network connectivity...
Network connection detected.
Initializing speed test...
Fetching server list...
Selecting best server...
Using server: Orange Polska (Warsaw)
Testing download speed... (typically takes 10-30 seconds)
Download test completed in 12.3 seconds
Testing upload speed... (typically takes 15-45 seconds)
Upload test completed in 18.7 seconds

========================================
SPEED TEST RESULTS
========================================
Download: 85.42 Mbps
Upload:   45.67 Mbps
Ping:     12.4 ms
========================================
```

### Uruchomienie z własną konfiguracją

```bash
# 1. Utwórz plik konfiguracyjny
python sp.py --create-config

# 2. Edytuj speedtest_config.json według potrzeb
nano speedtest_config.json

# 3. Uruchom z własną konfiguracją
python sp.py
```

## 🔧 Struktura projektu

```
Speed_test/
├── sp.py                           # Główna aplikacja
├── requirements.txt                # Zależności Pythona
├── speedtest_config.json.example   # Przykład konfiguracji
├── speedtest_config.json          # Konfiguracja użytkownika (ignorowana przez git)
├── README.md                      # Ta dokumentacja
├── ebv/                          # Środowisko wirtualne Pythona
│   ├── bin/                       # Pliki wykonywalne
│   └── lib/                       # Pakiety Pythona
└── .gitignore                     # Wzorce ignorowane przez git
```

## 🛠️ Funkcjonalności zaawansowane

### Obsługa błędów

- **Automatyczne ponawianie**: Przy przejściowych problemach sieciowych
- **Sprawdzenie łączności**: Weryfikacja połączenia przed testem
- **Graceful degradation**: Czytelne komunikaty o błędach
- **Walidacja wyników**: Ostrzeżenia o nietypowych wynikach

### Inteligentna walidacja

Tool automatycznie wykrywa i ostrzega o:
- Nieprawdopodobnie wysokich prędkościach (>1 Gbps)
- Ekstremalnie wysokich opóźnieniach (>1000 ms)
- Bardzo niskich prędkościach (<1 Mbps)
- Błędnych danych pomiarowych

### Kody wyjścia

- `0`: Test zakończony pomyślnie
- `1`: Test zakończony błędem (brak internetu, błąd pomiaru)

## 🐛 Rozwiązywanie problemów

### Brak połączenia internetowego

```
Error: No internet connection detected.
Please check your network connection and try again.
```
**Rozwiązanie**: Sprawdź połączenie internetowe i spróbuj ponownie.

### Błędy konfiguracji

```
Warning: Could not load config file speedtest_config.json: ...
Using default configuration.
```
**Rozwiązanie**: Sprawdź składnię JSON w pliku konfiguracyjnym lub usuń plik, aby użyć domyślnej konfiguracji.

### Wysokie opóźnienia/niskie prędkości

```
Warning: High latency (1500 ms) detected - connection may be slow
```
**Rozwiązanie**: To jest informacyjne - wskazuje na problemy z łączem internetowym.

## 📦 Zależności

- **speedtest-cli** (v2.1.3): Biblioteka do testowania prędkości internetu
- **Python 3.6+**: Ze wsparciem dla type hints

## 🤝 Rozwój projektu

### Środowisko deweloperskie

```bash
# Aktywacja środowiska
source ebv/bin/activate

# Instalacja zależności
pip install -r requirements.txt

# Testowanie zmian
python sp.py
```

### Dodawanie nowych funkcji

1. Edytuj `sp.py`
2. Testuj zmiany w różnych scenariuszach sieciowych
3. Aktualizuj dokumentację w razie potrzeby
4. Commituj zmiany z opisowymi komunikatami

## 📄 Licencja

Projekt jest dostępny na licencji open source. Szczegóły w pliku LICENSE.

## 🔗 Linki użyteczne

- [speedtest-cli documentation](https://pypi.org/project/speedtest-cli/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [JSON Configuration Format](https://www.json.org/)

---

**Uwaga**: Ten tool wymaga aktywnego połączenia internetowego do prawidłowego działania. Wszystkie testy są przeprowadzane z wykorzystaniem serwisów speedtest.net.