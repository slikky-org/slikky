# 📘 SLIKKY – Versielogboek (vanaf 6 april 2025, ISO-nummersysteem)

Overzicht van alle versies van `voedingsadvies.py` met ISO-chronologie en beschrijvingen.

---

## ✅ Versie BU20250406-01  
**Datum:** 2025-04-06  
**Status:** ✅ Getest  

**Wijzigingen:**  
- Eerste backup onder ISO-structuur  
- Overstap naar veilige testwijze met terugzetten werkende versie  
- Eerste versie met gescheiden filtersysteem voorbereid

---

## ✅ Versie BU20250407-01  
**Datum:** 2025-04-07  
**Status:** ✅ Getest  

**Wijzigingen:**  
- Filtersysteem actief: gluten, varkensvlees, lactose, suiker, noten, rauw voedsel  
**Let op:** Het filtersysteem is in deze versie getest maar uiteindelijk **niet geïmplementeerd** vanwege foutmeldingen. Wordt herzien in een latere versie.  
- Subheader '🔍 Voedingsmiddelenfilter (optioneel)' toegevoegd  
- Back-up BU0704002 als stabiele versie teruggezet

---

## ✅ Versie BU20250407-02  
**Datum:** 2025-04-07  
**Status:** ✅ Getest  

**Wijzigingen:**  
- Kleine update na filtertest  
- Bugfix of optimalisatie van UI verwacht

---

## ✅ Versie BU20250408-01  
**Datum:** 2025-04-08  
**Status:** ✅ Getest  

**Wijzigingen:**  
- Logica toegevoegd voor eetondersteuning bij toezicht = 'Ja'  
- Extra veld verplicht zichtbaar bij hulpbehoefte  
- Velden dynamisch en afhankelijk van input

---

## ✅ Versie BU20250409-01  
**Datum:** 2025-04-09  
**Status:** ✅ Getest / ✅ Gepusht naar GitHub  

**Wijzigingen:**  
- Volledige stabilisatieversie  
- Standaard IDDSI-waarde op Niveau 7  
- Filtersysteem compleet  
- Toezicht- & hulpveld goed werkend  
- Interface opgeschoond en foutvrij getest

**Back-up locatie:**  
- `backup_0904/BU20250409-01.py`

---

## ✅ Versie BU20250418-01  
**Datum:** 2025-04-18  
**Status:** ✅ Getest / ✅ Gepusht naar GitHub  

**Wijzigingen:**  
- Promptregel aangepast zodat AI-output in de basisversie maximaal 3 suggesties per onderdeel geeft  
- Getest met voorbeeldadviezen (zoals 'Piet Janssen') en gecontroleerd in PDF-output  
- Geen verdere codewijziging nodig dankzij duidelijke instructie aan GPT in de prompt

---
## ✅ Versie BU20250424-01  
**Datum:** 2025-04-24  
**Status:** ✅ Getest / ✅ Gepusht naar GitHub / ✅ Gedeployed op Streamlit  

**Wijzigingen:**  
- Eerste officiële versie van `slikky_pro_v1_250424.py` (SLIKKY® Premium)
- Volledige integratie van OpenAI-call en promptopbouw in premiumformaat
- Nieuwe PDF-export met vetgedrukte regels en begeleidingswaarschuwingen
- Filtersysteem voor uitsluitingen actief en dynamisch toegepast
- IDDSI-integratie (vast en vloeibaar), geldigheidslogica en locatie-/auteurvermelding
- App live gezet op Streamlit: [slikky-premium-v1.streamlit.app](https://slikky-premium-v1.streamlit.app)
- Secrets-omgeving correct ingericht op Streamlit (API-key beveiligd)
- README.md toegevoegd in repo  
- Tijdelijk openbaar gezet, upgrade- en privacymogelijkheden worden onderzocht

**Bestandsnaam:**  
- `slikky_pro_v1_250424.py`

---

