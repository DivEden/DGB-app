# 📱 Upload DGB Assistent til Google Play (Uden Java)

## ✅ Metode: Brug Google Play App Signing (Nemmeste)

Google Play kan selv generere og håndtere signing keys for dig. Du uploader en unsigned/debug-signed AAB, og Google tager sig af resten.

---

## 📋 Step-by-Step Guide

### 1️⃣ Byg AAB via GitHub Actions

AAB'en bliver automatisk bygget når du pusher til `main` branch.

**For at trigge et nyt build:**
```powershell
cd "c:\Users\mfed\Desktop\Python\DGB App\App"
git add .
git commit -m "Trigger build for Play Store upload"
git push origin main
```

**Eller brug manual trigger:**
1. Gå til: https://github.com/DivEden/DGB-app/actions
2. Klik på "Build Android APK" workflow
3. Klik "Run workflow" → "Run workflow"

### 2️⃣ Download AAB fra Actions

1. Gå til: https://github.com/DivEden/DGB-app/actions
2. Klik på den seneste succesfulde build (grøn checkmark ✓)
3. Scroll ned til **Artifacts**
4. Download **museum-search-app-builds**
5. Udpak zip-filen
6. Find: `dgbassistent-0.1-arm64-v8a_armeabi-v7a-release.aab`

---

### 3️⃣ Opret Google Play Console Account

1. Gå til: https://play.google.com/console
2. Log ind med Google konto
3. Betal engangsgebyr ($25 USD) hvis ikke allerede gjort
4. Accept developer terms

### 4️⃣ Opret App

1. Klik **"Create app"**
2. Udfyld:
   - **App name:** DGB Assistent
   - **Default language:** Dansk (Danmark)
   - **App or game:** App
   - **Free or paid:** Free
3. Accept policies
4. Klik **"Create app"**

---

### 5️⃣ Udfyld Obligatoriske Felter

Før du kan uploade, skal disse felter udfyldes:

#### A) Store listing (Dashboard → Store presence → Main store listing)
- **App name:** DGB Assistent
- **Short description:** Søg og udforsk museumsgenstande fra Danmarks Glamourøse Billedarkiv
- **Full description:**
  ```
  DGB Assistent gør det nemt at søge efter og udforske museumsgenstande fra 
  Danmarks samlinger. 
  
  Funktioner:
  • Søg efter genstande med objektnummer
  • Se detaljerede beskrivelser og billeder
  • Gem dine favoritter
  • Hurtig adgang til seneste søgninger
  ```
- **App icon:** Upload `museum_search_app/utils/Images/Icon.png`
- **Feature graphic:** Upload en 1024x500 px grafik (kan laves simpel)
- **Screenshots:** Tag 2-8 screenshots fra appen (min 2 påkrævet)
- **App category:** Vælg "Tools" eller "Education"
- **Contact details:** Email adresse

#### B) Data safety (Dashboard → Policy → Data safety)
Besvar spørgsmål om:
- Hvilke data indsamles? (Sandsynligvis: Ingen persondata)
- Deles data? (Sandsynligvis: Nej)
- Sikkerhedspraksis

#### C) Content rating (Dashboard → Policy → App content)
- Udfyld IARC questionnaire
- Vælg passende aldersgruppe (sandsynligvis "Everyone")

#### D) Target audience (Dashboard → Policy → Target audience)
- Vælg aldersgrupper (fx "18 and over")

#### E) App access (Dashboard → Policy → App access)
- Vælg "All functionality is available without special access"

#### F) Ads (Dashboard → Policy → Ads)
- Vælg "No" hvis appen ikke viser annoncer

---

### 6️⃣ Upload AAB og Aktivér App Signing

#### A) Start Internal Testing (Anbefalet først)
1. Gå til: **Release → Testing → Internal testing**
2. Klik **"Create new release"**

#### B) Upload AAB
1. Under "App bundles" klik **"Upload"**
2. Vælg din `.aab` fil
3. Vent på upload og validering

#### C) ⭐ VIGTIGT: Aktivér Google Play App Signing

