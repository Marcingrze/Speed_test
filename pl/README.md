# Narzędzie do Testowania Prędkości Internetu

Profesjonalne narzędzie do testowania prędkości internetu z zaawansowaną obsługą błędów, konfiguracją i walidacją wyników. Dostępne jako aplikacja konsolowa (CLI), interfejs graficzny (GUI) oraz widget KDE Plasma.

> **Dokumentacja angielska**: [README.md](../README.md)

## 📋 Opis

Profesjonalne narzędzie do testowania prędkości internetu oparte na Python, które wykorzystuje speedtest.net do pomiaru:
- Prędkości pobierania
- Prędkości wysyłania
- Opóźnienia (ping)

### ✨ Kluczowe Funkcje

- **Trzy interfejsy** - CLI, GUI (KivyMD) oraz widget KDE Plasma
- **Zaawansowana obsługa błędów** - automatyczne ponawianie prób przy przejściowych problemach sieciowych
- **Elastyczna konfiguracja** - wszystkie parametry konfigurowalne przez plik JSON
- **Walidacja wyników** - inteligentne ostrzeżenia o nieprawdopodobnych wynikach
- **Raportowanie postępu** - szczegółowe informacje o etapach testu
- **Sprawdzanie połączenia** - wstępna weryfikacja połączenia internetowego
- **Przyjazny interfejs** - przejrzyste wyświetlanie wyników z formatowaniem
- **Nowoczesny Material Design** - współczesny GUI z animacjami i responsywnym designem
- **Widget dla pulpitu KDE** - lekki widget Plasma z automatycznym odświeżaniem
- **Historia testów** - przechowywanie wyników w bazie SQLite z eksportem do CSV/JSON

## 🚀 Szybki Start

### Wymagania Systemowe

- Python 3.8+ (3.6+ tylko dla CLI, ale zależności GUI wymagają 3.8+)
- Połączenie internetowe
- Środowisko wirtualne (zalecane)

### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone <repository-url>
cd Speed_test
```

2. **Skonfiguruj używając Makefile (zalecane)**
```bash
make setup          # Utwórz venv i zainstaluj zależności
make run-cli        # Uruchom test CLI
make run-gui        # Uruchom test GUI
```

3. **Lub ręcznie**
```bash
python3 -m venv speedtest_env
source speedtest_env/bin/activate  # W Windows: speedtest_env\Scripts\activate
pip install -r requirements.txt
```

### Podstawowe Użycie

**Aplikacja CLI:**
```bash
# Uruchom test z domyślną konfiguracją
python sp.py

# Uruchom test z wyjściem JSON
python sp.py --json

# Utwórz plik konfiguracyjny do dostosowania
python sp.py --create-config
```

### Jak Działa CLI
- sp.py jest lekką warstwą, która deleguje całą logikę do speedtest_core
- Konfiguracja jest wczytywana i walidowana przez SpeedTestConfig
- Testowanie (z ponawianiem i walidacją) jest wykonywane przez SpeedTestEngine
- sp.py obsługuje tylko flagę --create-config i wyświetla wyniki

**Aplikacja GUI:**
```bash
# Uruchom interfejs graficzny
python speedtest_gui.py
```

## 🎨 Graficzny Interfejs Użytkownika (GUI)

### Funkcje GUI

- **Nowoczesny Material Design** - współczesny wygląd zgodny z wytycznymi Material Design
- **Postęp w czasie rzeczywistym** - animowany pasek postępu z informacjami o etapie testu
- **Responsywny design** - automatyczne dostosowanie rozmiaru okna
- **Intuicyjne sterowanie** - prosty interfejs z przyciskami Start/Stop
- **Wizualizacja wyników** - przejrzyste wyświetlanie wyników w kartach
- **Obsługa błędów** - przyjazne komunikaty o błędach i ostrzeżeniach
- **Dialog ustawień** - opcje konfiguracji (planowane w przyszłych wersjach)

### Uruchamianie GUI

```bash
# Uruchom aplikację graficzną
python speedtest_gui.py
```

### Architektura GUI

- **speedtest_gui.py** - główna aplikacja GUI z interfejsem KivyMD
- **speedtest_core.py** - logika biznesowa współdzielona przez CLI i GUI
- **Asynchroniczne testowanie** - testy działają w tle bez blokowania interfejsu
- **Callbacki postępu** - aktualizacje postępu w czasie rzeczywistym
- **Bezpieczeństwo wątków** - bezpieczne operacje wielowątkowe

## 🖥️ Widget KDE Plasma

Widget dla pulpitu KDE Plasma wyświetlający wyniki testów prędkości.

### Funkcje Widgetu

- **Wyświetlanie wyników** - pokazuje prędkości pobierania, wysyłania i ping
- **Automatyczne odświeżanie** - aktualizacja co 30 sekund
- **Uruchamianie testów** - przycisk do szybkiego uruchomienia nowego testu
- **Status sieci** - wskaźnik połączenia internetowego
- **Tryb kompaktowy** - może być dodany do panelu z podpowiedzią
- **Integracja z bazą danych** - wykorzystuje współdzieloną bazę SQLite

### Instalacja Widgetu

```bash
# Zainstaluj widget
make install-plasmoid

