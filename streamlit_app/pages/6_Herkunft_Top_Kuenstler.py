"""Herkunftsländer der Top-Künstler als interaktiver Barplot."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import altair as alt
import streamlit as st

from utils import load_data, GOLD, footer

st.set_page_config(
    page_title="Herkunft der Top-Künstler",
    page_icon="🌍",
    layout="wide",
)

df = load_data()

# Städte- und Regionseinträge auf Länderebene normalisieren
CITY_TO_COUNTRY = {
    "England": "United Kingdom", "Scotland": "United Kingdom",
    "Manchester": "United Kingdom", "Ipswich": "United Kingdom",
    "Buenos Aires": "Argentina",
    "Guadalajara": "Mexico",
    "Nashville": "United States", "Downingtown": "United States",
    "McAllen": "United States", "Monroe": "United States",
    "Torrance": "United States", "Los Angeles": "United States",
    "Providence": "United States", "Orlando": "United States",
    "New York": "United States", "Austin": "United States",
    "Boston": "United States", "Philadelphia": "United States",
    "United States of America": "United States",
    "Cabreúva": "Brazil", "Goiás": "Brazil", "Mato Grosso do Sul": "Brazil",
    "Amazonas": "Brazil", "Rio de Janeiro": "Brazil",
    "Helsinki": "Finland",
    "Berlin": "Germany",
    "Las Palmas de Gran Canaria": "Spain",
    "Türkiye": "Turkey",
    "Punjab": "India", "Gujarat": "India",
    "Sundsvall": "Sweden",
    "Oshawa": "Canada",
}

df["artist_country"] = df["artist_country"].replace(CITY_TO_COUNTRY)

# Robuste Aggregation: funktioniert unabhängig von pandas-Version
vc = df["artist_country"].value_counts()
country_counts = vc.rename_axis("Land").reset_index(name="Anzahl Songs")


def country_chart(data, top_n: int) -> alt.Chart:
    """Horizontaler Barplot der top_n Länder nach Anzahl der Songs."""
    return (
        alt.Chart(data.head(top_n))
        .mark_bar()
        .encode(
            x=alt.X("Anzahl Songs:Q", axis=alt.Axis(title="Anzahl Songs", labelFontSize=13)),
            y=alt.Y("Land:N", sort="-x", axis=alt.Axis(title="", labelFontSize=13)),
            color=alt.Color("Anzahl Songs:Q", scale=alt.Scale(scheme="blues"), legend=None),
            tooltip=["Land", "Anzahl Songs"],
        )
        .properties(
            title={"text": f"Top {top_n} Herkunftsländer der Top-Songs", "dy": -10},
            width=700,
            height=max(top_n * 28, 200),
        )
        .configure_title(fontSize=22, anchor="start", color=GOLD)
        .configure_axis(
            labelFontSize=13, titleFontSize=16,
            titleColor="gray", labelColor="gray", titlePadding=10, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False)
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Einstellungen")
top_n = st.sidebar.slider("Anzahl Länder anzeigen", min_value=5, max_value=30, value=15)

# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Aus welchem Land kommen die Top-Songs?")
st.write(
    "Aus welchen Ländern stammen die meisten Songs der Spotify Top-Charts 2023? "
    "Die USA dominieren — aber wie weit dahinter kommen andere Länder?"
)

st.markdown("---")

total_countries = country_counts["Land"].nunique()
top_country = country_counts.iloc[0]["Land"]
top_country_count = int(country_counts.iloc[0]["Anzahl Songs"])
us_share = round(top_country_count / len(df) * 100, 1)

k1, k2, k3 = st.columns(3)
k1.metric("Vertretene Länder", total_countries)
k2.metric("Dominantes Land", top_country)
k3.metric(f"Anteil {top_country}", f"{us_share} %")

st.markdown("---")

col_chart, col_table = st.columns([2, 1])

with col_chart:
    st.altair_chart(country_chart(country_counts, top_n), width="stretch")

with col_table:
    st.subheader("Rangliste")
    st.dataframe(
        country_counts.head(top_n).reset_index(drop=True),
        use_container_width=True,
        height=min(top_n * 35 + 40, 600),
    )

footer()