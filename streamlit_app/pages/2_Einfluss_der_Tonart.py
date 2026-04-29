"""Durchschnittliche Streams nach Tonart (Dur/Moll) und nach musikalischem Key."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import altair as alt
import streamlit as st

from utils import load_data, GOLD, BLUE, footer

st.set_page_config(page_title="Einfluss der Tonart", page_icon="📈", layout="wide")

df = load_data()


def mode_chart(df, selected_keys: list) -> alt.Chart:
    """Bar chart of average streams per mode (Major / Minor)."""
    key_label = "Key: " + ", ".join(selected_keys) if selected_keys else ""
    mode_df = df.groupby("mode")["streams"].mean().reset_index()
    return (
        alt.Chart(mode_df)
        .mark_bar(clip=True, size=50)
        .encode(
            x=alt.X("mode:N", axis=alt.Axis(title="Tonart", labelFontSize=14)),
            y=alt.Y(
                "streams:Q",
                scale=alt.Scale(domain=[250_000_000, 650_000_000]),
                axis=alt.Axis(
                    title="Ø Streams (Millionen)", titleFontSize=20, labelFontSize=14,
                    format=".0s", tickCount=6, tickMinStep=1e9, labelExpr="datum.value / 1e6",
                ),
            ),
            color=alt.Color("mode:N", legend=None, scale=alt.Scale(range=["#4ee2e6", "white"])),
            tooltip=[alt.Tooltip("mode", title="Tonart"), alt.Tooltip("streams", title="Ø Streams")],
        )
        .properties(
            title={"text": f"Ø Streams nach Tonart {key_label}", "dy": -20},
            width=550, height=400,
        )
        .configure_title(fontSize=25, anchor="start", color=GOLD)
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )


def key_chart(df, mode_label: str) -> alt.Chart:
    """Bar chart of average streams per musical key (C, C#, D, …)."""
    title_suffix = f"Tonart: {mode_label}" if mode_label != "Alle" else ""
    key_df = df.groupby("key")["streams"].mean().reset_index()
    return (
        alt.Chart(key_df)
        .mark_bar(clip=True, size=20)
        .encode(
            x=alt.X("key:N", axis=alt.Axis(title="Key", labelFontSize=14)),
            y=alt.Y(
                "streams:Q",
                scale=alt.Scale(domain=[250_000_000, 650_000_000]),
                axis=alt.Axis(
                    title="Ø Streams (Millionen)", titleFontSize=20, labelFontSize=14,
                    format=".0s", tickCount=6, tickMinStep=1e9, labelExpr="datum.value / 1e6",
                ),
            ),
            color=alt.Color("key:N", legend=None),
            tooltip=[alt.Tooltip("key", title="Key"), alt.Tooltip("streams", title="Ø Streams")],
        )
        .properties(
            title={"text": f"Ø Streams nach Key {title_suffix}", "dy": -20},
            width=550, height=400,
        )
        .configure_title(fontSize=25, anchor="start", color=BLUE)
        .configure_axis(
            labelFontSize=14, titleFontSize=20, titleColor="gray",
            labelColor="gray", titlePadding=12, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )


# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filtermöglichkeiten")
mode_options = df["mode"].unique().tolist() + ["Alle"]
selected_mode = st.sidebar.selectbox("Tonart", mode_options, index=mode_options.index("Alle"))
st.sidebar.markdown("---")
selected_keys = st.sidebar.multiselect("Key", df["key"].unique().tolist())

# Apply filters — four combinations handled via boolean logic
if selected_mode == "Alle" and not selected_keys:
    filtered = df
elif selected_mode == "Alle":
    filtered = df[df["key"].isin(selected_keys)]
elif not selected_keys:
    filtered = df[df["mode"] == selected_mode]
else:
    filtered = df[(df["mode"] == selected_mode) & (df["key"].isin(selected_keys))]

# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Einfluss der :orange[Tonart] und der :blue[Keys] auf die Streamingzahlen")
st.write(
    "Dur (*Major*) klingt hell und fröhlich, Moll (*Minor*) melancholischer. "
    "Hat das einen messbaren Einfluss auf den Erfolg eines Songs? "
    "Und welche Tonstufen (Keys) sind bei Hörerinnen und Hörern am beliebtesten?"
)
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(mode_chart(filtered, selected_keys), width="stretch")
with col2:
    st.altair_chart(key_chart(filtered, selected_mode), width="stretch")

# Dynamic top-5 ranking that reacts to the sidebar filters
_, col_m, _ = st.columns(3)
with col_m:
    mode_str = f":orange[***Tonart: {selected_mode}***]" if selected_mode != "Alle" else ""
    key_str = f":blue[***Key(s): {', '.join(selected_keys)}***]" if selected_keys else ""
    st.subheader(f"Top 5 Songs {mode_str} {key_str}")
    top5 = (
        filtered.sort_values("streams", ascending=False)
        .head(5)[["track_name", "artist(s)_name", "streams"]]
        .rename(columns={"track_name": "Titel", "artist(s)_name": "Künstler", "streams": "Streams"})
        .reset_index(drop=True)
    )
    st.table(top5)

footer()