# Lub ręcznie
cd plasma-widget
./install_plasmoid.sh
```

### Dodawanie do Pulpitu

1. Kliknij prawym przyciskiem myszy na pulpicie
2. Wybierz **"Dodaj widżety"**
3. Wyszukaj **"Speed Test"**
4. Przeciągnij widget na pulpit lub panel

### Korzystanie z Widgetu

- **Wyświetlanie wyników**: Widget pokazuje najnowsze wyniki z bazy danych
- **Uruchomienie testu**: Kliknij przycisk "Run Speed Test"
- **Odświeżanie**: Ikona odświeżania ręcznie aktualizuje wyniki
- **Tryb panelu**: Dodaj do panelu dla szybkiego przeglądu

Więcej informacji w [plasma-widget/README.md](../plasma-widget/README.md)

## ⚙️ Konfiguracja

### Tworzenie Pliku Konfiguracyjnego

```bash
python sp.py --create-config
```

To polecenie tworzy plik `speedtest_config.json` z domyślnymi ustawieniami.

### Dostępne Opcje Konfiguracji

```json
{
  "bits_to_mbps": 1000000,                    // Konwersja bitów na Mbps
  "connectivity_check_timeout": 10,           // Timeout sprawdzania połączenia (s)
  "speedtest_timeout": 60,                    // Timeout głównego testu (s)
  "max_retries": 3,                          // Maksymalna liczba ponownych prób
  "retry_delay": 2,                          // Opóźnienie między próbami (s)
  "max_typical_speed_gbps": 1,               // Próg typowej prędkości (Gbps)
  "max_reasonable_speed_gbps": 10,           // Maksymalna rozsądna prędkość (Gbps)
  "max_typical_ping_ms": 1000,               // Próg typowego pingu (ms)
  "max_reasonable_ping_ms": 10000,           // Maksymalny rozsądny ping (ms)
  "show_detailed_progress": true,            // Szczegółowe informacje o postępie
  "save_results_to_database": true           // Zapisuj wyniki do bazy SQLite
}
```

## 📊 Przykłady Użycia

### Standardowe Uruchomienie

```bash
$ python sp.py

Internet Speed Test Tool
-------------------------
Checking network connectivity...
Network connection detected.

========================================
SPEED TEST RESULTS
========================================
Download: 85.42 Mbps
Upload:   45.67 Mbps
Ping:     12.4 ms
Server:   Orange Polska (Warsaw)
========================================

Result saved to database (ID: 1).
```

Uwaga: Wszelkie ostrzeżenia (np. o niezwykle wysokich prędkościach) będą wyświetlane poniżej wyników w sekcji "Warnings:".

### Uruchomienie z Niestandardową Konfiguracją

```bash
# 1. Utwórz plik konfiguracyjny
python sp.py --create-config

# 2. Edytuj speedtest_config.json według potrzeb
nano speedtest_config.json

