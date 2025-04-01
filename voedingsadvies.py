import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import locale
try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

from fpdf import FPDF
from io import BytesIO
import datetime


# Laad de API key uit het .env-bestand
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Resetlogica
if st.session_state.get("reset", False):
    import datetime
    st.session_state["gender"] = "Dhr."
    st.session_state["naam"] = ""
    st.session_state["geboortedatum"] = datetime.date(2000, 1, 1)
    st.session_state["zorgorganisatie"] = ""
    st.session_state["locatie"] = ""
    st.session_state["advies_datum"] = datetime.date.today()
    st.session_state["geldigheid"] = "4 weken"
    st.session_state["geldigheid_datum"] = datetime.date.today()
    st.session_state["auteur"] = ""
    st.session_state["functie"] = ""
    st.session_state["advies"] = ""
    st.session_state["toezicht"] = None
    st.session_state["iddsi_vast"] = "Niveau 7: Normaal - makkelijk te kauwen"
    st.session_state["iddsi_vloeibaar"] = "Niveau 0: Dun vloeibaar"
    st.session_state["allergie"] = ""
    st.session_state["voorkeuren"] = ""
    st.session_state["reset"] = False
    st.rerun()

# Streamlit UI
st.image("logo_slikky.png", width=150)
st.markdown("### Voedingsadvies bij slikproblemen")
st.write("Voer het logopedisch advies in, geef IDDSI-niveaus en specifieke voorkeuren op.")

# Gegevens cliënt
st.subheader("📅 Cliëntgegevens (worden niet opgeslagen)")
col1, col2, col3 = st.columns([1, 3, 2])
client_gender = col1.selectbox("Aanhef:", ["Dhr.", "Mevr.", "X"], key="gender")
client_naam = col2.text_input("Naam van de cliënt:", key="naam")
client_geboortedatum = col3.date_input("Geboortedatum:", format="DD/MM/YYYY", min_value=datetime.date(1933, 1, 1), max_value=datetime.date.today(), key="geboortedatum")

col_org1, col_org2 = st.columns([2, 2])
zorgorganisatie = col_org1.text_input("Zorgorganisatie:", key="zorgorganisatie")
locatie = col_org2.text_input("Locatie:", key="locatie")

col4, col5 = st.columns([2, 2])
advies_datum = col4.date_input("Datum aanmaak voedingsadvies:", format="DD/MM/YYYY", key="advies_datum")
geldigheid_optie = col5.selectbox("Geldig voor:", ["4 weken", "6 weken", "8 weken", "Anders"], key="geldigheid")

if geldigheid_optie == "Anders":
    col6, _ = st.columns([2, 2])
    geldigheid_datum = col6.date_input("Kies einddatum:", format="DD/MM/YYYY", key="geldigheid_datum")
else:
    geldigheid_datum = None

col_creator1, col_creator2 = st.columns([2, 2])
aangemaakt_door = col_creator1.text_input("Aangemaakt door:", key="auteur")
functie = col_creator2.text_input("Functie:", key="functie")

# Invoervelden
advies = st.text_area("📜 Logopedisch advies:", key="advies")
onder_toezicht_optie = st.radio(
    "🚨 Moet de cliënt eten onder toezicht?",
    options=["Ja", "Nee"],
    index=None,
    key="toezicht",
    help="Selecteer een van beide opties om verder te gaan."
)
iddsi_vast = st.selectbox("🍽️ Niveau voor voedsel:", [
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Glad gemalen",
    "Niveau 5: Fijngemalen en smeuïg",
    "Niveau 6: Zacht & klein gesneden",
    "Niveau 7: Normaal - makkelijk te kauwen"
], key="iddsi_vast")
iddsi_vloeibaar = st.selectbox("🥤 Niveau voor vloeistof:", [
    "Niveau 0: Dun vloeibaar",
    "Niveau 1: Licht vloeibaar",
    "Niveau 2: Matig vloeibaar",
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Zeer dik vloeibaar"
], key="iddsi_vloeibaar")
allergieën = st.text_input("⚠️ Allergieën (optioneel, scheid met komma's):", key="allergie")
voorkeuren = st.text_input("✅ Voedselvoorkeuren (optioneel, scheid met komma's):", key="voorkeuren")

advies_output = ""

