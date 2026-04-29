"""Top-10 Songs, Top-10 Künstler und ein interaktiver Künstler-Vergleich."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import altair as alt
import streamlit as st

from utils import load_data, GOLD, BLUE, footer

st.set_page_config(page_title="Künstler & Streams", page_icon="📈", layout="wide")

df = load_data()


def split_streams_by_artist(df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode collaborative tracks so each featured artist gets a proportional
    share of the streams. Without this, artists who appear only as features
    are systematically under-counted.
    """
    df = df.copy()
    df["artist(s)_name"] = df["artist(s)_name"].astype(str)
    exploded = df["artist(s)_name"].str.split(",").explode().reset_index()
    exploded["artist(s)_name"] = exploded["artist(s)_name"].str.strip()
    exploded = exploded.merge(df[["streams"]], left_index=True, right_index=True)
    collaborators_per_track = exploded.groupby(level=0)["artist(s)_name"].transform("count")
    exploded["streams"] = exploded["streams"] / collaborators_per_track
    return exploded.reset_index(drop=True)


def top_songs_chart(df: pd.DataFrame) -> alt.Chart:
    top10 = df.sort_values("streams", ascending=False).head(10)[
        ["track_name", "streams", "artist(s)_name"]
    ]
    return (
        alt.Chart(top10.reset_index())
        .mark_bar()
        .encode(
            y=alt.Y("track_name:N", sort="-x", axis=alt.Axis(title="Songtitel", labelFontSize=12)),
            x=alt.X(
                "streams:Q",
                axis=alt.Axis(
                    title="Streams (Milliarden)", titleFontSize=20, labelFontSize=12,
                    format=".0s", tickCount=5, tickMinStep=1e9, labelExpr="datum.value / 1e9",
                ),
            ),
            color=alt.Color("streams:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=[
                alt.Tooltip("track_name", title="Songtitel"),
                alt.Tooltip("streams", title="Streams"),
                alt.Tooltip("artist(s)_name", title="Künstler"),
            ],
        )
        .properties(title={"text": "Top 10 Songs nach Streams 2023"}, width=600, height=400)
        .configure_title(fontSize=25, anchor="start", color=GOLD)
        .configure_axis(
            labelFontSize=12, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=7, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="middle", titleFontSize=20)
    )


def top_artists_chart(df: pd.DataFrame) -> alt.Chart:
    top10 = (
        df.groupby("artist(s)_name")["streams"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    return (
        alt.Chart(top10)
        .mark_bar()
        .encode(
            y=alt.Y("artist(s)_name:N", sort="-x", axis=alt.Axis(title="Künstler")),
            x=alt.X(
                "streams:Q",
                axis=alt.Axis(
                    title="Streams (Milliarden)", format=".0s",
                    tickCount=5, tickMinStep=1e9, labelExpr="datum.value / 1e9",
                ),
            ),
            color=alt.Color("streams:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=[
                alt.Tooltip("artist(s)_name", title="Künstler"),
                alt.Tooltip("streams", title="Streams"),
            ],
        )
        .properties(title={"text": "Top 10 Künstler nach Streams"}, width=600, height=400)
        .configure_title(fontSize=25, anchor="start", color=BLUE)
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="middle", titleFontSize=20)
    )


# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Spotify Top-Songs und Künstler 2023")
st.write(
    "Bevor wir tiefer in die Daten eindringen, verschaffen wir uns einen Überblick. "
    ":orange[**Welche Songs wurden am meisten gestreamt?**] "
    "Und :blue[**wer waren die Top-Künstler 2023?**]"
)
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(top_songs_chart(df), width="stretch")
with col2:
    st.altair_chart(top_artists_chart(df), width="stretch")

st.markdown("---")
st.subheader("Eigener Künstler-Vergleich")
st.write(
    "Wähle bis zu 12 Künstler aus, um deren Streams-Anteil zu vergleichen. "
    "Streams werden bei Kollaborationen proportional aufgeteilt. :point_down:"
)

df_split = split_streams_by_artist(df)
artist_list = sorted(df_split["artist(s)_name"].unique().tolist())
selected = st.multiselect("Künstler auswählen", artist_list)

if 1 <= len(selected) <= 12:
    filtered = (
        df_split[df_split["artist(s)_name"].isin(selected)]
        .groupby("artist(s)_name")["streams"]
        .sum()
        .reset_index()
    )
    donut = (
        alt.Chart(filtered)
        .mark_arc()
        .encode(
            theta=alt.Theta("streams:Q"),
            color=alt.Color("artist(s)_name:N", legend=alt.Legend(title="Künstler")),
            order=alt.Order("streams", sort="ascending"),
            tooltip=[
                alt.Tooltip("artist(s)_name", title="Künstler"),
                alt.Tooltip("streams", title="Streams"),
            ],
        )
        .properties(title="Streams-Vergleich", width=400, height=300)
        .configure_title(fontSize=25, anchor="start")
        .configure_legend(titleFontSize=16, labelFontSize=12)
        .configure_view(strokeWidth=0)
    )
    _, col_m, _ = st.columns(3)
    with col_m:
        st.altair_chart(donut, width="content")
elif len(selected) > 12:
    st.error("Bitte wähle maximal 12 Künstler aus.")

footer()