import streamlit as st
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Radar Immo - Debug", layout="wide")
st.title("🏠 Radar Immo : Debug - Embourg · Beaufays · Chaudfontaine")

sources = [
    "immoweb.be",
    "immovlan.be",
    "zimmo.be"  # Ajout d'une 3e source pour plus de résultats
]

zones = ["Embourg", "Beaufays", "Chaudfontaine"]

def enrich(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("meta", property="og:title")
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

def search_duckduckgo(query, max_results=10):
    try:
        results = ddg(query, max_results=max_results)
        st.write(f"🔍 Résultats bruts pour : {query}", results)  # Affichage debug
        return [r['href'] for r in results if 'href' in r]
    except Exception as e:
        st.error(f"Erreur DuckDuckGo pour '{query}': {e}")
        return []

if st.button("🔍 Lancer la recherche"):
    all_results = []
    with st.spinner("Recherche en cours..."):
        for zone in zones:
            for source in sources:
                query = f"site:{source} maison à vendre {zone}"
                urls = search_duckduckgo(query, max_results=10)
                for url in urls:
                    enriched = enrich(url)
                    all_results.append(enriched)
    df = pd.DataFrame(all_results)
    st.dataframe(df, use_container_width=True)
