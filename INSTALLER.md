# Instalacja i Konfiguracja Speed Test Tool

## Instrukcja Instalacji Kompletnej Aplikacji

### 1. Przygotowanie Systemu

#### Ubuntu/Debian:
```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Python 3.8+ i narzędzi
sudo apt install -y python3 python3-pip python3-venv git

# Instalacja zależności systemowych dla GUI (Kivy)
sudo apt install -y python3-dev build-essential libssl-dev libffi-dev \
    libgstreamer-1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    libgl1-mesa-dev libglu1-mesa-dev freeglut3-dev libjpeg-dev libpng-dev

# Dla starszych systemów może być potrzebne:
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y python3 python3-pip python3-devel git

# Fedora
sudo dnf update -y
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel git

# Zależności GUI
sudo yum install -y mesa-libGL-devel mesa-libGLU-devel freeglut-devel \
    libjpeg-turbo-devel libpng-devel SDL2-devel
```

### 2. Pobieranie i Instalacja Aplikacji

```bash
# Klonowanie repozytorium
git clone https://github.com/twój-użytkownik/Speed_test.git
cd Speed_test

# Tworzenie środowiska wirtualnego
python3 -m venv speedtest_env

# Aktywacja środowiska
source speedtest_env/bin/activate  # Linux/macOS
# lub na Windows: speedtest_env\Scripts\activate

# Instalacja zależności
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Tworzenie Plików Uruchamialnych

#### A. Skrypty uruchamialne (utworzone automatycznie przez installer)

**speedtest-cli** - CLI Interface:
```bash
#!/bin/bash
cd "$(dirname "$0")"
source speedtest_env/bin/activate
python3 sp.py "$@"
```

**speedtest-gui** - GUI Interface:
```bash
#!/bin/bash
cd "$(dirname "$0")"
source speedtest_env/bin/activate
python3 speedtest_gui.py "$@"
```

**speedtest-scheduler** - Background Scheduler:
```bash
#!/bin/bash
cd "$(dirname "$0")"
source speedtest_env/bin/activate
python3 scheduled_testing.py "$@"
```

### 4. Instalacja Systemowa (opcjonalna)

```bash
# Uruchomienie automatycznego instalatora
chmod +x install.py
sudo python3 install.py

# Lub ręcznie:
sudo cp speedtest-* /usr/local/bin/
sudo chmod +x /usr/local/bin/speedtest-*

# Tworzenie linków symbolicznych
sudo ln -sf /usr/local/bin/speedtest-cli /usr/bin/speedtest-cli
sudo ln -sf /usr/local/bin/speedtest-gui /usr/bin/speedtest-gui
sudo ln -sf /usr/local/bin/speedtest-scheduler /usr/bin/speedtest-scheduler
```

### 5. Konfiguracja

```bash
# Utworzenie przykładowej konfiguracji
speedtest-cli --create-config

# Edycja konfiguracji
nano speedtest_config.json

# Testowanie konfiguracji
speedtest-cli
```

### 6. Użytkowanie

#### CLI (Linia Komend):
```bash
# Podstawowy test prędkości
speedtest-cli

# Utworzenie konfiguracji
speedtest-cli --create-config

# Test z automatycznym zapisem do bazy
speedtest-scheduler --immediate
```

#### GUI (Interfejs Graficzny):
```bash
# Uruchomienie interfejsu graficznego
speedtest-gui

# Aplikacja uruchomi się w oknie z Material Design
```

#### Scheduler (Automatyczne testy):
```bash
# Test jednorazowy z zapisem
speedtest-scheduler --immediate

# Automatyczne testy co 30 minut
speedtest-scheduler --interval 30

# Wyświetlenie statystyk z ostatnich 7 dni
speedtest-scheduler --stats --days 7

# Uruchomienie w tle jako daemon
nohup speedtest-scheduler --interval 60 > speedtest.log 2>&1 &
```

### 7. Integracja z Systemem

#### Systemd Service (Linux):
```bash
# Utworzenie pliku usługi
sudo tee /etc/systemd/system/speedtest.service << EOF
[Unit]
Description=Speed Test Scheduler
After=network.target

[Service]
Type=simple
User=speedtest
Group=speedtest
WorkingDirectory=/home/speedtest/Speed_test
ExecStart=/home/speedtest/Speed_test/speedtest-scheduler --interval 60
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Włączenie i uruchomienie usługi
sudo systemctl daemon-reload
sudo systemctl enable speedtest.service
sudo systemctl start speedtest.service

# Sprawdzenie statusu
sudo systemctl status speedtest.service
```

#### Desktop Entry (GUI Application):
```bash
# Utworzenie .desktop file
tee ~/.local/share/applications/speedtest.desktop << EOF
[Desktop Entry]
Name=Speed Test Tool
Comment=Internet Speed Testing Application
Exec=/usr/local/bin/speedtest-gui
Icon=/home/$USER/Speed_test/icon.png
Terminal=false
Type=Application
Categories=Network;Utility;
EOF

# Aktualizacja cache aplikacji
update-desktop-database ~/.local/share/applications/
```

### 8. Rozwiązywanie Problemów

#### Problemy z GUI:
```bash
# Sprawdzenie instalacji Kivy
python3 -c "import kivy; print(kivy.__version__)"
python3 -c "from kivymd.app import MDApp; print('GUI OK')"

# Problemy z OpenGL
export KIVY_GL_BACKEND=gl
export LIBGL_ALWAYS_INDIRECT=1  # Dla X11 forwarding

# Alternatywne GUI
speedtest-gui-fallback  # Jeśli główne GUI nie działa
```

#### Problemy z siecią:
```bash
# Test łączności
ping -c 4 8.8.8.8

# Test speedtest-cli
pip install speedtest-cli
speedtest-cli --simple

# Debugowanie z verbose
speedtest-cli --create-config
# Edytuj speedtest_config.json: "show_detailed_progress": true
```

#### Problemy z uprawnieniami:
```bash
# Sprawdzenie uprawnień
ls -la speedtest-*
chmod +x speedtest-*

# Naprawa uprawnień virtualenv
chown -R $USER:$USER speedtest_env/
```

### 9. Aktualizacje

```bash
# Aktualizacja kodu
git pull origin main

# Aktualizacja zależności
source speedtest_env/bin/activate
pip install --upgrade -r requirements.txt

# Ponowna instalacja skryptów
sudo python3 install.py
```

### 10. Deinstalacja

```bash
# Usunięcie plików systemowych
sudo rm -f /usr/local/bin/speedtest-*
sudo rm -f /usr/bin/speedtest-*

# Usunięcie usługi systemd
sudo systemctl stop speedtest.service
sudo systemctl disable speedtest.service
sudo rm -f /etc/systemd/system/speedtest.service
sudo systemctl daemon-reload

# Usunięcie .desktop file
rm -f ~/.local/share/applications/speedtest.desktop

# Usunięcie folderu aplikacji
cd ..
rm -rf Speed_test
```

## Wsparcie

- **Problemy**: Utwórz issue w repozytorium GitHub
- **Dokumentacja**: Sprawdź README.md i AGENTS.md
- **Konfiguracja**: Przykłady w speedtest_config.json.example

## Wymagania Systemowe

- **Python**: 3.6 lub nowszy (zalecane 3.8+)
- **RAM**: Minimum 512 MB (zalecane 1 GB)
- **Dysk**: 100 MB wolnego miejsca
- **Sieć**: Połączenie internetowe do testowania
- **GUI**: X11/Wayland dla interfejsu graficznego