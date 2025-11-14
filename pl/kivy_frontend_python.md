# Tworzenie frontendu w Pythonie z wykorzystaniem biblioteki Kivy

## Wprowadzenie

Kivy to otwartoźródłowy framework do budowania graficznych interfejsów użytkownika (GUI) napisanych w języku Python. Pozwala na tworzenie aplikacji działających multiplatformowo: na systemach Linux, Windows, macOS oraz na urządzeniach mobilnych z Androidem i iOS[4][8][10]. Kivy wyróżnia się wsparciem dla dotyku i gestów multitouch oraz możliwością szybkiego prototypowania interfejsów z wykorzystaniem własnego języka deklaratywnego — KV Language.

## Instalacja i środowisko pracy

Najlepszym rozwiązaniem jest przygotowanie osobnego środowiska wirtualnego na projekt z Kivy:

```bash
python -m venv kivy_env
source kivy_env/bin/activate  # Linux/macOS
# lub na Windows:
kivy_env\Scripts\activate
pip install kivy
```

Oficjalna dokumentacja: https://kivy.org/doc/stable/gettingstarted/installation.html

## Struktura aplikacji Kivy

Każda aplikacja Kivy składa się z klasy dziedziczącej po `kivy.app.App`, w której nadpisuje się metodę `build()` zwracającą główny widget aplikacji. Przykład minimalnego programu:

```python
from kivy.app import App
from kivy.uix.label import Label

class MainApp(App):
    def build(self):
        return Label(text="Hello, World!")

if __name__ == '__main__':
    MainApp().run()
```

Szczegółowy opis pierwszej aplikacji: https://kivy.org/doc/stable/gettingstarted/first_app.html

## Widgety — budowanie interfejsu

Podstawą każdego GUI w Kivy są widgety. Można korzystać z takich elementów jak:
- Label (etykieta)
- Button (przycisk)
- TextInput (pole tekstowe)
- Image (obraz)
- CheckBox, Switch, ProgressBar, i inne[24][30]

Układ widgetów kontrolują specjalne widgety-layouty:
- BoxLayout (układ pionowy/poziomy)
- GridLayout (siatka)
- AnchorLayout, FloatLayout, StackLayout, RelativeLayout, PageLayout[22][34][37]

Widgety można dodawać dynamicznie z poziomu kodu (metoda `.add_widget(widget)`) lub statycznie deklarować strukturę w pliku KV.

Dokumentacja wszystkich widgetów: https://kivy.org/doc/stable/api-kivy.uix.widget.html

## Język KV — oddzielanie logiki od projektu interfejsu

KV Language to język deklaratywny stworzony z myślą o łatwym i przejrzystym opisie struktury graficznej aplikacji oraz ich stylowaniu. Pliki mają rozszerzenie `.kv`[40][43][46][57].

Nazewnictwo: plik `.kv` powinien zaczynać się tak jak nazwa klasy aplikacji (np. `MainApp` → `main.kv`). Podstawowe elementy języka:

```kv
BoxLayout:
    orientation: 'vertical'
    Label:
        text: 'Nagłówek'
    Button:
        text: 'Kliknij mnie!'
        on_press: app.on_button_click()  # wywołanie funkcji z klasy App
```

Warto poznać trójkę specjalnych zmiennych:
- `app` — odnosi się do instancji klasy App
- `root` — główny widget w regule
- `self` — aktualny widget

Instrukcja: https://kivy.org/doc/stable/api-kivy.lang.html

## Własne widgety i dziedziczenie

Możliwe jest rozszerzanie własnych widgetów przez dziedziczenie po istniejących klasach (np. Button, BoxLayout) oraz nadpisywanie ich właściwości i obsługi zdarzeń (eventów). Fragment python:

```python
from kivy.uix.button import Button

class CustomButton(Button):
    def on_press(self):
        self.text = 'Naciśnięto!'
```

Odpowiadający fragment w KV:

```kv
<CustomButton>:
    background_color: 1, 0, 0, 1
```

## Obsługa zdarzeń

Kivy korzysta z tzw. event dispatchera. Własne funkcje obsługujące zdarzenia przypisuje się do widgetów poprzez wiązanie odpowiednich metod (np. `on_press`, `on_release`, `on_text`)[23][26][29][32][35]. Przykład obsługi przycisku:

```python
button = Button(text="Kliknij")
button.bind(on_press=moja_funkcja)
```