**Når du uploader første gang vises:**
```
┌────────────────────────────────────────────┐
│  Use Google Play App Signing              │
├────────────────────────────────────────────┤
│                                            │
│  ● Let Google manage and protect your app │
│    signing key (recommended)               │
│                                            │
│            [ Continue ]                    │
└────────────────────────────────────────────┘
```

**✅ VÆLG denne option!**

Google vil nu:
- ✅ Generere en production signing key
- ✅ Signere din app med den key
- ✅ Gemme key'en sikkert
- ✅ Håndtere alle fremtidige signings automatisk

#### D) Hvis du får "All uploaded bundles must be signed" fejl:

**Dette burde IKKE ske**, men hvis det gør:

1. Download og installer Java JDK fra terminal:
   ```powershell
   winget install EclipseAdoptium.Temurin.17.JDK
   ```

2. Genstart PowerShell og opret keystore:
   ```powershell
   cd "c:\Users\mfed\Desktop\Python\DGB App\App"
   keytool -genkey -v -keystore upload.jks -alias upload -keyalg RSA -keysize 2048 -validity 10000
   ```

3. Følg min anden guide for at tilføje keystore til GitHub Secrets

---

### 7️⃣ Færdiggør Release

1. **Release name:** 0.1 - Initial Release
2. **Release notes (dansk):**
   ```
   Første version af DGB Assistent
   
   Funktioner:
   • Søg efter museumsgenstande via objektnummer
   • Se detaljer, billeder og beskrivelser
   • Gem favorit-objekter
   • Hurtig adgang til seneste søgninger
   ```

3. Klik **"Review release"**
4. Klik **"Start rollout to Internal testing"**

---

### 8️⃣ Tilføj Testere (Internal Testing)

1. Gå til **Release → Testing → Internal testing → Testers tab**
2. Opret en tester liste
3. Tilføj email adresser på testere
4. Del test link med testere

---

### 9️⃣ Promover til Production

Når du er klar til at gå live:

1. Gå til **Release → Testing → Internal testing**
2. Find din release
3. Klik **"Promote release"**
4. Vælg **"Production"**
5. Review og klik **"Start rollout to Production"**

Google reviewer appen (kan tage timer til dage).

---

## 🔄 Fremtidige Updates

### Når du skal udgive opdatering:

1. **Opdater version i `buildozer.spec`:**
   ```ini
   version = 0.2
   ```

2. **Commit og push:**
   ```powershell
   git add buildozer.spec
   git commit -m "Bump version to 0.2"
   git push origin main
   ```

3. **Download ny AAB fra Actions**

4. **Upload til Play Console:**
   - Samme process som før
   - Google signerer automatisk med samme key
   - Ingen keystore management nødvendigt!

---

## 📊 Verificér App Signing

Efter første upload, tjek:

**Release → Setup → App signing**

Du skulle se:
```
✅ Google Play App Signing: Active

App signing key certificate (Google's key)
SHA-1: XX:XX:XX:...

Upload key certificate (GitHub Actions debug key)  
SHA-1: YY:YY:YY:...
```

---

## 🆘 Troubleshooting

### "All uploaded bundles must be signed"
- Buildozer skulle signere med debug key automatisk
- Hvis ikke, installer Java og følg keystore guide

### "Your app bundle is not optimized"
- Dette er kun en advarsel, ikke en fejl
- Kan ignoreres

### "Missing required assets"
- Udfyld alle felter i Store Listing
- Upload mindst 2 screenshots

### "Content rating required"
- Udfyld IARC questionnaire under App Content

---

## ✅ Checklist

- [ ] Build AAB via GitHub Actions
- [ ] Download AAB fra artifacts
- [ ] Opret Google Play Console account
- [ ] Opret app
- [ ] Udfyld Store Listing (navn, beskrivelse, screenshots)
- [ ] Udfyld Data Safety
- [ ] Udfyld Content Rating
- [ ] Upload AAB til Internal Testing
- [ ] Vælg "Let Google manage signing"
- [ ] Udfyld release notes
- [ ] Start rollout
- [ ] Test med internal testers
- [ ] Promover til production når klar

---

## 📞 Hvis du har brug for hjælp

Spørg mig om:
- Screenshots fra appen
- Feature graphic design
- Store listing beskrivelse
- Data safety svar
- Troubleshooting upload problemer
