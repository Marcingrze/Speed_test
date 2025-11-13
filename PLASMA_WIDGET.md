# KDE Plasma Speed Test Widget - Dokumentacja Techniczna

Kompletna dokumentacja techniczna widget KDE Plasma dla Speed Test Tool, obejmująca development, testowanie i deployment produkcyjny.

## 📋 Spis treści

- [Architektura](#architektura)
- [Środowisko Developerskie](#środowisko-developerskie)
- [Testowanie](#testowanie)
- [Debugging](#debugging)
- [Deployment Produkcyjny](#deployment-produkcyjny)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [API Backend](#api-backend)

## Architektura

### Struktura Widget

```
org.kde.plasma.speedtest/
├── metadata.json                      # Metadane KDE Plasma
│   ├── KPlugin                        # Informacje o autorach, licencji, wersji
│   ├── X-Plasma-API                   # declarativeappletscript
│   └── X-Plasma-MainScript            # ui/main.qml
│
└── contents/
    ├── ui/
    │   └── main.qml                   # Frontend (Qt Quick/QML)
    │       ├── PlasmoidItem           # Główny kontener widget
    │       ├── fullRepresentation     # Widok pełny (desktop)
    │       └── compactRepresentation  # Widok kompaktowy (panel)
    │
    ├── code/
    │   └── speedtest_helper.py        # Backend Python
    │       ├── get_last_result()      # Pobiera ostatni wynik z DB
    │       ├── run_test_background()  # Uruchamia test
    │       └── check_connectivity()   # Sprawdza sieć
    │
    └── config/                        # Konfiguracja (future use)
```

### Komunikacja Frontend ↔ Backend

```
┌─────────────────────────────────────────────────────────────┐
│                      QML Frontend                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ PlasmaCore.DataSource (engine: "executable")       │    │
│  │   • Uruchamia procesy systemowe                    │    │
│  │   • Odbiera stdout jako string                     │    │
│  │   • Asynchroniczne wykonanie                       │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Wywołanie: python3 speedtest_helper.py <command>
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                   Python Backend                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │ speedtest_helper.py                                │    │
│  │   • Parsuje argumenty (get_last/run_test/check)    │    │
│  │   • Importuje speedtest_core, test_results_storage│    │
│  │   • Wykonuje operację                              │    │
│  │   • Zwraca JSON na stdout                          │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ JSON Response
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  SQLite Database                             │
│                 speedtest_history.db                         │
│  • Współdzielona z CLI, GUI, Scheduler                      │
│  • WAL mode + busy timeout                                  │
└─────────────────────────────────────────────────────────────┘
```

### Format Danych (JSON)

**get_last (success)**:
```json
{
  "status": "success",
  "download": 85.4,
  "upload": 45.2,
  "ping": 12.0,
  "server": "Orange Polska (Warsaw)",
  "timestamp": "2025-11-13 18:42:35",
  "is_valid": true,
  "warnings": []
}
```

**get_last (no_data)**:
```json
{
  "status": "no_data",
  "message": "No test results available. Run a test first."
}
```

**run_test (success)**:
```json
{
  "status": "success",
  "message": "Speed test started in background"
}
```

**check_network (success)**:
```json
{
  "status": "success",
  "connected": true
}
```

**Error response**:
```json
{
  "status": "error",
  "message": "Failed to retrieve results: <error details>"
}
```

## Środowisko Developerskie

### Wymagania

- **KDE Plasma** 5.x lub 6.x
- **Qt Quick/QML** - dostępne z Plasma
- **Python 3.8+**
- **Speed Test** - zainstalowany w katalogu nadrzędnym
- **Narzędzia dev**:
  - `kpackagetool5` lub `kpackagetool6`
  - `plasmoidviewer` (opcjonalnie, do testowania)
  - `qmlscene` (opcjonalnie, do debugowania QML)

### Setup Środowiska

```bash
# 1. Przejdź do głównego katalogu projektu
cd /path/to/Speed_test

# 2. Upewnij się, że speedtest_env jest skonfigurowany
make setup

# 3. Sprawdź czy backend działa
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# 4. Zainstaluj widget w trybie dev
cd plasma-widget
./install_plasmoid.sh

# 5. Restart Plasma (lub użyj plasmoidviewer)
make restart-plasma
```

### Edycja i Iteracja

#### Szybkie zmiany QML (bez reinstalacji)

```bash
# 1. Edytuj plik QML
nano ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/ui/main.qml

# 2. Restart widget (bez restart całego Plasma)
# Usuń widget z pulpitu i dodaj ponownie przez "Add Widgets"
```

#### Zmiany wymagające reinstalacji

Backend Python lub metadata:

```bash
# 1. Edytuj pliki
nano plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py
# lub
nano plasma-widget/org.kde.plasma.speedtest/metadata.json

# 2. Reinstaluj
cd plasma-widget
./uninstall_plasmoid.sh
./install_plasmoid.sh

# 3. Restart Plasma
make restart-plasma
```

### Użycie plasmoidviewer (Plasma 5)

Testowanie widget bez instalacji w systemie:

```bash
# Uruchom widget w standalone viewer
plasmoidviewer -a plasma-widget/org.kde.plasma.speedtest

# Z hot-reload (auto-refresh po zmianach)
plasmoidviewer -a plasma-widget/org.kde.plasma.speedtest --hotreload
```

**Uwaga**: `plasmoidviewer` może nie być dostępny w Plasma 6.

## Testowanie

### 1. Unit Testing Backend

Test helperów Python:

```bash
# Test get_last
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# Oczekiwany output (jeśli są dane):
# {"status": "success", "download": 85.4, ...}

# Test run_test
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py run_test

# Oczekiwany output:
# {"status": "success", "message": "Speed test started in background"}

# Test check_network
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py check_network

# Oczekiwany output:
# {"status": "success", "connected": true}
```

### 2. Integration Testing

Test pełnego flow:

```bash
# 1. Wyczyść bazę danych (opcjonalnie)
mv speedtest_history.db speedtest_history.db.backup

# 2. Uruchom test przez CLI
./speedtest_env/bin/python3 sp.py

# 3. Sprawdź czy wynik jest w bazie
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# 4. Zainstaluj widget i sprawdź czy wyświetla dane
make install-plasmoid
# Dodaj widget do pulpitu i sprawdź czy pokazuje wyniki
```

### 3. Manual Testing Checklist

#### Widget na pulpicie (Full Representation)

- [ ] Widget wyświetla się poprawnie po dodaniu
- [ ] Pokazuje dane z ostatniego testu (Download, Upload, Ping)
- [ ] Przycisk "Run Speed Test" jest klikalny
- [ ] Przycisk refresh odświeża dane
- [ ] Status sieci jest poprawny (zielony gdy online)
- [ ] Auto-refresh działa (sprawdź po 30 sekundach)
- [ ] Po uruchomieniu testu przycisk się dezaktywuje
- [ ] Po 60 sekundach widget automatycznie odświeża wyniki
- [ ] Ostrzeżenie "No network" pojawia się gdy brak internetu

#### Widget w panelu (Compact Representation)

- [ ] Ikona pokazuje się w panelu
- [ ] Hover tooltip wyświetla quick stats
- [ ] Kliknięcie otwiera pełny widok
- [ ] Compact text pokazuje prędkości (↓85.4 Mbps ↑45.2 Mbps)

### 4. Error Scenarios Testing

Test zachowania przy błędach:

```bash
# Brak danych w bazie
rm speedtest_history.db
# Widget powinien pokazać: "No test results available"

# Błąd importu (symulacja)
mv speedtest_core.py speedtest_core.py.backup
# Helper powinien zwrócić: {"error": "Failed to import..."}

# Brak uprawnień do bazy
chmod 000 speedtest_history.db
# Helper powinien zwrócić: {"status": "error", ...}

# Przywróć po testach
chmod 644 speedtest_history.db
mv speedtest_core.py.backup speedtest_core.py
```

### 5. Performance Testing

```bash
# Zmierz czas odpowiedzi backend
time ./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# Oczekiwany czas: < 200ms
```

### 6. Memory Leak Testing

Sprawdź czy widget nie leakuje pamięci:

```bash
# 1. Zanotuj zużycie pamięci Plasma
ps aux | grep plasmashell

# 2. Dodaj widget
# 3. Zostaw na kilka godzin z auto-refresh
# 4. Sprawdź zużycie ponownie

# Nie powinno rosnąć znacząco (max +5-10 MB)
```

## Debugging

### 1. Plasma Logs

Monitor logów Plasma podczas testowania:

```bash
# Wszystkie logi Plasma
journalctl --user -f -u plasma-plasmashell

# Tylko błędy
journalctl --user -f -u plasma-plasmashell | grep -i error

# QML specific
journalctl --user -f | grep -i qml
```

### 2. Backend Debugging

Dodaj debug output do `speedtest_helper.py`:

```python
import sys
import json

def debug_log(message):
    """Log to stderr (nie stdout, bo stdout to JSON response)"""
    print(f"DEBUG: {message}", file=sys.stderr)

# W funkcjach:
debug_log(f"Getting last result from DB")
```

Sprawdź stderr:

```bash
./speedtest_env/bin/python3 plasma-widget/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last 2>&1 | grep DEBUG
```

### 3. QML Debugging

Dodaj console.log w `main.qml`:

```qml
function loadLastResult() {
    console.log("Loading last result...")
    executeCommand("python3", [helperScript, "get_last"], function(output) {
        console.log("Received output:", output)
        // ... rest of code
    })
}
```

Sprawdź logi:

```bash
journalctl --user -f | grep "qml:"
```

### 4. DataSource Debugging

Test PlasmaCore.DataSource bezpośrednio:

```qml
// Dodaj do main.qml
Component.onCompleted: {
    console.log("Helper script path:", helperScript)
    console.log("Script exists:", Qt.fileExists(helperScript))
}
```

### 5. Common Issues

**Problem**: Widget nie wyświetla danych
```bash
# Check 1: Backend działa?
python3 plasma-widget/.../speedtest_helper.py get_last

# Check 2: Ścieżka jest poprawna?
grep helperScript ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/ui/main.qml

# Check 3: Logi Plasma
journalctl --user -f | grep speedtest
```

**Problem**: Auto-refresh nie działa
```qml
// Sprawdź czy Timer jest aktywny
Timer {
    id: refreshTimer
    interval: 30000
    running: true  // <-- Czy true?
    repeat: true   // <-- Czy true?
    onTriggered: {
        console.log("Timer triggered!")  // Dodaj debug
        loadLastResult()
    }
}
```

**Problem**: executeCommand nie działa
```qml
// Sprawdź czy DataSource jest utworzony poprawnie
function executeCommand(program, args, callback) {
    console.log("Executing:", program, args)
    var process = Qt.createQmlObject('...')
    if (!process) {
        console.error("Failed to create DataSource!")
        return
    }
    // ... rest
}
```

## Deployment Produkcyjny

### 1. Pre-release Checklist

Przed wypuszczeniem nowej wersji:

- [ ] Wszystkie testy przechodzą
- [ ] Dokumentacja zaktualizowana
- [ ] Wersja w `metadata.json` zwiększona
- [ ] CHANGELOG.md zaktualizowany
- [ ] Brak debug console.log w kodzie
- [ ] Permissions: pliki 644, skrypty 755
- [ ] Testowane na Plasma 5 i 6 (jeśli możliwe)

### 2. Tworzenie Release Package

```bash
# 1. Przejdź do katalogu
cd plasma-widget

# 2. Sprawdź strukturę
find org.kde.plasma.speedtest -type f

# 3. Utworz archiwum
tar -czf speedtest-plasmoid-v1.0.0.tar.gz org.kde.plasma.speedtest/

# 4. Oblicz checksum
sha256sum speedtest-plasmoid-v1.0.0.tar.gz > speedtest-plasmoid-v1.0.0.tar.gz.sha256

# 5. Testuj instalację z archiwum
kpackagetool5 --type=Plasma/Applet --install speedtest-plasmoid-v1.0.0.tar.gz
```

### 3. Instalacja Produkcyjna

#### Metoda 1: Makefile (Rekomendowana)

```bash
# System-wide installation (jeśli dostępne)
sudo make install-plasmoid

# User installation
make install-plasmoid
```

#### Metoda 2: Skrypt instalacyjny

```bash
cd plasma-widget
./install_plasmoid.sh
```

#### Metoda 3: Ręcznie przez kpackagetool

```bash
# Plasma 5
kpackagetool5 --type=Plasma/Applet --install org.kde.plasma.speedtest

# Plasma 6
kpackagetool6 --type=Plasma/Applet --install org.kde.plasma.speedtest

# Update (jeśli już zainstalowany)
kpackagetool5 --type=Plasma/Applet --upgrade org.kde.plasma.speedtest
```

#### Metoda 4: KDE Store (Przyszłość)

Upload do https://store.kde.org/

### 4. Weryfikacja Instalacji

```bash
# Check 1: Widget jest zainstalowany?
kpackagetool5 --type=Plasma/Applet --show org.kde.plasma.speedtest

# Check 2: Pliki są w miejscu?
ls -la ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/

# Check 3: Backend działa?
python3 ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# Check 4: Widget pojawia się w menu?
# Sprawdź w "Add Widgets" -> Search: "Speed Test"
```

### 5. Post-deployment Monitoring

Po instalacji u użytkownika:

```bash
# Monitor błędów
journalctl --user -f -u plasma-plasmashell | grep -i "speedtest\|error"

# Check memory usage
ps aux | grep plasmashell | awk '{print $6/1024 " MB"}'

# Check database access
ls -lh speedtest_history.db
sqlite3 speedtest_history.db "SELECT COUNT(*) FROM test_results;"
```

## Best Practices

### 1. Performance

**DO:**
- ✅ Używaj asynchronicznych wywołań (PlasmaCore.DataSource)
- ✅ Cachuj wyniki na poziomie QML
- ✅ Używaj Timer zamiast busy loops
- ✅ Minimalizuj częstotliwość odświeżania (30s jest OK)

**DON'T:**
- ❌ Nie blokuj UI thread
- ❌ Nie odpytuj backend co sekundę
- ❌ Nie ładuj ciężkich obrazów/resources
- ❌ Nie twórz memory leaks (właściwie cleanup DataSource)

### 2. Error Handling

```qml
// Zawsze obsługuj błędy parsowania JSON
function loadLastResult() {
    executeCommand("python3", [helperScript, "get_last"], function(output) {
        try {
            var result = JSON.parse(output)
            if (result.status === "success") {
                // Handle success
            } else {
                console.warn("Backend error:", result.message)
                showErrorState(result.message)
            }
        } catch (e) {
            console.error("JSON parse error:", e, "Output:", output)
            showErrorState("Failed to parse response")
        }
    })
}
```

### 3. Security

**Backend (speedtest_helper.py):**
- ✅ Waliduj wszystkie argumenty
- ✅ Używaj `subprocess.Popen` z `start_new_session=True`
- ✅ Nigdy nie wykonuj user input bez walidacji
- ✅ Ograniczaj permisje (644 dla plików, 755 dla skryptów)

**Frontend (main.qml):**
- ✅ Escapuj dane przed wyświetleniem
- ✅ Nie ufaj danym z backend blindly
- ✅ Waliduj format JSON

### 4. Compatibility

Wspieraj Plasma 5 i 6:

```qml
// Sprawdź wersję Plasma
property bool isPlasma6: PlasmaCore.Units !== undefined

// Używaj kompatybilnych API
// Plasma 5: PlasmaCore.Units.gridUnit
// Plasma 6: Kirigami.Units.gridUnit
width: isPlasma6 ? Kirigami.Units.gridUnit * 18 : PlasmaCore.Units.gridUnit * 18
```

### 5. Code Style

**QML:**
```qml
// Naming: camelCase dla properties
property string downloadSpeed: "N/A"

// Naming: camelCase dla funkcji
function loadLastResult() { }

// Indentation: 4 spaces
ColumnLayout {
    spacing: Kirigami.Units.smallSpacing

    PlasmaComponents3.Label {
        text: "Speed Test"
    }
}
```

**Python:**
```python
# Naming: snake_case
def get_last_result():
    pass

# Docstrings
def run_test_background():
    """Start a speed test in the background."""
    pass

# Type hints
def check_connectivity() -> dict:
    return {"status": "success", "connected": True}
```

## Troubleshooting

### Problem: Widget nie instaluje się

**Symptom:**
```bash
kpackagetool5: error: Could not install package
```

**Rozwiązanie:**
```bash
# Check 1: Metadata poprawny?
cat plasma-widget/org.kde.plasma.speedtest/metadata.json | jq .

# Check 2: Struktura katalogów
find plasma-widget/org.kde.plasma.speedtest -type f

# Check 3: Try manual install
mkdir -p ~/.local/share/plasma/plasmoids/
cp -r plasma-widget/org.kde.plasma.speedtest ~/.local/share/plasma/plasmoids/
```

### Problem: Widget wyświetla "No data"

**Symptom:** Widget pokazuje "No test results available"

**Rozwiązanie:**
```bash
# 1. Sprawdź czy baza istnieje
ls -la speedtest_history.db

# 2. Sprawdź czy są dane
sqlite3 speedtest_history.db "SELECT COUNT(*) FROM test_results;"

# 3. Uruchom test
python3 sp.py

# 4. Refresh widget (kliknij przycisk refresh)
```

### Problem: Backend timeout

**Symptom:** Widget nie odpowiada, logs pokazują timeout

**Rozwiązanie:**
```bash
# Test backend ręcznie
time python3 ~/.local/share/plasma/plasmoids/org.kde.plasma.speedtest/contents/code/speedtest_helper.py get_last

# Jeśli > 1 sekunda, problem z:
# - Importami Python (sprawdź sys.path)
# - Dostępem do bazy (sprawdź permissions)
# - Ciężką operacją (dodaj profiling)
```

### Problem: Memory leak

**Symptom:** Plasmashell zużywa coraz więcej pamięci

**Rozwiązanie:**
```qml
// Upewnij się że unschedule Timer przy niszczeniu
Component.onDestruction: {
    refreshTimer.stop()
    if (updateEvent) {
        Clock.unschedule(updateEvent)
    }
}
```

### Problem: Python import error

**Symptom:**
```json
{"error": "Failed to import speedtest modules: No module named 'speedtest_core'"}
```

**Rozwiązanie:**
```python
# W speedtest_helper.py:
import sys
from pathlib import Path

# Dodaj parent dir do path
parent_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Debug: print path
print(f"DEBUG: parent_dir = {parent_dir}", file=sys.stderr)
print(f"DEBUG: sys.path = {sys.path}", file=sys.stderr)
```

## API Backend

### speedtest_helper.py API

#### Command: `get_last`

**Description:** Pobiera ostatni wynik testu z bazy danych

**Usage:**
```bash
python3 speedtest_helper.py get_last
```

**Response (Success):**
```json
{
  "status": "success",
  "download": 85.4,
  "upload": 45.2,
  "ping": 12.0,
  "server": "Orange Polska (Warsaw)",
  "timestamp": "2025-11-13 18:42:35",
  "is_valid": true,
  "warnings": []
}
```

**Response (No Data):**
```json
{
  "status": "no_data",
  "message": "No test results available. Run a test first."
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Failed to retrieve results: <details>"
}
```

#### Command: `run_test`

**Description:** Uruchamia nowy test prędkości w tle (non-blocking)

**Usage:**
```bash
python3 speedtest_helper.py run_test
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Speed test started in background"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Failed to start test: <details>"
}
```

**Note:** Test działa w tle. Wyniki będą dostępne po ~60 sekundach przez `get_last`.

#### Command: `check_network`

**Description:** Sprawdza dostępność połączenia internetowego

**Usage:**
```bash
python3 speedtest_helper.py check_network
```

**Response (Success):**
```json
{
  "status": "success",
  "connected": true
}
```

**Response (No Connection):**
```json
{
  "status": "success",
  "connected": false
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Failed to check connectivity: <details>",
  "connected": false
}
```

### Extending API

Dodawanie nowego command:

```python
# W speedtest_helper.py

def get_statistics(days=7):
    """Get statistics for last N days."""
    try:
        storage = TestResultStorage()
        stats = storage.get_statistics(days=days)

        return {
            "status": "success",
            "download": {
                "min": stats['download_min'],
                "max": stats['download_max'],
                "avg": stats['download_avg']
            },
            "upload": { /* ... */ },
            "ping": { /* ... */ }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get statistics: {str(e)}"
        }

# W main():
def main():
    # ...
    elif command == "get_stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = get_statistics(days)
    # ...
```

```qml
// W main.qml

function loadStatistics(days) {
    executeCommand("python3", [helperScript, "get_stats", days.toString()],
        function(output) {
            var result = JSON.parse(output)
            if (result.status === "success") {
                // Display stats
            }
        }
    )
}
```

## Changelog

### v1.0.0 (2025-11-13)
- ✨ Initial release
- 🎨 Material Design interface
- 📊 Display download, upload, ping
- 🔄 Auto-refresh every 30 seconds
- 🚀 One-click test execution
- 📱 Compact and full representations
- 🔌 Database integration

## Contributing

Przy dodawaniu nowych funkcji:

1. **Testuj lokalnie** - Użyj plasmoidviewer lub reinstaluj widget
2. **Dokumentuj zmiany** - Zaktualizuj ten plik i README.md
3. **Zwiększ wersję** - W metadata.json
4. **Dodaj do CHANGELOG** - Opisz zmiany
5. **Test na obu Plasma** - Jeśli możliwe, testuj na 5 i 6

## License

MIT License - zgodnie z głównym projektem Speed Test Tool

---

**Pytania?** Otwórz issue w repozytorium głównym projektu.