# Genereer het voedingsadvies
if st.button("🎯 Genereer Voedingsprogramma"):
    if not advies:
        st.warning("⚠️ Voer eerst een logopedisch advies in.")
    elif onder_toezicht_optie not in ["Ja", "Nee"]:
        st.warning("⚠️ Kies of de cliënt onder toezicht moet eten.")
    else:
        toezicht_tekst = "De cliënt moet eten onder toezicht." if onder_toezicht_optie == "Ja" else "De cliënt hoeft niet onder toezicht te eten."
        client_label = f"{client_gender} {client_naam} ({client_geboortedatum.strftime('%d/%m/%Y')})"
        geldigheid_tekst = geldigheid_datum.strftime('%d/%m/%Y') if geldigheid_datum else f"{geldigheid_optie} vanaf {advies_datum.strftime('%d/%m/%Y')}"

        prompt = f"""
Je bent een AI-diëtist die voedingsprogramma's opstelt op basis van logopedisch advies.

Toon deze regels vetgedrukt bovenaan het advies:
**Dit voedingsadvies is bedoeld voor {client_label}.**
**Geldig tot: {geldigheid_tekst}**
**Zorgorganisatie: {zorgorganisatie} | Locatie: {locatie}**
**Aangemaakt door: {aangemaakt_door} ({functie})**

**1. Logopedisch advies**  
Herhaal het advies dat is ingevoerd.

**2. Vertaling naar voedingsplan**  
Leg kort uit hoe je dit advies hebt vertaald naar een aangepast voedingsplan.

**3. Belangrijke gegevens**  
- Logopedisch advies: {advies}  
- Allergieën: {allergieën}  
- Voedselvoorkeuren: {voorkeuren}  
- Niveau voor voedsel: {iddsi_vast}  
- Niveau voor vloeistof: {iddsi_vloeibaar}  
- {toezicht_tekst}

**4. Concreet voedingsprogramma**  
- Geef aanbevolen voedingsmiddelen  
- Benoem te vermijden voeding  
- Geef een voorbeeld dagmenu (ontbijt, lunch, diner, tussendoor)  
- Geef alternatieven bij voorkeuren of allergieën

Gebruik in het advies dezelfde Nederlandse IDDSI-terminologie zoals hierboven vermeld.  
Zorg dat het advies duidelijk, praktisch en bruikbaar is voor een zorgverlener. Vermeld duidelijk als eten onder toezicht moet gebeuren.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Je bent een AI gespecialiseerd in voedingsadvies voor cliënten met slikproblemen."},
                    {"role": "user", "content": prompt}
                ]
            )
            advies_output = response.choices[0].message.content

            if onder_toezicht_optie == "Ja":
                st.subheader("🚨 Belangrijke waarschuwing")
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">🚨 Deze persoon mag alleen eten onder toezicht!</div>',
                    unsafe_allow_html=True
                )

            st.subheader("📋 Voedingsadvies:")
            st.write(advies_output)

        except Exception as e:
            st.error(f"Er ging iets mis bij het ophalen van het advies: {e}")

# Download als PDF
if advies_output:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
    font_bold_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans-Bold.ttf')
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.add_font('DejaVu', 'B', font_bold_path, uni=True)
    pdf.set_font('DejaVu', size=12)
    pdf.image("logo_slikky.png", x=10, y=8, w=40)
    pdf.ln(20)

    pdf.multi_cell(0, 10, "---")
    pdf.multi_cell(0, 10, "Deze app slaat géén cliëntgegevens op. Alle ingevoerde data verdwijnt zodra het advies is gegenereerd.")
    pdf.multi_cell(0, 10, "---")

    if onder_toezicht_optie == "Ja":
        pdf.set_fill_color(255, 204, 204)
        pdf.set_text_color(153, 0, 0)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.multi_cell(0, 10, "🚨 Deze persoon mag alleen eten onder toezicht!", border=1, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVu', size=12)

    for line in advies_output.split("\n"):
        pdf.multi_cell(0, 10, line)


    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)


    st.download_button(
        label="💾 Opslaan als PDF",
        data=buffer,
        file_name=f"voedingsadvies_{client_naam.replace(' ', '')}{client_geboortedatum.strftime('%d%m%Y')}.pdf",
        mime="application/pdf"
    )

    st.markdown("""
    ---
    *Deze app slaat géén cliëntgegevens op. Alle ingevoerde data verdwijnt zodra het advies is gegenereerd.*
    """)

# Resetknop onderaan
if st.button("🔁 Formulier resetten"):
    st.session_state["reset"] = True
    st.rerun()
