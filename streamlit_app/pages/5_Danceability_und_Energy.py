"""Verteilung der Songs nach Energy- und Danceability-Bereichen (0–100 %)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import altair as alt
import streamlit as st

from utils import load_data, BLUE, GOLD, footer

st.set_page_config(page_title="Danceability & Energy", page_icon="📈")

df = load_data()


def distribution_chart(df: pd.DataFrame, feature: str) -> alt.Chart:
    """
    Bar + line chart showing how many songs fall into each 10-point bucket.
    Buckets of 10 are wide enough to smooth noise but tight enough to show the peak.
    """
    label = "Energy" if feature == "energy_%" else "Danceability"
    color = BLUE if feature == "energy_%" else GOLD
    col_name = f"{label.lower()}_range"

    grouped = (
        df.groupby(pd.cut(df[feature], range(0, 101, 10)))
        .size()
        .reset_index(name="song_count")
    )
    grouped.columns = [col_name, "song_count"]
    grouped[col_name] = grouped[col_name].apply(lambda x: f"{x.left}–{x.right}")

    bars = (
        alt.Chart(grouped)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(col_name, axis=alt.Axis(title=label, labelFontSize=14)),
            y=alt.Y("song_count:Q", axis=alt.Axis(title="Anzahl der Songs", titleFontSize=20, labelFontSize=14)),
            color=alt.Color(col_name, scale=alt.Scale(scheme="viridis"), legend=alt.Legend(title=label)),
            tooltip=[col_name, "song_count"],
        )
    )
    trend = (
        alt.Chart(grouped)
        .mark_line(interpolate="monotone", color="red")
        .encode(
            x=alt.X(col_name),
            y=alt.Y("song_count:Q"),
            tooltip=[col_name, "song_count"],
        )
    )
    return (
        alt.layer(bars, trend)
        .properties(
            title={"text": f"Anzahl der Songs nach {label}", "dy": 0},
            width=600, height=400,
        )
        .configure_title(fontSize=25, anchor="start", color=color)
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Merkmal wählen")
diagram = st.sidebar.radio(
    "Welches Merkmal möchtest du betrachten?", ("Energy", "Danceability"), index=0
)

# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Wie tanzbar und wie energetisch sollte ein Song sein?")
st.write(
    ":blue[Energy] spiegelt die Intensität und Aktivität eines Songs wider, "
    "während :orange[Danceability] beschreibt, wie gut sich ein Song zum Tanzen eignet."
)

if diagram == "Energy":
    st.altair_chart(distribution_chart(df, "energy_%"), width="stretch")
    st.write(":point_right: :blue[Die meisten Top-Songs haben einen Energy-Wert von 60–70 %.]")
else:
    st.altair_chart(distribution_chart(df, "danceability_%"), width="stretch")
    st.write(":point_right: :orange[Die meisten Top-Songs haben einen Danceability-Wert von 70–80 %.]")

footer()