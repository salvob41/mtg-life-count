# MTG Life Counter

App per tenere il conto dei life point in Magic: The Gathering (2 giocatori), costruita con [Flet](https://flet.dev/).

## Requisiti

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)

## Avviare in locale

```bash
uv run flet run src/main.py
```

## Build per mobile

### Android (APK)

```bash
flet build apk
```

### iOS (IPA)

```bash
flet build ipa
```

Gli artefatti vengono generati nella cartella `build/`.

## Avviare come web app

```bash
FLET_WEB=1 uv run flet run src/main.py
```
