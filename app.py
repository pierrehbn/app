import streamlit as st
from duckduckgo_search import DuckDuckGoSearch
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Radar Immo - Tri Localisé", layout="wide")
st.title("🏠 Radar Immo : Annonces à Embourg · Beaufays · Chaudfontaine")

sources = [
    "immoweb.be",
    "immovlan.be",
    "zimmo.be",
    "logic-immo.be",
    "trevi.be",
    "weinvest.be",
    "century21.be",
    "immoscoop.be"
]

zones = ["Embourg", "Beaufays", "Chaudfontaine"]
all_results = []

def enrich(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("meta", property="og:title")
        description = soup.find("meta", property="og:description")

        full_text = soup.get_text(separator=' ')
        price_match = ""
        address_match = ""

        for line in full_text.splitlines():
            if "€" in line and any(x in line.lower() for x in ["prix", "€"]):
                price_match = line.strip()
                break

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

def search_duckduckgo(query, max_results=5):
    ddg = DuckDuckGoSearch()
    results = ddg.text(query, max_results=max_results)
    return [result['href'] for result in results]

with st.spinner("Recherche en cours..."):
    for zone in zones:
        for source in sources:
            query = f"site:{source} maison à vendre {zone}"
            urls = search_duckduckgo(query)
            for url in urls:
                if any(domain in url for domain in sources):
                    enriched = enrich(url)
                    all_results.append(enriched)

df = pd.DataFrame(all_results)
st.dataframe(df, use_container_width=True)
