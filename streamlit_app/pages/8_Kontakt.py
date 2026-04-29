"""Kontaktseite mit Autor-Informationen."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils import footer

st.set_page_config(page_title="Kontakt", page_icon="📬")

st.title("Kontakt")
st.write(
    "Bei Fragen oder Anmerkungen zum Dashboard kannst du mich gerne kontaktieren."
)

st.markdown("""
**Autor:** Laurenz Brahner

**GitHub:** [github.com/laurenzbrahner](https://github.com/laurenzbrahner)

**E-Mail:** lb184@hdm-stuttgart.de
""")

footer()