import streamlit as st
from googlesearch import search

st.set_page_config(page_title="Radar Immo - Facebook", layout="centered")
st.title("📡 Radar Immo : Annonces Facebook")

keywords = [
    "site:facebook.com vend maison Chaudfontaine",
    "site:facebook.com vend maison Embourg",
    "site:facebook.com vend maison Beaufays"
]

results = []

for query in keywords:
    st.subheader(f"🔍 Résultats pour : {query}")
    count = 0
    for url in search(query, num_results=10):
        # On filtre un peu les liens (on peut affiner)
        if any(x in url for x in ["facebook.com", "groups", "marketplace", "posts"]):
            st.markdown(f"- [Lien]({url})")
            count += 1
    if count == 0:
        st.write("❌ Aucun résultat trouvé récemment.")
