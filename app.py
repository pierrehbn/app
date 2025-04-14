import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Radar Immo - Liège", layout="centered")
st.title("🏠 Radar Immo : Embourg · Beaufays · Chaudfontaine")

# Sites ciblés
sources = [
    "site:immoweb.be",
    "site:immovlan.be",
    "site:zimmo.be",
    "site:logic-immo.be",
    "site:trevi.be",
    "site:weinvest.be",
    "site:immoscoop.be",
    "site:immomine.be",
    "site:century21.be",
    "site:era.be"
]

# Localités ciblées
zones = ["Embourg", "Beaufays", "Chaudfontaine"]

def enrich(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find("meta", property="og:title")
        description = soup.find("meta", property="og:description")
        image = soup.find("meta", property="og:image")

        return {
            "url": url,
            "title": title["content"] if title else "Sans titre",
            "description": description["content"] if description else "Pas de description trouvée.",
            "image": image["content"] if image else None
        }
    except Exception as e:
        return {
            "url": url,
            "title": "Erreur",
            "description": str(e),
            "image": None
        }

# Lancement de la recherche
for zone in zones:
    st.subheader(f"📍 Annonces récentes à {zone}")
    for source in sources:
        query = f"{source} maison à vendre {zone}"
        for url in search(query, num_results=5):
            if any(s in url for s in ["immoweb", "immovlan", "zimmo", "trevi", "era", "weinvest", "logic-immo"]):
                data = enrich(url)
                st.markdown(f"### 🔗 [{data['title']}]({data['url']})")
                st.write(data['description'])
                if data['image']:
                    st.image(data['image'], use_column_width=True)
                st.markdown("---")