# 3. Uruchom z niestandardową konfiguracją
python sp.py
```

### Tryb Wyjścia JSON

```bash
# Wyjście JSON czytelne dla maszyn
python sp.py --json
```

## 🔧 Struktura Projektu

```
Speed_test/
├── sp.py                           # Lekki frontend CLI delegujący do speedtest_core
├── speedtest_gui.py                # Aplikacja GUI (Kivy/KivyMD)
├── speedtest_core.py               # Logika biznesowa (współdzielona przez CLI/GUI)
├── scheduled_testing.py            # Harmonogram w tle dla automatycznego testowania
├── test_results_storage.py         # Przechowywanie SQLite z możliwością eksportu
├── config_validator.py             # Walidacja konfiguracji
├── requirements.txt                # Zależności Python
├── speedtest_config.json.example   # Przykładowa konfiguracja
├── speedtest_config.json          # Konfiguracja użytkownika (ignorowana przez git)
├── Makefile                        # Automatyzacja budowania
├── plasma-widget/                  # Widget KDE Plasma
├── README.md                      # Dokumentacja angielska
├── pl/                            # Dokumentacja polska
├── speedtest_env/                 # Wirtualne środowisko Python
└── .gitignore                     # Wzorce ignorowane przez Git
```

## 🛠️ Zaawansowane Funkcje

### Obsługa Błędów

- **Automatyczne ponawianie**: Dla przejściowych problemów sieciowych
- **Sprawdzanie połączenia**: Weryfikacja połączenia przed testem
- **Łagodna degradacja**: Czytelne komunikaty o błędach
- **Walidacja wyników**: Ostrzeżenia o niezwykłych wynikach

### Inteligentna Walidacja

Narzędzie automatycznie wykrywa i ostrzega o:
- Nieprawdopodobnie wysokich prędkościach (>1 Gbps)
- Ekstremalnie wysokich opóźnieniach (>1000 ms)
- Bardzo niskich prędkościach (<1 Mbps)
- Nieprawidłowych danych pomiarowych

### Kody Wyjścia

- `0`: Test zakończony pomyślnie
- `1`: Test nieudany (brak internetu, błąd pomiaru)

## 🐛 Rozwiązywanie Problemów

### Brak Połączenia Internetowego

```
Error: No internet connection detected.
Please check your network connection and try again.
```
**Rozwiązanie**: Sprawdź swoje połączenie internetowe i spróbuj ponownie.

### Błędy Konfiguracji

```
Warning: Could not load config file speedtest_config.json: ...
Using default configuration.
```
**Rozwiązanie**: Sprawdź składnię JSON w pliku konfiguracyjnym lub usuń plik, aby użyć domyślnej konfiguracji.

### Wysokie Opóźnienie/Niskie Prędkości

```
Warning: High latency (1500 ms) detected - connection may be slow
```
**Rozwiązanie**: To informacja - wskazuje na problemy z połączeniem internetowym.

### Problemy z GUI

```
Error: Unable to start GUI application
```
**Rozwiązanie**: Upewnij się, że wszystkie zależności GUI są zainstalowane:
```bash
pip install -r requirements.txt
```

### Kompatybilność z Python 3.13

```
AttributeError: 'ProcessingStream' object has no attribute 'fileno'
```

**Automatyczne rozwiązanie**: Patch jest automatycznie stosowany podczas instalacji.

**Rozwiązanie ręczne** (jeśli potrzebne):
```bash
source speedtest_env/bin/activate
python3 fix_speedtest_py313.py
```

**Alternatywa** - zastosuj patch ręcznie dodając `AttributeError` do obsługi wyjątków w `speedtest.py` około linii 181:
```python
# Przed:
except OSError:
# Po:
except (OSError, AttributeError):
```

## 📦 Zależności

### Aplikacja CLI
- **speedtest-cli** (v2.1.3): Biblioteka do testowania prędkości internetu
- **Python 3.8+**: Z obsługą podpowiedzi typów

### Aplikacja GUI (dodatkowe)
- **Kivy** (v2.3.1): Framework aplikacji wieloplatformowych
- **KivyMD** (v1.2.0): Komponenty Material Design dla Kivy
- **Pillow**: Obsługa obrazów w Kivy

### Baza Danych i Przechowywanie
- **SQLite3**: Wbudowane w Python, używane do przechowywania wyników testów

## 💾 Przechowywanie Wyników Testów i Baza Danych

Wszystkie komponenty (CLI, GUI, harmonogram, widget Plasma) współdzielą ujednoliconą bazę danych SQLite dla wyników testów.

### Lokalizacja Bazy Danych

**Ujednolicona lokalizacja** (wszystkie komponenty):
```
~/.local/share/speedtest/speedtest_history.db
```

Katalog bazy danych jest automatycznie tworzony przy pierwszym użyciu. Ta scentralizowana lokalizacja zapewnia:
- Wszystkie interfejsy mają dostęp do tej samej historii testów
- Łatwa kopia zapasowa i zarządzanie danymi
- Spójne dane do analizy we wszystkich narzędziach

### Schemat Bazy Danych

Baza danych przechowuje kompleksowe informacje o testach:

| Kolumna | Typ | Opis |
|--------|------|-------------|
| `id` | INTEGER | Automatycznie zwiększany klucz główny |
| `timestamp` | REAL | Znacznik czasu Unix (czas systemowy wykonania testu) |
| `download_mbps` | REAL | Prędkość pobierania w Mbps |
| `upload_mbps` | REAL | Prędkość wysyłania w Mbps |
| `ping_ms` | REAL | Opóźnienie w milisekundach |
| `server_info` | TEXT | Informacje o serwerze testu prędkości |
| `is_valid` | BOOLEAN | Status walidacji wyniku |
| `warnings` | TEXT | Tablica JSON z ostrzeżeniami (jeśli są) |
| `test_date` | TEXT | Data/czas sformatowana ISO 8601 (np. "2025-11-15T13:48:11.601623") |

**Indeksy**: Utworzone na `timestamp` i `test_date` dla szybkich zapytań.

**Tryb WAL**: Baza danych używa Write-Ahead Logging dla lepszego współbieżnego dostępu.

### Automatyczne Zapisywanie Wyników

Wyniki są automatycznie zapisywane, gdy `save_results_to_database` jest włączone w konfiguracji:

```json
{
  "save_results_to_database": true
}
```

- **CLI**: Zapisuje po każdym udanym teście, wyświetla ID rekordu
- **GUI**: Cicho zapisuje wyniki w tle
- **Harmonogram**: Zawsze zapisuje wyniki niezależnie od ustawienia konfiguracji
- **Widget**: Odczytuje najnowsze wyniki ze współdzielonej bazy danych

### Eksportowanie Danych

Użyj polecenia `speedtest-storage` do eksportu danych:

```bash
# Eksportuj ostatnie 30 dni do CSV
speedtest-storage export-csv --days 30 --output results.csv

