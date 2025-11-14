# Speed Test Tool - Konfiguracja Plików Wykonywalnych

## 📋 Przegląd

Ten dokument opisuje jak skonfigurować Speed Test Tool aby działał jako aplikacja uruchomialna bez bezpośredniego wywoływania Python.

## 🚀 Instalacja Automatyczna (Zalecane)

### Dla wszystkich użytkowników (wymaga sudo):
```bash
sudo python3 install.py
```

### Dla bieżącego użytkownika:
```bash
python3 install.py --user
```

### Za pomocą Makefile:
```bash
make install          # System-wide
make install-user     # User-only
```

## 📁 Struktura Po Instalacji

```
/usr/local/bin/              # System-wide installation
├── speedtest-cli*           # CLI interface executable
├── speedtest-gui*           # GUI interface executable
├── speedtest-gui-fallback*  # Alternative GUI executable
├── speedtest-scheduler*     # Background scheduler executable
└── speedtest-storage*       # Data management executable

~/.local/bin/                # User installation
├── speedtest-cli*           # Same executables for user
├── speedtest-gui*
└── ...
```

## 🎯 Utworzone Pliki Wykonywalne

### 1. `speedtest-cli` - Interface CLI
```bash
# Podstawowe użycie
speedtest-cli

# Tworzenie konfiguracji
speedtest-cli --create-config

# Pomoc
speedtest-cli --help
```

**Funkcjonalność:**
- Test prędkości download/upload/ping
- System retry przy błędach sieci
- Walidacja i ostrzeżenia o wynikach
- Wsparcie konfiguracji JSON

### 2. `speedtest-gui` - Interface Graficzny
```bash
# Uruchomienie GUI
speedtest-gui

# Material Design interface z:
# - Real-time progress
# - Możliwość anulowania
# - Graficzne wyniki
# - Animacje i feedback
```

**Funkcjonalność:**
- Modern Material Design
- Progress tracking w czasie rzeczywistym
- Możliwość anulowania testów
- Wizualne wyświetlanie wyników

### 3. `speedtest-gui-fallback` - Alternatywny GUI
```bash
# Jeśli główny GUI nie działa
speedtest-gui-fallback

# Prostszy interface jako fallback
```

### 4. `speedtest-scheduler` - Automatyzacja
```bash
# Test jednorazowy z zapisem do bazy
speedtest-scheduler --immediate

# Automatyczne testy co 30 minut
speedtest-scheduler --interval 30

# Wyświetlenie statystyk
speedtest-scheduler --stats --days 7

# Uruchomienie w tle
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &
```

**Funkcjonalność:**
- Automatyczne testy w tle
- Zapis do bazy SQLite
- Statystyki historyczne
- Export danych

### 5. `speedtest-storage` - Zarządzanie Danymi
```bash
# Statystyki z ostatnich 30 dni
speedtest-storage stats --days 30

# Export do CSV
speedtest-storage export csv wyniki.csv

# Export do JSON
speedtest-storage export json dane.json --days 7

# Informacje o bazie
speedtest-storage info

# Czyszczenie starych danych
speedtest-storage cleanup --keep-days 365
```

## ⚙️ Konfiguracja PATH

### Automatyczna (podczas instalacji):
Installer automatycznie sprawdza czy skrypty są w PATH i wyświetla instrukcje jeśli potrzeba.

### Ręczna konfiguracja:
```bash
# Dla instalacji użytkownika - dodaj do ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Sprawdzenie czy działa
which speedtest-cli
```

## 🖥️ Desktop Integration (Linux)

### .desktop File
Installer automatycznie tworzy:
```
~/.local/share/applications/speedtest.desktop
```

**Funkcjonalność:**
- Ikona w menu aplikacji
- Uruchomienie przez kliknięcie
- Kategorie: Network, Utility

### Menu Applications
Po instalacji aplikacja pojawi się w:
- Menu → Network → Speed Test Tool
- lub Applications → Internet → Speed Test Tool

## 🔧 Systemd Service (Opcjonalne)

### Instalacja usługi:
```bash
sudo make service-install
sudo systemctl enable speedtest.service
sudo systemctl start speedtest.service
```

### Zarządzanie:
```bash
make service-status    # Status usługi
make service-start     # Uruchomienie
make service-stop      # Zatrzymanie
journalctl -u speedtest.service  # Logi
```

## 🎛️ Konfiguracja

### Tworzenie konfiguracji:
```bash
speedtest-cli --create-config
```

