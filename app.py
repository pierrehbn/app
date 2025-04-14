import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Radar Immo - Facebook", layout="centered")
st.title("📡 Radar Immo : Annonces Facebook enrichies")

keywords = [
    "site:facebook.com vend maison Chaudfontaine",
    "site:facebook.com vend maison Embourg",
    "site:facebook.com vend maison Beaufays"
]

def enrich_facebook_post(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=5)
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
            "title": "Erreur de chargement",
            "description": str(e),
            "image": None
        }

for query in keywords:
    st.subheader(f"🔍 Résultats pour : {query}")
    for url in search(query, num_results=5):
        if "facebook.com" in url:
            data = enrich_facebook_post(url)
            st.markdown(f"### 🔗 [{data['title']}]({data['url']})")
            st.write(data['description'])
            if data['image']:
                st.image(data['image'], use_column_width=True)
            st.markdown("---")
