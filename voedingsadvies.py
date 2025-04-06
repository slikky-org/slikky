import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI
import locale
from io import BytesIO
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Image
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle

try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

if st.session_state.get("reset", False):
    st.session_state.update({
        "gender": "Dhr.",
        "naam": "",
        "geboortedatum": datetime.date(2000, 1, 1),
        "zorgorganisatie": "",
        "locatie": "",
        "advies_datum": datetime.date.today(),
        "geldigheid": "4 weken",
        "geldigheid_datum": datetime.date.today(),
        "auteur": "",
        "functie": "",
        "advies": "",
        "toezicht": None,
        "iddsi_vast": "Niveau 7: Normaal - makkelijk te kauwen",
        "iddsi_vloeibaar": "Niveau 0: Dun vloeibaar",
        "allergie": "",
        "voorkeuren": "",
        "reset": False
    })
    st.rerun()

st.image("logo_slikky.png", width=150)
st.markdown("### Voedingsadvies bij slikproblemen")
st.write("Voer het logopedisch advies in, geef IDDSI-niveaus en specifieke voorkeuren op.")

st.subheader("\U0001F4C5 Cliëntgegevens (worden niet opgeslagen)")
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

advies = st.text_area("\U0001F4DC Logopedisch advies:", key="advies")
onder_toezicht_optie = st.radio(
    "\U0001F6A8 Moet de cliënt eten onder toezicht?",
    options=["Ja", "Nee"],
    index=None,
    key="toezicht",
    help="Selecteer een van beide opties om verder te gaan."
)
iddsi_vast = st.selectbox("\U0001F37D️ Niveau voor voedsel:", [
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Glad gemalen",
    "Niveau 5: Fijngemalen en smeuïg",
    "Niveau 6: Zacht & klein gesneden",
    "Niveau 7: Normaal - makkelijk te kauwen"
], key="iddsi_vast")
iddsi_vloeibaar = st.selectbox("\U0001F964 Niveau voor vloeistof:", [
    "Niveau 0: Dun vloeibaar",
    "Niveau 1: Licht vloeibaar",
    "Niveau 2: Matig vloeibaar",
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Zeer dik vloeibaar"
], key="iddsi_vloeibaar")
allergieën = st.text_input("⚠️ Allergieën (optioneel, scheid met komma's):", key="allergie")
voorkeuren = st.text_input("✅ Voedselvoorkeuren (optioneel, scheid met komma's):", key="voorkeuren")
advies_output = ""

if st.button("\U0001F3AF Genereer Voedingsprogramma"):
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
                st.subheader("\U0001F6A8 Belangrijke waarschuwing")
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">\U0001F6A8 Deze persoon mag alleen eten onder toezicht!</div>',
                    unsafe_allow_html=True
                )

            st.subheader("\U0001F4CB Voedingsadvies:")
            st.write(advies_output)

        except Exception as e:
            st.error(f"Er ging iets mis bij het ophalen van het advies: {e}")

if advies_output:
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    elements = []

    # Stijlen
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Body', fontSize=11, leading=16, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='BoldBox', fontSize=12, leading=16, alignment=TA_LEFT, textColor=colors.red))
    styles.add(ParagraphStyle(name='Small', fontSize=9, leading=12, alignment=TA_LEFT))

    # Adviesregels verwerken in PDF
    for regel in advies_output.split("\n"):
        if regel.strip() != "":
            elements.append(Paragraph(regel.strip(), styles['Body']))
            elements.append(Spacer(1, 6))

    # Disclaimer IDDSI
    elements.append(Spacer(1, 160))
    iddsi_disclaimer = "Het gebruik van het IDDSI-framework in dit document is in overeenstemming met de CC BY-SA 4.0 licentie.\nZie iddsi.org voor meer informatie."
    elements.append(Paragraph(iddsi_disclaimer, styles["Small"]))

    # Merkvermelding
    elements.append(Spacer(1, 36))
    elements.append(Paragraph("SLIKKY is een officieel geregistreerd merk (Benelux, 2025)", styles['Body']))
    elements.append(Spacer(1, 12))

    # Logo onderaan
    try:
        merkbadge = Image("images/logo_slikky.png", width=5.0*cm, height=5.0*cm)
        merkbadge.hAlign = 'CENTER'
        elements.append(merkbadge)
    except Exception as e:
        elements.append(Paragraph("⚠️ Merkbadge niet gevonden: " + str(e), styles['Body']))

    # Pagina-header/footer
    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        titel = f"Voedingsadvies voor {client_gender} {client_naam} ({client_geboortedatum.strftime('%d/%m/%Y')})"
        canvas.drawString(2 * cm, A4[1] - 1.5 * cm, titel)
        page_num = f"Pagina {doc.page}"
        canvas.drawRightString(A4[0] - 2 * cm, 1.5 * cm, page_num)
        canvas.restoreState()

    pdf.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)

    st.download_button(
        label="\U0001F4BE Opslaan als PDF",
        data=buffer,
        file_name=f"voedingsadvies_{client_naam.replace(' ', '')}{client_geboortedatum.strftime('%d%m%Y')}.pdf",
        mime="application/pdf"
    )