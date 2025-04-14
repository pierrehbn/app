import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Radar Immo - SerpApi", layout="wide")
st.title("🏠 Radar Immo (via Google API) — Embourg · Beaufays · Chaudfontaine")

sources = [
    "immoweb.be",
    "immovlan.be",
    "zimmo.be"
]

zones = ["Embourg", "Beaufays", "Chaudfontaine"]

def search_serpapi(query, num=5):
    try:
        api_key = st.secrets["serpapi_key"]
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": num,
            "hl": "fr",
            "gl": "be"
        }
        res = requests.get("https://serpapi.com/search", params=params)
        res.raise_for_status()
        results = res.json().get("organic_results", [])
        st.write(f"🔍 Résultats pour : {query}", results)
        return [r["link"] for r in results if "link" in r]
    except Exception as e:
        st.error(f"Erreur SerpApi pour '{query}': {e}")
        return []

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

if st.button("🔍 Lancer la recherche"):
    all_results = []
    with st.spinner("Recherche en cours..."):
        for zone in zones:
            for source in sources:
                query = f"site:{source} maison à vendre {zone}"
                urls = search_serpapi(query, num=5)
                for url in urls:
                    enriched = enrich(url)
                    all_results.append(enriched)
    df = pd.DataFrame(all_results)
    st.dataframe(df, use_container_width=True)