### Lokalizacja plików:
```
Speed_test/
├── speedtest_config.json     # Konfiguracja użytkownika
├── speedtest_history.db      # Baza danych wyników
└── speedtest_env/            # Środowisko wirtualne
```

### Przykład konfiguracji:
```json
{
  "bits_to_mbps": 1000000,
  "speedtest_timeout": 60,
  "max_retries": 3,
  "show_detailed_progress": true
}
```

## 🧪 Testowanie Instalacji

### Szybki test:
```bash
make test
# lub
python3 test_installation.py --quick
```

### Pełny test:
```bash
make test-full
# lub
python3 test_installation.py
```

### Test bez sieci:
```bash
make test-offline
# lub
python3 test_installation.py --no-network
```

### Test komend:
```bash
# Test każdej komendy
speedtest-cli --create-config
speedtest-storage info
speedtest-scheduler --immediate
speedtest-gui  # Test GUI (wyświetli okno)
```

## 🔍 Rozwiązywanie Problemów

### Skrypty nie są znalezione:
```bash
# Sprawdź PATH
echo $PATH

# Sprawdź instalację
ls -la ~/.local/bin/speedtest-*
# lub
ls -la /usr/local/bin/speedtest-*

# Reinstalacja
python3 install.py --user
```

### Błędy uprawnień:
```bash
# Naprawa uprawnień
chmod +x ~/.local/bin/speedtest-*

# lub system-wide
sudo chmod +x /usr/local/bin/speedtest-*
```

### GUI nie uruchamia się:
```bash
# Sprawdź zależności
python3 -c "from kivymd.app import MDApp; print('GUI OK')"

# Ustaw backend
export KIVY_GL_BACKEND=gl

# Użyj fallback
speedtest-gui-fallback
```

### Błędy środowiska wirtualnego:
```bash
# Sprawdź czy istnieje
ls -la speedtest_env/

# Reinstalacja
make setup
python3 install.py
```

## 📊 Informacje Systemowe

### Status instalacji:
```bash
make info
```

### Lokalizacje plików:
```bash
# Skrypty wykonywalne
which speedtest-cli
which speedtest-gui
which speedtest-scheduler

# Pliki aplikacji
ls -la Speed_test/

# Desktop entry
ls -la ~/.local/share/applications/speedtest.desktop
```

## 🗑️ Deinstalacja

### Podstawowa deinstalacja:
```bash
python3 uninstall.py
```

### Pełna deinstalacja (z danymi):
```bash
python3 uninstall.py --remove-all
```

### Ręczna deinstalacja:
```bash
# Usuń skrypty
rm ~/.local/bin/speedtest-*
# lub
sudo rm /usr/local/bin/speedtest-*

# Usuń desktop entry
rm ~/.local/share/applications/speedtest.desktop

# Usuń katalog aplikacji
rm -rf Speed_test/
```

## 💡 Wskazówki Użytkowania

### Aliasy (opcjonalne):
```bash
# Dodaj do ~/.bashrc dla wygody
alias st="speedtest-cli"
alias stgui="speedtest-gui"
alias stats="speedtest-storage stats"
```

### Crontab (alternatywa dla systemd):
```bash
# Edytuj crontab
crontab -e

# Dodaj linię dla testów co godzinę
0 * * * * /home/user/.local/bin/speedtest-scheduler --immediate
```

### Monitoring:
```bash
# Logi z automatycznych testów
tail -f speedtest.log

# Ostatnie wyniki
speedtest-storage stats --days 1

# Export do monitoringu
speedtest-storage export json /monitoring/speedtest-$(date +%Y%m).json --days 30
```

## 📈 Przykłady Użycia

### 1. Jednorazowy test:
```bash
speedtest-cli
```

### 2. Monitoring ciągły:
```bash
# Uruchomienie w tle
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &

# Sprawdzanie wyników
speedtest-storage stats --days 7
```

### 3. Analiza wydajności:
```bash
# Export do analizy
speedtest-storage export csv "network-performance-$(date +%Y%m).csv" --days 30

# Import do spreadsheet lub narzędzi analitycznych
```

### 4. GUI dla prezentacji:
```bash
# Uruchomienie GUI dla demonstracji
speedtest-gui

# Real-time monitoring z wizualnym feedbackiem
```

**✅ Po zakończeniu instalacji aplikacja jest gotowa do użycia jako standardowa aplikacja systemowa bez konieczności znajomości Python!**