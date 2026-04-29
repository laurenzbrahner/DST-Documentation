"""Anzahl der Top-Song-Veröffentlichungen pro Monat mit animierter Demo."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import pandas as pd
import altair as alt
import streamlit as st

from utils import load_data, footer

st.set_page_config(page_title="Veröffentlichungsmonat", page_icon="📅")

df = load_data()

MONTH_LABELS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

monthly = df.groupby("released_month").size().reset_index(name="count")
monthly["released_month"] = monthly["released_month"].map(MONTH_LABELS)


def line_chart(df: pd.DataFrame) -> alt.Chart:
    """Liniendiagramm der monatlichen Veröffentlichungen."""
    return (
        alt.Chart(df)
        .mark_line(strokeWidth=3)
        .encode(
            x=alt.X(
                "released_month:N",
                sort=list(MONTH_LABELS.values()),
                axis=alt.Axis(title="Monat", labelFontSize=14),
            ),
            y=alt.Y(
                "count:Q",
                scale=alt.Scale(domain=(30, 120)),
                axis=alt.Axis(
                    title="Veröffentlichungen", titleFontSize=20, labelFontSize=14
                ),
            ),
            tooltip=["released_month", "count"],
        )
        .properties(
            title={"text": "Top-Song-Veröffentlichungen nach Monat", "dy": -20},
            width=600, height=400,
        )
        .configure_title(fontSize=25, anchor="start")
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )


# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Einfluss des Veröffentlichungsmonats")
st.write(
    "Wann ist der beste Zeitpunkt, einen Song zu veröffentlichen? "
    "Wir schauen uns an, in welchen Monaten die meisten Top-Songs erschienen sind."
)

# Session state keeps animation/detail flags alive across widget interactions
if "run_animation" not in st.session_state:
    st.session_state["run_animation"] = False
if "show_details" not in st.session_state:
    st.session_state["show_details"] = False

col1, _, col3 = st.columns(3)
with col1:
    if st.button("Diagrammdemo starten"):
        st.session_state["run_animation"] = True
with col3:
    if st.button("Mehr Details anzeigen"):
        st.session_state["show_details"] = True

chart_slot = st.empty()

# Animate by revealing one month at a time
if st.session_state["run_animation"]:
    for i in range(1, 13):
        chart_slot.altair_chart(line_chart(monthly.iloc[:i]), width="stretch")
        time.sleep(0.25)
    st.session_state["run_animation"] = False

# Show annotated chart with min/max markers
if st.session_state["show_details"]:
    base = (
        alt.Chart(monthly)
        .mark_line(strokeWidth=3)
        .encode(
            x=alt.X("released_month:N", sort=list(MONTH_LABELS.values()),
                    axis=alt.Axis(title="Monat", labelFontSize=14)),
            y=alt.Y("count:Q", scale=alt.Scale(domain=(30, 120)),
                    axis=alt.Axis(title="Veröffentlichungen", titleFontSize=20, labelFontSize=14)),
            tooltip=["released_month", "count"],
        )
    )
    max_val = monthly["count"].max()
    min_val = monthly["count"].min()

    max_points = alt.Chart(monthly[monthly["count"] == max_val]).mark_point(
        size=100, color="green", opacity=0.8, filled=True
    ).encode(
        x=alt.X("released_month:N", sort=list(MONTH_LABELS.values())),
        y="count:Q",
    )
    min_points = alt.Chart(monthly[monthly["count"] == min_val]).mark_point(
        size=100, color="red", opacity=0.8, filled=True
    ).encode(
        x=alt.X("released_month:N", sort=list(MONTH_LABELS.values())),
        y="count:Q",
    )

    annotated = (
        alt.layer(base, max_points, min_points)
        .properties(
            title={"text": "Top-Song-Veröffentlichungen nach Monat", "dy": -20},
            width=550, height=400,
        )
        .configure_title(fontSize=25, anchor="start")
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )
    chart_slot.altair_chart(annotated, width="stretch")
    st.write(":point_right: :green[Die meisten Top-Songs werden im Januar und im Mai released.]")
    st.write(":point_right: :red[Die wenigsten Top-Songs werden im August released.]")

footer()