# Internet Speed Test Tool

Narzędzie do testowania prędkości połączenia internetowego z zaawansowaną obsługą błędów, konfiguracją i walidacją wyników. Dostępne jako aplikacja konsolowa i graficzny interfejs użytkownika (GUI).

## 📋 Opis

To jest profesjonalne narzędzie do testowania prędkości internetu napisane w Pythonie, które wykorzystuje serwis speedtest.net do pomiaru:
- Prędkości pobierania (download)
- Prędkości wysyłania (upload)  
- Opóźnienia (ping/latencja)

### ✨ Główne funkcjonalności

- **Dwa interfejsy** - konsola (CLI) i graficzny interfejs (GUI)
- **Zaawansowana obsługa błędów** - automatyczne ponowne próby przy przejściowych problemach sieciowych
- **Elastyczna konfiguracja** - wszystkie parametry można dostosować przez plik JSON
- **Walidacja wyników** - inteligentne ostrzeżenia o nieprawdopodobnych wynikach
- **Progresywne informacje** - szczegółowe informacje o postępie testów
- **Sprawdzenie łączności** - wstępna weryfikacja połączenia internetowego
- **Przyjazny interfejs** - czytelny wyświetlacz wyników z formatowaniem
- **Modern Material Design** - nowoczesny GUI z animacjami i responsywnym designem

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

**Aplikacja konsolowa (CLI):**
```bash
# Uruchom test z domyślną konfiguracją
python sp.py

# Utwórz plik konfiguracyjny do dostosowania
python sp.py --create-config
```

### Jak działa CLI
- sp.py jest lekką nakładką, która w całości deleguje logikę do speedtest_core.
- Konfiguracja jest ładowana i walidowana przez SpeedTestConfig.
- Pomiar (z retry i walidacją) wykonuje SpeedTestEngine.
- sp.py tylko obsługuje flagę --create-config i wyświetla wyniki.

**Aplikacja graficzna (GUI):**
```bash
# Uruchom interfejs graficzny
python speedtest_gui.py
```

## 🎨 Interfejs graficzny (GUI)

### Funkcjonalności GUI

- **Modern Material Design** - nowoczesny wygląd zgodny z Material Design
- **Real-time progress** - animowany pasek postępu z informacjami o etapie testu
- **Responsive design** - automatyczne dostosowanie do rozmiaru okna
- **Intuitive controls** - prosty interfejs z przyciskami Start/Stop
- **Visual results** - przejrzyste wyświetlanie wyników w kartach
- **Error handling** - przyjazne komunikaty błędów i ostrzeżeń
- **Settings dialog** - możliwość konfiguracji (planowane w przyszłych wersjach)

### Uruchomienie GUI

```bash
# Uruchom aplikację graficzną
python speedtest_gui.py
```

### Architektura GUI

- **speedtest_gui.py** - główna aplikacja GUI z interfejsem KivyMD
- **speedtest_core.py** - logika biznesowa wspólna dla CLI i GUI
- **Asynchronous testing** - testy działają w tle bez blokowania interfejsu
- **Progress callbacks** - real-time aktualizacje postępu
- **Thread safety** - bezpieczne operacje wielowątkowe

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
```

Uwaga: Ewentualne ostrzeżenia (np. nietypowo wysokie prędkości) zostaną wypisane pod wynikami w sekcji "Warnings:".

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
├── sp.py                           # Lekki frontend CLI delegujący do speedtest_core
├── speedtest_gui.py                # Aplikacja GUI (Kivy/KivyMD)
├── speedtest_core.py               # Logika biznesowa (wspólna dla CLI/GUI)
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

**Automatyczne rozwiązanie**: Od wersji bieżącej patch jest automatycznie stosowany podczas instalacji.

**Ręczne rozwiązanie** (jeśli potrzebne):
```bash
source speedtest_env/bin/activate  # lub ebv/bin/activate
python3 fix_speedtest_py313.py
```

**Alternatywnie** - zastosuj patch manualnie, dodając `AttributeError` do obsługi wyjątków w pliku `speedtest.py` linii ~181:
```python
# Przed:
except OSError:
# Po:
except (OSError, AttributeError):
```

## 📦 Zależności

### Aplikacja CLI
- **speedtest-cli** (v2.1.3): Biblioteka do testowania prędkości internetu
- **Python 3.6+**: Ze wsparciem dla type hints

### Aplikacja GUI (dodatkowo)
- **Kivy** (v2.3.1): Framework do tworzenia aplikacji multiplatformowych
- **KivyMD** (v1.2.0): Material Design komponenty dla Kivy
- **Pillow**: Obsługa obrazów w Kivy

## 🤝 Rozwój projektu

### Środowisko deweloperskie

```bash
# Aktywacja środowiska
source ebv/bin/activate

# Instalacja zależności
pip install -r requirements.txt

# Testowanie zmian CLI
python sp.py

# Testowanie zmian GUI
python speedtest_gui.py
```

### Dodawanie nowych funkcji

1. Edytuj odpowiedni plik (`sp.py` dla CLI, `speedtest_gui.py` dla GUI, `speedtest_core.py` dla logiki wspólnej)
2. Testuj zmiany w różnych scenariuszach sieciowych
3. Aktualizuj dokumentację w razie potrzeby
4. Commituj zmiany z opisowymi komunikatami

## 📄 Licencja

Projekt jest dostępny na licencji MIT. Szczegóły w pliku LICENSE.

### Licencje Third-Party

Ten projekt wykorzystuje następujące biblioteki:
- **speedtest-cli** - Apache License 2.0 (pełny tekst w LICENSE-APACHE-2.0)
- **Kivy** - MIT License
- **KivyMD** - MIT License
- **Pillow** - HPND License

Zobacz plik NOTICE dla szczegółowych informacji o atrybuacji i licencjach.

## 🔗 Linki użyteczne

- [speedtest-cli documentation](https://pypi.org/project/speedtest-cli/)
- [Kivy documentation](https://kivy.org/doc/stable/)
- [KivyMD documentation](https://kivymd.readthedocs.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [JSON Configuration Format](https://www.json.org/)

---

**Uwaga**: Ten tool wymaga aktywnego połączenia internetowego do prawidłowego działania. Wszystkie testy są przeprowadzane z wykorzystaniem serwisów speedtest.net.