Opis: https://kivy.org/doc/stable/api-kivy.uix.button.html

## Właściwości (Properties) i bindowanie

System Properties w Kivy umożliwia automatyczne reagowanie na zmiany wartości poprzez „wiązanie” (binding) funkcji/callbacków. Przykład:

```python
from kivy.properties import StringProperty
from kivy.uix.widget import Widget

class MyWidget(Widget):
    napis = StringProperty('Domyślny tekst')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(napis=self.on_napis_zmieniony)

    def on_napis_zmieniony(self, instance, value):
        print('Nowa wartość:', value)
```

Istotna dokumentacja: https://kivy.org/doc/stable/api-kivy.properties.html

## Rysowanie na canvasie

Każdy widget ma swój własny canvas. Instrukcje rysujące (np. `Line`, `Rectangle`, `Ellipse`, `Color`) pozwalają tworzyć dowolną grafikę 2D. Przykład:

```python
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
```

Canvas potrafi być deklarowany z poziomu pliku KV (`canvas:`, `canvas.before:`, `canvas.after:`)[42][45][48][51].

## Zaawansowane funkcje i techniki

- **RecycleView** — efektywne wyświetlanie dużych zbiorów danych (np. list, tabelek)[76][82][85][91].
- **ScreenManager** — obsługa wielu ekranów i wygodne przełączanie (animacje, transitions)[77][80][83][86][89].
- **Animacje** — wbudowany system animacji użytkownika i przejść.
- **Obsługa rysowania własnych widgetów**.

Podsumowanie: https://kivy.org/doc/stable/guide/widgets.html

## Stylizowanie i Material Design — KivyMD

KivyMD to zewnętrzna biblioteka oferująca Material Design widgets: https://kivymd.readthedocs.io/
Aplikację MDApp budujemy tak samo, korzystając z MDButton, MDLabel i wielu innych, np.:

```python
from kivymd.app import MDApp
from kivy.lang import Builder

KV = '''
MDScreen:
    MDLabel:
        text: "To jest KivyMD Label"
        halign: "center"
'''

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

MainApp().run()
```

Więcej na temat Material Design: https://kivymd.readthedocs.io/en/latest/

## Pakowanie aplikacji na systemy mobilne (Android/iOS)

- **Buildozer** — Automatyzuje budowanie paczek APK/AAB na Androida:
    1. `pip install buildozer`
    2. `buildozer init`
    3. Edycja pliku `buildozer.spec`
    4. `buildozer android debug` (APK w katalogu bin)

Instrukcja krok po kroku: https://kivy.org/doc/stable/guide/packaging-android.html

Warto też poznać: https://github.com/kivy/buildozer

## Optymalizacja i dobre praktyki

- Optymalizuj użycie widgetów (unikanie zagnieżdżonych layoutów bez potrzeby)[75][81].
- Używaj RecycleView zamiast ListView dla dużych danych.
- Do wydajnych animacji korzystaj z wbudowanego systemu animacji.
- Testuj UI na różnych rozdzielczościach i DPI

Praktyki produkcyjne: https://gist.github.com/SurajDadral/02c48bd41c18ba9b427b823e4438d85d

## Linki do dokumentacji oraz zasobów edukacyjnych

- Oficjalna dokumentacja https://kivy.org/doc/stable/
- Przewodnik: https://kivy.org/doc/stable/guide/index.html
- Lista widgetów: https://kivy.org/doc/stable/api-kivy.uix.widget.html
- RecycleView: https://kivy.org/doc/stable/api-kivy.uix.recycleview.html
- KivyMD — Material Design: https://kivymd.readthedocs.io/
- Buildozer — packaging na Androida/iOS: https://github.com/kivy/buildozer
- Tutoriale „Real Python”: https://realpython.com/mobile-app-kivy-python/
- Python GUI (blog): https://pythonguis.com/tutorials/

---

> "Kivy to jedna z najciekawszych bibliotek do budowy wieloplatformowych aplikacji z graficznym interfejsem użytkownika w Pythonie zarówno na desktop, jak i Androida/iOS. Nauka jej składni, architektury i idiomatycznego wykorzystania języka KV otwiera szerokie możliwości rozwoju własnych narzędzi GUI. Dla bardziej zaawansowanych aplikacji, warto sięgnąć po KivyMD, by nadać UI spójny wygląd oraz mobilną ergonomię zgodną z Material Design."
