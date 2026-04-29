"""Shared utilities for the Spotify dashboard: data loading and common helpers."""
import os
import pandas as pd
import streamlit as st

# Absolute path so the app works regardless of the working directory when started
_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "processed", "spotify_angereichert_cleaned.csv"
)

# Colour palette used consistently across all pages
SPOTIFY_GREEN = "#1DB954"
GOLD = "#ffbd45"
BLUE = "#60b4ff"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Read the cleaned Spotify CSV. Cached so the file is only read once per session."""
    df = pd.read_csv(_DATA_PATH)
    # Remove the unnamed index column that Pandas writes when saving with df.to_csv()
    df.drop(columns=["Unnamed: 0"], inplace=True, errors="ignore")
    return df


def footer():
    """Render a consistent footer on every page."""
    st.markdown("---")
    st.caption("© 2023 Laurenz Brahner — [GitHub](https://github.com/laurenzbrahner)")