# Eksportuj wszystkie wyniki do JSON
speedtest-storage export-json --output results.json

# Wyświetl statystyki
speedtest-storage stats --days 7
```

### Ręczny Dostęp do Bazy Danych

Możesz uzyskać bezpośredni dostęp do bazy danych za pomocą dowolnego klienta SQLite:

```bash
# Używając wiersza poleceń sqlite3
sqlite3 ~/.local/share/speedtest/speedtest_history.db "SELECT * FROM test_results ORDER BY timestamp DESC LIMIT 10;"
```

### Konserwacja Bazy Danych

**Kopia zapasowa**:
```bash
cp ~/.local/share/speedtest/speedtest_history.db ~/speedtest_backup.db
```

**Reset** (usuń wszystkie wyniki):
```bash
rm ~/.local/share/speedtest/speedtest_history.db*
```

Uwaga: Znak wieloznaczny `*` usuwa również pliki WAL i SHM utworzone przez SQLite.

## 🧪 Testowanie i Rozwój

### Środowisko Deweloperskie

```bash
# Skonfiguruj środowisko deweloperskie
make dev-setup      # Instaluje pytest, black, flake8, mypy

# Uruchom testy
make test           # Szybkie testy funkcjonalności
make test-full      # Pełny zestaw testów
make test-offline   # Testy bez sieci

# Jakość kodu
make lint           # Uruchom flake8
make format         # Formatuj za pomocą black
```

### Uruchamianie Testów

```bash
# Szybkie testy
./speedtest_env/bin/python3 test_installation.py --quick

# Pełny zestaw testów
./speedtest_env/bin/python3 test_installation.py

# Testy offline
./speedtest_env/bin/python3 test_installation.py --no-network

# Testy walidacji konfiguracji
./speedtest_env/bin/python3 test_config_validation.py
```

### Dodawanie Nowych Funkcji

1. Edytuj odpowiedni plik (`sp.py` dla CLI, `speedtest_gui.py` dla GUI, `speedtest_core.py` dla wspólnej logiki)
2. Przetestuj zmiany w różnych scenariuszach sieciowych
3. Zaktualizuj dokumentację według potrzeb
4. Commituj zmiany z opisowymi komunikatami

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik LICENSE dla szczegółów.

### Licencje Bibliotek Zewnętrznych

Ten projekt wykorzystuje następujące biblioteki:
- **speedtest-cli** - Apache License 2.0 (pełny tekst w LICENSE-APACHE-2.0)
- **Kivy** - MIT License
- **KivyMD** - MIT License
- **Pillow** - HPND License

Zobacz plik NOTICE dla szczegółowych informacji o przypisaniu i licencjach.

## 🔗 Przydatne Linki

- [Dokumentacja speedtest-cli](https://pypi.org/project/speedtest-cli/)
- [Dokumentacja Kivy](https://kivy.org/doc/stable/)
- [Dokumentacja KivyMD](https://kivymd.readthedocs.io/)
- [Wirtualne Środowiska Python](https://docs.python.org/3/tutorial/venv.html)
- [Format Konfiguracji JSON](https://www.json.org/)

---

**Uwaga**: To narzędzie wymaga aktywnego połączenia internetowego do prawidłowego działania. Wszystkie testy są przeprowadzane przy użyciu usług speedtest.net.
