import os
import streamlit as st
import locale
from openai import OpenAI
from dotenv import load_dotenv

# Haal sleutel uit secrets (voor Streamlit Cloud) of uit .env (voor lokaal gebruik)
try:
    # Werkt op Streamlit Cloud
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    # Werkt lokaal via .env of systeemvariabelen
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

from io import BytesIO
import datetime
def tel_gebruik():
    bestand = 'slikky_log.csv'
    bestaat = os.path.isfile(bestand)
    tijdstip = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    if bestaat:
        with open(bestand, 'r') as file:
            regels = file.readlines()
            gebruik_id = len(regels)
    else:
        gebruik_id = 1

    with open(bestand, 'a') as file:
        if not bestaat:
            file.write('Datum,Tijd,Gebruik_ID,Advies_Type\n')  # header
        file.write(f"{tijdstip.split(',')[0]},{tijdstip.split(',')[1]},{gebruik_id},Basis\n")
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_LEFT

# Locale instellen voor datumweergave
try:
    locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')

# API sleutel laden
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Resetknop voor formulier
if st.session_state.get("reset", False):
    st.cache_data.clear()
    st.cache_resource.clear()
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
        "allergieën": "",
        "voorkeuren": "",
        "reset": False
    })
    st.rerun()

# Interface
st.image("logo_slikky.png", width=150)
st.markdown("### Voedingsadvies bij slikproblemen")

st.subheader("🔒 Cliëntgegevens (worden niet opgeslagen)")
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

advies = st.text_area("📄 Logopedisch advies:", key="advies")
onder_toezicht_optie = st.radio(
    "🚨 Moet de cliënt eten onder toezicht?",
    options=["Ja", "Nee"],
    index=None,
    key="toezicht"
)

# Extra vraag indien onder toezicht
if onder_toezicht_optie == "Ja":
    hulp_bij_eten_optie = st.radio(
        "👐 Moet de cliënt geholpen worden met eten?",
        options=["Ja", "Nee"],
        index=None,
        key="hulp_bij_eten_radio"
    )
else:
    hulp_bij_eten_optie = None

st.write("---")
st.write("👇 Kies de gewenste consistentieniveaus:")

iddsi_vast = st.selectbox("🍽️ Niveau voor voedsel:", [
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Glad gemalen",
    "Niveau 5: Fijngemalen en smeuïg",
    "Niveau 6: Zacht & klein gesneden",
    "Niveau 7: Normaal - makkelijk te kauwen"
], index=4, key="iddsi_vast")

iddsi_vloeibaar = st.selectbox("🥣 Niveau voor vloeistof:", [
    "Niveau 0: Dun vloeibaar",
    "Niveau 1: Licht vloeibaar",
    "Niveau 2: Matig vloeibaar",
    "Niveau 3: Dik vloeibaar",
    "Niveau 4: Zeer dik vloeibaar"
], key="iddsi_vloeibaar")

allergieën = st.text_input("⚠️ Allergieën (optioneel, scheid met komma's):", key="allergie")
voorkeuren = st.text_input("✅ Voedselvoorkeuren (optioneel, scheid met komma's):", key="voorkeuren")

