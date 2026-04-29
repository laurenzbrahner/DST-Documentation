"""Dashboard landing page: project overview and key performance metrics."""
import os
import streamlit as st
from utils import load_data, footer

_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

st.set_page_config(
    page_title="Spotify Analyse Dashboard",
    page_icon="🎵",
    layout="wide",
)

df = load_data()

# ── Header ───────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(os.path.join(_ASSETS, "spotify_logo_black_new.png"), width=90)
with col_title:
    st.title("Spotify Top Songs 2023 — Analyse Dashboard")
    st.caption(
        "Was macht einen Song erfolgreich? "
        "Eine datengesteuerte Analyse von 953 Top-Songs auf Basis von Kaggle-Daten."
    )

st.markdown("---")

# ── KPI Metrics ──────────────────────────────────────────────────────────────
# These give recruiters/visitors an instant data summary without reading further.
total_songs = len(df)
total_streams_bn = df["streams"].sum() / 1e9
top_artist = df.groupby("artist(s)_name")["streams"].sum().idxmax()
avg_streams_m = df["streams"].mean() / 1e6

k1, k2, k3, k4 = st.columns(4)
k1.metric("Songs im Datensatz", f"{total_songs:,}")
k2.metric("Gesamte Streams", f"{total_streams_bn:.1f} Mrd.")
k3.metric("Meistgestreamter Künstler", top_artist)
k4.metric("Ø Streams pro Song", f"{avg_streams_m:.0f} Mio.")

st.markdown("---")

# ── Project Details ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    st.subheader("Über das Projekt")
    st.markdown("""
    - **Datenquelle:** [Kaggle – Top Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023)
    - **Ziel:** Welche Audio-Merkmale, Tonarten und Veröffentlichungszeitpunkte korrelieren mit hohen Stream-Zahlen?
    - **Stack:** Python · Pandas · Scikit-learn · Altair · Streamlit
    """)

with col2:
    st.subheader("Seitenübersicht")
    st.markdown("""
    | Seite | Inhalt |
    |---|---|
    | Künstler & Streams | Wer dominiert die Charts? |
    | Einfluss der Tonart | Dur vs. Moll & Keys |
    | Veröffentlichungsmonat | Wann ist der beste Release-Zeitpunkt? |
    | Audio-Merkmale | Speechiness, Liveness, Acousticness … |
    | Danceability & Energy | Tanzbarkeit und Intensität |
    | Herkunft der Künstler | Barplot der Herkunftsländer |
    | **Song-Cluster-Analyse** | **K-Means: Welcher Klang-Typ bist du?** |
    | Kontakt | Autor & Kontaktdaten |
    """)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Über den Autor")
st.sidebar.markdown("""
**Laurenz Brahner**

[GitHub](https://github.com/laurenzbrahner) · lb184@hdm-stuttgart.de
""")

footer()