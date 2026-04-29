"""Scatter plots with regression lines for six audio features vs. stream count."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from sklearn.linear_model import LinearRegression

from utils import load_data, footer

st.set_page_config(
    page_title="Audio-Merkmale", page_icon="📈", layout="wide"
)

df = load_data()

# Features shown on this page: internal column name → (display label, title colour)
FEATURES = {
    "speechiness_%":      ("Speechiness",     "blue"),
    "liveness_%":         ("Liveness",         "orange"),
    "instrumentalness_%": ("Instrumentalness", "green"),
    "acousticness_%":     ("Acousticness",     "gray"),
    "danceability_%":     ("Danceability",     "#ffbd45"),
    "energy_%":           ("Energy",           "#60b4ff"),
}


def make_chart(merkmal: str, y_axis: str, display_mode: str) -> alt.Chart:
    """Build a scatter / regression-line chart for one audio feature."""
    label, color = FEATURES[merkmal]

    if y_axis == "Streams":
        agg_df = df.groupby(merkmal).agg({"streams": "mean"}).reset_index()
        y_col = "streams"
        y_scale = alt.Scale(domain=[0, 1_500_000_000])
        y_format = alt.Axis(
            title="Streams (Milliarden)", titleFontSize=16, labelFontSize=14,
            format=".0s", tickCount=5, tickMinStep=1e9,
            labelExpr="datum.value / 1e9",
        )
    else:
        agg_df = df.groupby(merkmal).size().reset_index(name="song_count")
        y_col = "song_count"
        y_max = agg_df["song_count"].max()
        y_scale = alt.Scale(domain=[0, y_max])
        y_format = alt.Axis(
            title="Anzahl der Songs", titleFontSize=16, labelFontSize=14, tickCount=5
        )

    # Fit a simple OLS line to show the trend direction
    X = agg_df[merkmal].values.reshape(-1, 1)
    y = agg_df[y_col].values
    reg = LinearRegression().fit(X, y)
    reg_df = pd.DataFrame(
        {merkmal: np.linspace(df[merkmal].min(), df[merkmal].max(), 100)}
    )
    # .values removes column names so sklearn doesn't warn about feature-name mismatch
    reg_df["predicted"] = reg.predict(reg_df[[merkmal]].values)
    if y_axis == "Anzahl der Songs":
        reg_df["predicted"] = reg_df["predicted"].clip(lower=0)

    x_enc = alt.X(merkmal, axis=alt.Axis(title=label, labelFontSize=14))

    scatter = (
        alt.Chart(agg_df)
        .mark_circle(size=60, opacity=0.7)
        .encode(
            x=x_enc,
            y=alt.Y(y_col, scale=y_scale, axis=y_format),
            color=alt.Color(y_col, scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=[merkmal, y_col],
        )
    )
    line = (
        alt.Chart(reg_df)
        .mark_line(color="red")
        .encode(x=x_enc, y=alt.Y("predicted:Q", scale=y_scale))
    )

    # Compose layers according to user selection — avoids repeating this logic for every feature
    layers = {
        "Beides":            alt.layer(scatter, line),
        "Regressions Linie": line,
        "Scatter Points":    scatter,
    }
    return (
        layers[display_mode]
        .properties(title={"text": label, "dy": -20}, width=475, height=400)
        .configure_title(fontSize=25, anchor="start", color=color)
        .configure_axis(
            labelFontSize=14, titleFontSize=20,
            titleColor="gray", labelColor="gray", titlePadding=12, grid=False,
        )
        .configure_view(strokeWidth=0)
        .configure_axisX(labelAngle=0, titleAnchor="start")
        .configure_axisY(grid=False, titleAnchor="end", titleFontSize=20)
    )


# ── Sidebar controls ──────────────────────────────────────────────────────────
display_mode = st.sidebar.radio(
    "Darstellung", ("Beides", "Regressions Linie", "Scatter Points"), index=0
)
y_axis = st.sidebar.radio("Y-Achse", ("Streams", "Anzahl der Songs"), index=0)

# ── Page ──────────────────────────────────────────────────────────────────────
st.title("Einfluss von Audio-Merkmalen auf die Songpopularität")
st.write(
    "Wie stark beeinflussen :blue[Speechiness], :orange[Liveness], "
    ":green[Instrumentalness], :gray[Acousticness], "
    ":orange[**Danceability**] und :blue[**Energy**] "
    "die Streamingzahlen? Die rote Regressionslinie zeigt die Trendrichtung."
)

# Render all six features in a 2-column grid — one loop replaces 300 lines of if/elif blocks
feature_keys = list(FEATURES.keys())
for row_start in range(0, len(feature_keys), 2):
    col1, col2 = st.columns(2)
    for col, feat in zip([col1, col2], feature_keys[row_start: row_start + 2]):
        with col:
            st.altair_chart(make_chart(feat, y_axis, display_mode), width="stretch")
    st.markdown("---")

footer()