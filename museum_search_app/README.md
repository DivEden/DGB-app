# SARA Museum Søge App

En mobil applikation til at søge gennem Danmarks Geologiske og Biologiske Samling (SARA) database med objektnummer.

## 📁 Projekt Struktur

```
museum_search_app/
├── main.py              # Hoved app (Kivy interface med farver)
├── simple_main.py       # Simpel version (basic interface) 
├── sara_api.py          # SARA API integration
├── start_app.bat        # Start hoved app (Windows)
├── start_simple.bat     # Start simpel app (Windows)
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore fil
└── venv/               # Virtuelt Python miljø
```

## 🚀 Hurtig Start

### Windows
- **Hoved app**: Dobbelt-klik på `start_app.bat`
- **Simpel app**: Dobbelt-klik på `start_simple.bat`

### Manuel Start
```bash
# Aktiver virtuelt miljø
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# eller
venv\Scripts\activate.bat    # Windows CMD

# Start hoved app (anbefalet)
python main.py

# Eller start simpel app
python simple_main.py
```

## 🔍 Sådan Bruger Du Appen

1. **Start appen** med en af batch filerne
2. **Indtast objektnummer** i søgefeltet:
   - `0054x0007` - Traditionelt format
   - `12345;15` - Genstands format  
   - `AAB 1234` - AAB format
   - `1234` - Enkelt nummer
3. **Tryk Søg** for at finde objekter
4. **Se resultater** med:
   - ✅ **Korrekt titel** (fra SARA Title felt)
   - 📝 **Fuld beskrivelse** (ingen længdebegrænsning)  
   - 🖼️ **Billede status** (om objektet har billeder)
   - 📋 **Objekt detaljer** (type, nummer, SARA ID)

## 🛠️ Teknisk Info

- **Framework**: Kivy (cross-platform GUI)
- **API**: SARA database med HTTPBasicAuth
- **Sprog**: Python 3.13
- **Interface**: Dansk

## 📦 Dependencies

```
kivy>=2.3.0
kivymd>=1.2.0
requests>=2.31.0
pillow>=10.0.0
```

## 📝 Noter

- KivyMD version 1.2.0 er deprecated, derfor bruger main.py kun Kivy
- simple_main.py er en backup version med minimal interface
- Begge versioner virker med SARA API integration