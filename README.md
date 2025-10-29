# DGB Assistent

En moderne museumssøgeapp til at søge og udforske samlingsobjekter fra DGB's SARA database.

## 🚀 Features

- **🔍 Avanceret søgning**: Søg efter objektnummer, titel, beskrivelse og mere
- **📱 Mobil-venlig**: Optimeret til både desktop og Android
- **🖼️ Billedgalleri**: Se billeder af museumsobjekter med thumbnail navigation
- **💾 Gem favoritter**: Gem interessante objekter til senere
- **📊 Detaljeret info**: Se omfattende metadata og nye SARA database felter
- **🎨 Moderne UI**: Elegant og brugervenlig interface

## 🏛️ Nye Database Felter

Appen viser nu udvidede informationer fra SARA API:

- **📍 Placering**: Navn og kontekst
- **📥 Erhvervelse**: Accession nr., giver, begrundelse, dato
- **📜 Proveniens**: Type, betegnelse, beskrivelse  
- **👤 Ophavsmand**: Kunstner/håndværker information

## 🛠️ Teknologi

- **Framework**: Kivy 2.3.1 (Python cross-platform UI)
- **API**: SARA database med Basic Authentication
- **Build**: Buildozer til Android APK
- **Backend**: Python 3.9+

## 📱 Installation

### Desktop (Udvikling)
```bash
cd museum_search_app
pip install -r requirements.txt
python main.py
```

### Android Build
```bash
# Installer buildozer først
pip install buildozer

# Byg APK
buildozer android debug
```

## 🔧 Konfiguration

1. **SARA API**: Autentificering er konfigureret i `sara_api.py`
2. **App Icon**: Placeret i `utils/Images/Icon.png`
3. **Build Settings**: Konfigureret i `buildozer.spec`

## 📁 Projekt Struktur

```
museum_search_app/
├── main.py                 # App entry point
├── sara_api.py            # SARA API integration
├── requirements.txt       # Python dependencies
├── screens/              # App screens
│   ├── search_screen.py  # Søgeside
│   ├── results_screen.py # Resultatliste
│   ├── detail_screen.py  # Objekt detaljer
│   └── saved_screen.py   # Gemte objekter
├── components/           # UI komponenter
│   ├── result_card.py    # Resultat kort
│   ├── carousel.py       # Billedkarusel
│   └── search_bar.py     # Søgebjælke
└── utils/               # Hjælpe funktioner
    ├── data_manager.py   # Data persistering
    └── Images/          # App ikoner
```

## 🎯 Brug

1. **Søg**: Indtast søgeord eller objektnummer
2. **Bladr**: Se resultater i listeformat
3. **Detaljer**: Klik på objekt for fuld visning
4. **Gem**: Bookmark interessante objekter
5. **Galleri**: Navigate mellem billeder med thumbnails

## 🏗️ Udvikling

- **Kivy**: Cross-platform UI framework
- **Android**: Buildozer konverterer til APK
- **SARA Integration**: Authenticated API calls
- **Billeder**: Cached downloads til performance

## 📄 Licens

Udviklet til DGB museum samlingen.

## 🔄 Seneste Opdateringer

- ✅ Tilføjet 10 nye SARA database felter
- ✅ Android-kompatible billeder 
- ✅ Forbedret UI design og typografi
- ✅ App logo og branding
- ✅ Optimeret ydeevne