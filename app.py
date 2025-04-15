import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Radar Immo", layout="wide")

sources = [
    "immoweb.be",
    "immovlan.be",
    "zimmo.be"
]

zones = ["Embourg", "Beaufays", "Chaudfontaine", "Tilff"]
filtrants_exclus = ["search", "recherche", "listing", "results", "map", "list"]

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
        return [r["link"] for r in results if "link" in r and not any(x in r["link"] for x in filtrants_exclus)]
    except Exception as e:
        st.error(f"Erreur SerpApi : {e}")
        return []

def enrich(url, zone):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("meta", property="og:title")
        author = soup.find("meta", property="og:site_name") or soup.find("meta", attrs={"name": "author"})
        nom = author["content"] if author else "Inconnu"

        return {
            "Agence / Nom": nom,
            "Lien": f"[lien]({url})",
            "Localité": zone
        }

    except Exception as e:
        return {
            "Agence / Nom": "Erreur",
            "Lien": f"[lien]({url})",
            "Localité": zone
        }

if st.button("🔍 Lancer la recherche"):
    progress_text = "Recherche des annonces en cours..."
    my_bar = st.progress(0, text=progress_text)

    all_results = []
    total = len(zones) * len(sources)
    step = 1

    for zone in zones:
        for source in sources:
            query = f"site:{source} maison à vendre {zone}"
            urls = search_serpapi(query, num=6)
            for url in urls:
                enriched = enrich(url, zone)
                all_results.append(enriched)
            progress_percent = step / total
            my_bar.progress(progress_percent, text=f"{step}/{total} requêtes traitées")
            step += 1

    my_bar.empty()
    df = pd.DataFrame(all_results)
    st.dataframe(df, use_container_width=True)
