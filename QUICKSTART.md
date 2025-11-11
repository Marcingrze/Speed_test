# Speed Test Tool - Szybki Start

## 🚀 Instalacja w 3 krokach

### 1. Pobierz i przygotuj
```bash
# Klonuj repozytorium
git clone https://github.com/twój-użytkownik/Speed_test.git
cd Speed_test

# Daj uprawnienia wykonania
chmod +x install.py sp.py speedtest_gui.py
```

### 2. Zainstaluj automatycznie
```bash
# Dla wszystkich użytkowników (wymaga sudo)
sudo python3 install.py

# LUB dla obecnego użytkownika tylko
python3 install.py --user
```

### 3. Uruchom aplikację
```bash
# CLI - Test prędkości w terminalu
speedtest-cli

# GUI - Interfejs graficzny
speedtest-gui

# Scheduler - Automatyczne testy
speedtest-scheduler --immediate
```

---

## 📋 Alternatywne metody uruchamiania

### A. Bez instalacji (tryb deweloperski)
```bash
# Przygotowanie środowiska
make setup

# Uruchamianie bezpośrednie
make run-cli          # CLI
make run-gui          # GUI  
make run-scheduler    # Scheduler
```

### B. Za pomocą Makefile
```bash
# Pełna instalacja
make install

# Tylko środowisko deweloperskie  
make dev-setup

# Test funkcjonalności
make test
```

### C. Ręcznie (bez automatyzacji)
```bash
# Tworzenie środowiska wirtualnego
python3 -m venv speedtest_env
source speedtest_env/bin/activate

# Instalacja zależności
pip install -r requirements.txt

# Uruchamianie
python3 sp.py              # CLI
python3 speedtest_gui.py   # GUI
```

---

## ⚙️ Konfiguracja

### Tworzenie konfiguracji
```bash
# Utworzenie przykładowej konfiguracji
speedtest-cli --create-config

# Edycja konfiguracji
nano speedtest_config.json
```

### Przykład konfiguracji
```json
{
  "bits_to_mbps": 1000000,
  "speedtest_timeout": 60,
  "max_retries": 3,
  "show_detailed_progress": true
}
```

---

## 🖥️ Interfejsy użytkownika

### 1. CLI (Linia komend)
```bash
speedtest-cli                    # Podstawowy test
speedtest-cli --create-config    # Utworzenie konfiguracji
```

**Funkcje:**
- ✅ Test download/upload/ping
- ✅ Automatyczny retry przy błędach
- ✅ Walidacja wyników
- ✅ Kolorowy output

### 2. GUI (Interfejs graficzny)
```bash
speedtest-gui                    # Material Design GUI
speedtest-gui-fallback          # Alternatywny GUI
```

**Funkcje:**
- ✅ Material Design
- ✅ Real-time progress
- ✅ Anulowanie testów
- ✅ Graficzne wyniki

### 3. Scheduler (Automatyzacja)
```bash
speedtest-scheduler --immediate              # Jednorazowy test
speedtest-scheduler --interval 30           # Co 30 minut  
speedtest-scheduler --stats --days 7        # Statystyki
```

**Funkcje:**
- ✅ Automatyczne testy
- ✅ Zapis do bazy danych
- ✅ Statystyki historyczne
- ✅ Export danych

---

## 📊 Zarządzanie danymi

### Wyświetlanie statystyk
```bash
speedtest-storage stats --days 30           # Ostatnie 30 dni
speedtest-storage info                      # Info o bazie
```

### Export danych
```bash
speedtest-storage export csv wyniki.csv     # Export do CSV
speedtest-storage export json dane.json    # Export do JSON
```

### Czyszczenie starych danych
```bash
speedtest-storage cleanup --keep-days 365   # Usuń starsze niż rok
```

---

## 🔧 Rozwiązywanie problemów

### GUI nie uruchamia się (Python 3.13+)
```bash
# Automatyczny patch jest stosowany podczas instalacji
# Jeśli GUI nie działa, zastosuj patch ręcznie:
source speedtest_env/bin/activate
python3 fix_speedtest_py313.py

# Sprawdź zależności GUI
python3 -c "from kivymd.app import MDApp; print('GUI OK')"

# Ustaw backend OpenGL
export KIVY_GL_BACKEND=gl

# Użyj alternatywnego GUI
speedtest-gui-fallback
```

### Problemy z siecią
```bash
# Test podstawowej łączności
ping -c 4 8.8.8.8

# Debug speedtest-cli
speedtest-cli --simple
```

### Brak uprawnień
```bash
# Naprawa uprawnień
chmod +x speedtest-*

# Instalacja użytkownika  
python3 install.py --user
```

---

## 🎯 Typowe przypadki użycia

### Jednorazowy test
```bash
speedtest-cli
```

### Monitoring w tle
```bash
# Uruchomienie w tle
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &

# Sprawdzenie statusu
tail -f speedtest.log
```

### Analiza wydajności
```bash
# Statystyki tygodniowe
speedtest-scheduler --stats --days 7

# Export dla dalszej analizy
speedtest-storage export csv "analiza-$(date +%Y%m).csv" --days 30
```

### Testowanie po zmianach w sieci
```bash
# Test przed zmianą
speedtest-cli > przed.txt

# Test po zmianie
speedtest-cli > po.txt

# Porównanie wyników
diff przed.txt po.txt
```

---

## 📁 Struktura plików

```
Speed_test/
├── speedtest-cli*           # CLI executable
├── speedtest-gui*           # GUI executable  
├── speedtest-scheduler*     # Scheduler executable
├── speedtest_config.json    # Konfiguracja użytkownika
├── speedtest_history.db     # Baza danych wyników
├── install.py*              # Installer
├── uninstall.py*            # Uninstaller
└── Makefile                 # Automatyzacja
```

---

## 🔄 Aktualizacje

### Aktualizacja kodu
```bash
git pull origin main
make update                  # Aktualizacja zależności
sudo python3 install.py     # Reinstalacja skryptów
```

### Backup danych
```bash
make backup                  # Backup konfiguracji i danych
make restore                 # Przywracanie z backup
```

---

## 🗑️ Odinstalowanie

### Częściowe (zachowaj dane)
```bash
python3 uninstall.py
```

### Kompletne (usuń wszystko)
```bash
python3 uninstall.py --remove-all
```

### Ręczne usunięcie
```bash
# Usuń pliki wykonywalne
sudo rm /usr/local/bin/speedtest-*

# Usuń katalog aplikacji
rm -rf Speed_test/
```

---

## 📞 Wsparcie

- **Błędy**: Utwórz issue na GitHub
- **Dokumentacja**: README.md, AGENTS.md, INSTALLER.md
- **Konfiguracja**: speedtest_config.json.example

---

## ⚡ Skróty poleceń

| Komenda | Opis |
|---------|------|
| `speedtest-cli` | Test CLI |
| `speedtest-gui` | Interface graficzny |
| `speedtest-scheduler --immediate` | Test jednorazowy |
| `speedtest-scheduler --interval 30` | Co 30 min |
| `speedtest-storage stats` | Statystyki |
| `make install` | Instalacja |
| `make test` | Test funkcjonalności |
| `make clean` | Czyszczenie |

**Start w 30 sekund:**
```bash
git clone repo && cd Speed_test
sudo python3 install.py
speedtest-cli --create-config
speedtest-gui
```