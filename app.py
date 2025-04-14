import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Radar Immo - Tri Localisé", layout="wide")
st.title("🏠 Radar Immo : Annonces à Embourg · Beaufays · Chaudfontaine")

# Sites d’annonces immobilières
sources = [
    "site:immoweb.be",
    "site:immovlan.be",
    "site:zimmo.be",
    "site:logic-immo.be",
    "site:trevi.be",
    "site:weinvest.be",
    "site:century21.be",
    "site:immoscoop.be"
]

# Localités ciblées
zones = ["Embourg", "Beaufays", "Chaudfontaine"]

# Stockage des résultats
all_results = []

# Fonction d’enrichissement depuis une page HTML
def enrich(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("meta", property="og:title")
        description = soup.find("meta", property="og:description")

        # Essais basiques pour capturer adresse et prix dans le texte brut
        full_text = soup.get_text(separator=' ')
        price_match = ""
        address_match = ""

        # Recherche d'un prix
        for line in full_text.splitlines():
            if "€" in line and any(x in line for x in ["prix", "€"]):
                price_match = line.strip()
                break

        # Recherche d'une adresse approximative
        for line in full_text.splitlines():
            if any(zone in line for zone in zones):
                address_match = line.strip()
                break

        return {
            "Titre": title["content"] if title else "Sans titre",
            "Prix": price_match or "Non détecté",
            "Adresse": address_match or "Non trouvée",
            "Lien": url
        }

    except Exception as e:
        return {
            "Titre": "Erreur",
            "Prix": "—",
            "Adresse": "—",
            "Lien": url
        }

# Recherche Google + enrichissement
with st.spinner("Recherche en cours..."):
    for zone in zones:
        for source in sources:
            query = f"{source} maison à vendre {zone}"
            for url in search(query, num_results=5):
                if any(domain in url for domain in sources):
                    enriched = enrich(url)
                    all_results.append(enriched)

# Affichage dans un tableau
df = pd.DataFrame(all_results)
st.dataframe(df, use_container_width=True)