if st.button("🎯 Genereer Voedingsprogramma"):
    if not advies:
        st.warning("⚠️ Voer eerst een logopedisch advies in.")
    elif onder_toezicht_optie not in ["Ja", "Nee"]:
        st.warning("⚠️ Kies of de cliënt onder toezicht moet eten.")
    elif onder_toezicht_optie == "Ja" and hulp_bij_eten_optie not in ["Ja", "Nee"]:
        st.warning("⚠️ Kies of de cliënt geholpen moet worden met eten.")
    else:
        st.success("✅ Alles correct ingevuld. Hier komt je advies...")

        toezicht_tekst = "De cliënt moet eten onder toezicht." if onder_toezicht_optie == "Ja" else "De cliënt hoeft niet onder toezicht te eten."
        hulp_tekst = "De cliënt moet geholpen worden met eten." if hulp_bij_eten_optie == "Ja" else ""

        client_label = f"{client_gender} {client_naam} ({client_geboortedatum.strftime('%d/%m/%Y')})"
        geldigheid_tekst = geldigheid_datum.strftime('%d/%m/%Y') if geldigheid_datum else f"{geldigheid_optie} vanaf {advies_datum.strftime('%d/%m/%Y')}"

        golden_prompt = f"""Je bent een professionele AI-diëtist en logopedisch voedingsadviseur, gespecialiseerd in het samenstellen van voedingsadviezen voor cliënten met slikproblemen.

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
- IDDSI niveau voedsel: {iddsi_vast}
- IDDSI niveau vloeistof: {iddsi_vloeibaar}
- Logopedisch advies: {advies}
- Allergieën: {allergieën}
- Voedselvoorkeuren: {voorkeuren}
- {toezicht_tekst}
- {hulp_tekst}

**4. Concreet voedingsprogramma**
- Geef maximaal 3 aanbevolen voedingsmiddelen per categorie (bijv. vast en vloeibaar)
- Benoem maximaal 3 voedingsmiddelen die moeten worden vermeden
- Geef een voorbeeld dagmenu (ontbijt, lunch, diner, tussendoor)
- Geef maximaal 3 alternatieven bij voorkeuren of allergieën

Je doel is om veilige, praktische en gevarieerde suggesties te geven die volledig voldoen aan de opgegeven IDDSI-niveaus voor vast en vloeibaar voedsel.

Belangrijke instructies:
- Houd je strikt aan bestaande, veilige voedingsmiddelen die passen bij het opgegeven IDDSI-niveau.
- Structureer je antwoord altijd in twee secties: één voor vast voedsel, één voor vloeibaar voedsel.
- Geef per sectie maximaal 3 duidelijke suggesties.
- Zorg dat de suggesties gevarieerd zijn, maar realistisch en haalbaar.
- Noem geen zelfbedachte producten of exotische, moeilijk verkrijgbare ingrediënten.
- Geef het antwoord in duidelijke, korte bullet points.
- Voeg bij ‘Vertaling naar voedingsplan’ maximaal 2 zinnen toe over hoe het advies aansluit op het IDDSI-niveau.
- Vat het logopedisch advies puntsgewijs samen (korte bullets).
- Geef bij elke vermelding onder 'Te vermijden' een korte toelichting, bijvoorbeeld "ivm allergie" of "ivm verhoogde slikrisico’s".
- Bied bij elke allergie of intolerantie minimaal twee alternatieve voedingsopties aan.
- Geef bij 'Vertaling naar voedingsplan' maximaal twee zinnen uitleg over de koppeling met de opgegeven IDDSI-niveaus.
- Vermijd dubbele of herhaalde adviezen binnen dezelfde sectie (bijvoorbeeld niet twee keer 'niet praten tijdens de maaltijd').
- Sluit af met een vriendelijke, bemoedigende zin.

Focuspunten:
- Veiligheid en gemak zijn belangrijker dan creativiteit.
- Schrijf begrijpelijk en bondig, geschikt voor zorgprofessionals.
- Vermijd herhaling van dezelfde producten in beide secties.

Antwoord altijd in de Nederlandse taal.
"""

        try:
            prompt = "Genereer het voedingsadvies op basis van bovenstaande instructies."

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": golden_prompt},
                    {"role": "user", "content": prompt}
    ]
)
            advies_output = response.choices[0].message.content

            st.subheader("🚨 Belangrijke waarschuwing")
            if onder_toezicht_optie == "Ja":
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">🚨 Deze persoon mag alleen eten onder toezicht!</div>',
                    unsafe_allow_html=True
                )
            if hulp_bij_eten_optie == "Ja":
                st.markdown(
                    '<div style="background-color:#ffcccc;padding:15px;border-radius:10px;color:#990000;font-weight:bold;">⚠️ Deze persoon moet geholpen worden met eten!</div>',
                    unsafe_allow_html=True
                )

            st.subheader("📋 Voedingsadvies:")
            st.write(advies_output)

            # PDF-GENERATIE MET VETGEDRUKTE REGELS
            buffer = BytesIO()

            try:
                pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

                elements = []
                styles = getSampleStyleSheet()
                styles.add(ParagraphStyle(name='Body', fontSize=11, leading=16, alignment=TA_LEFT))
                styles.add(ParagraphStyle(name='BoldBox', fontSize=12, leading=16, alignment=TA_LEFT, textColor=colors.red))
                styles.add(ParagraphStyle(name='BoldBody', fontSize=11, leading=16, alignment=TA_LEFT, fontName='Helvetica-Bold'))

                try:
                    logo = Image("logo_slikky.png", width=3.5*cm, height=3.5*cm)
                    elements.append(logo)
                except Exception as e:
                    elements.append(Paragraph("⚠️ Logo niet gevonden: " + str(e), styles['Body']))

                elements.append(Spacer(1, 12))
                elements.append(Paragraph("---", styles['Body']))
                elements.append(Paragraph("Deze app slaat géén cliëntgegevens op.", styles['Body']))
                elements.append(Paragraph("---", styles['Body']))
                elements.append(Spacer(1, 12))

                if onder_toezicht_optie == "Ja":
                    toezicht_box = Paragraph("\U0001F6A8 Deze persoon mag alleen eten onder toezicht!", styles["BoldBox"])
                    elements.append(toezicht_box)
                    elements.append(Spacer(1, 12))

                if hulp_bij_eten_optie == "Ja":
                    hulp_box = Paragraph("\u26A0\ufe0f Deze persoon moet geholpen worden met eten!", styles["BoldBox"])
                    elements.append(hulp_box)
                    elements.append(Spacer(1, 12))

                for regel in advies_output.split("\n"):
                    if regel.strip() != "":
                        if regel.strip().startswith("**") and regel.strip().endswith("**"):
                            tekst_zonder_sterren = regel.strip().strip("*")
                            elements.append(Paragraph(tekst_zonder_sterren, styles['BoldBody']))
                        else:
                            elements.append(Paragraph(regel.strip(), styles['Body']))
                        elements.append(Spacer(1, 6))

                elements.append(Spacer(1, 60))
                elements.append(Paragraph("SLIKKY is een officieel geregistreerd merk (Benelux, 2025)", styles['Body']))
                elements.append(Spacer(1, 40))

                try:
                    merkbadge = Image("images/logo_slikky.png", width=5.0*cm, height=5.0*cm)
                    merkbadge.hAlign = 'CENTER'
                    elements.append(merkbadge)
                except Exception as e:
                    elements.append(Paragraph("⚠️ Merkbadge niet gevonden: " + str(e), styles['Body']))

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

                tel_gebruik()

                st.download_button(
                    label="💾 Opslaan als PDF",
                    data=buffer,
                    file_name=f"voedingsadvies_{client_naam.replace(' ', '')}{client_geboortedatum.strftime('%d%m%Y')}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Er ging iets mis bij het genereren van de PDF: {e}")

        except Exception as e:
            st.error(f"Er ging iets mis bij het ophalen van het advies: {e}")

if st.button("🔁 Herstel alle velden"):
    st.session_state["reset"] = True
    st.rerun()