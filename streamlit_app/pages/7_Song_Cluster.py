"""
Song-Cluster-Analyse — K-Means-Clustering auf Audio-Features.

Da der Datensatz ausschliesslich erfolgreiche Top-Songs enthaelt,
laesst sich nicht vorhersagen ob ein Song ein Hit wird. K-Means zeigt
stattdessen, welche Klang-Typen innerhalb der Top-Songs existieren.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils import load_data, footer

st.set_page_config(page_title="Song-Cluster-Analyse", page_icon=None, layout="wide")

FEATURES = [
    "danceability_%",
    "valence_%",
    "energy_%",
    "acousticness_%",
    "liveness_%",
    "speechiness_%",
]

LABELS = {
    "danceability_%": "Danceability",
    "valence_%":      "Valence",
    "energy_%":       "Energy",
    "acousticness_%": "Acousticness",
    "liveness_%":     "Liveness",
    "speechiness_%":  "Speechiness",
}

N_CLUSTERS = 4


@st.cache_resource
def fit_clusters():
    """
    Skaliert Audio-Features und trainiert K-Means (k=4).

    StandardScaler ist notwendig, da Features wie BPM (60-210) und
    Prozentwerte (0-100) sonst unterschiedlich stark ins Distanzmass
    einfliessen wuerden. Gibt (model, scaler, dataframe) zurueck.
    """
    df = load_data()
    X = df[FEATURES].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    df = df.copy()
    df["cluster"] = km.fit_predict(X_scaled)
    df["cluster_label"] = df["cluster"].apply(lambda c: f"Cluster {c + 1}")
    return km, scaler, df


km, scaler, df_c = fit_clusters()

cluster_labels = [f"Cluster {i + 1}" for i in range(N_CLUSTERS)]

# ── Heatmap-Daten ─────────────────────────────────────────────────────────────
profile = (
    df_c.groupby("cluster_label")[FEATURES]
    .mean()
    .reset_index()
    .melt(id_vars="cluster_label", var_name="feature", value_name="Wert")
)
profile["feature"] = profile["feature"].map(LABELS)

heatmap = (
    alt.Chart(profile)
    .mark_rect(stroke="white", strokeWidth=2)
    .encode(
        x=alt.X(
            "cluster_label:N",
            axis=alt.Axis(title=None, labelFontSize=13, labelAngle=0),
            sort=cluster_labels,
        ),
        y=alt.Y(
            "feature:N",
            sort=list(LABELS.values()),
            axis=alt.Axis(title=None, labelFontSize=13),
        ),
        color=alt.Color(
            "Wert:Q",
            scale=alt.Scale(scheme="greens", domain=[0, 80]),
            legend=alt.Legend(title="Wert (%)"),
        ),
        tooltip=[
            alt.Tooltip("cluster_label:N", title="Cluster"),
            alt.Tooltip("feature:N", title="Merkmal"),
            alt.Tooltip("Wert:Q", title="Durchschnitt (%)", format=".1f"),
        ],
    )
    .properties(width=400, height=280)
    .configure_view(stroke="lightgray", strokeWidth=1)
    .configure_axis(grid=False)
    .configure_legend(labelFontSize=12, titleFontSize=13)
)

# ── Sidebar: Sliders + Ergebnis ───────────────────────────────────────────────
st.sidebar.header("Eigenes Song-Profil eingeben")
st.sidebar.caption("Bewege die Regler und sieh, welchem Cluster dein Song angehoert.")
st.sidebar.markdown("---")

user_input = {}
for feat in FEATURES:
    user_input[feat] = st.sidebar.slider(
        LABELS[feat] + " (%)",
        0, 100,
        int(df_c[feat].median()),
    )

input_df = pd.DataFrame([user_input])[FEATURES]
input_scaled = scaler.transform(input_df)
pred_idx = int(km.predict(input_scaled)[0])
pred_label = f"Cluster {pred_idx + 1}"

st.sidebar.markdown("---")
st.sidebar.subheader("Ergebnis")
st.sidebar.metric("Dein Cluster", pred_label)

share = round(len(df_c[df_c["cluster"] == pred_idx]) / len(df_c) * 100, 1)
st.sidebar.caption(f"{share} % der Top-Songs gehoeren diesem Cluster an.")

nearest = (
    df_c[df_c["cluster"] == pred_idx]
    .sort_values("streams", ascending=False)
    .head(3)[["track_name", "artist(s)_name"]]
    .rename(columns={"track_name": "Aehnliche Songs", "artist(s)_name": "Kuenstler"})
    .reset_index(drop=True)
)
st.sidebar.dataframe(nearest, use_container_width=True, hide_index=True)

# ── Hauptbereich ──────────────────────────────────────────────────────────────
st.title("Song-Cluster-Analyse")
st.write(
    "K-Means teilt die Top-Songs in vier Klang-Typen ein. "
    "Die Heatmap zeigt das durchschnittliche Audio-Profil jedes Clusters "
    "— helle Felder bedeuten hohe Merkmalswerte."
)
st.caption(
    "Hinweis: Da alle Songs im Datensatz bereits Top-Hits sind, "
    "kann dieses Modell nicht vorhersagen ob ein Song erfolgreich wird. "
    "Es beschreibt nur Muster innerhalb der Erfolgs-Songs."
)

st.markdown("---")

col_heat, col_songs = st.columns([1, 1])

with col_heat:
    st.subheader("Audio-Profile der Cluster")
    st.altair_chart(heatmap)

    # Cluster-Groessen als kompakte Tabelle
    counts = (
        df_c.groupby("cluster_label")
        .size()
        .reset_index(name="Anzahl Songs")
        .rename(columns={"cluster_label": "Cluster"})
        .sort_values("Cluster")
    )
    st.dataframe(counts, use_container_width=True, hide_index=True)

with col_songs:
    st.subheader("Top-Songs je Cluster")
    selected = st.selectbox("Cluster auswaehlen", cluster_labels)
    top5 = (
        df_c[df_c["cluster_label"] == selected]
        .sort_values("streams", ascending=False)
        .head(5)[["track_name", "artist(s)_name", "streams"]]
        .rename(columns={
            "track_name":    "Titel",
            "artist(s)_name": "Kuenstler",
            "streams":       "Streams",
        })
        .reset_index(drop=True)
    )
    st.dataframe(top5, use_container_width=True, hide_index=True)

footer()