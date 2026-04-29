# Spotify Top Songs 2023 — Datenanalyse

Analyse der meistgestreamten Spotify-Songs des Jahres 2023. Das Projekt untersucht, welche Audio-Merkmale, Veroeffentlichungszeitpunkte und Kuenstler-Herkuenfte mit hohen Streamingzahlen korrelieren. K-Means-Clustering identifiziert ausserdem vier unterschiedliche Klang-Typen innerhalb der Top-Charts.

**Live-Dashboard:** [laurenzbrahner.github.io/DST-Documentation](https://laurenzbrahner.github.io/DST-Documentation/)

---

## Projektstruktur

```
DST-Documentation/
├── data/
│   ├── raw/                        Originaldatensatz von Kaggle (953 Songs)
│   └── processed/                  Bereinigter und angereicherter Datensatz
├── notebooks/
│   ├── 01_data_preparation.ipynb   Bereinigung, Typkonvertierung, fehlende Werte
│   ├── 02_data_exploration.ipynb   Explorative Datenanalyse und Visualisierungen
│   ├── 03_data_enrichment.ipynb    Anreicherung mit Kuenstler-Herkunftsdaten
│   └── 04_visuals.ipynb            Diagramme fuer die Praesentation
├── streamlit_app/
│   ├── main.py                     Einstiegspunkt des Dashboards
│   ├── utils.py                    Gemeinsames Datenladen und Hilfsfunktionen
│   ├── assets/                     Logo-Bilder
│   └── pages/
│       ├── 1_Kuenstler_und_Streams.py
│       ├── 2_Einfluss_der_Tonart.py
│       ├── 3_Veroeffentlichungsmonat.py
│       ├── 4_Audio_Merkmale.py
│       ├── 5_Danceability_und_Energy.py
│       ├── 6_Herkunft_Top_Kuenstler.py
│       ├── 7_Song_Cluster.py       K-Means-Clustering der Top-Songs
│       └── 8_Kontakt.py
├── docs/                           Quarto-Dokumentationsquellen
├── requirements.txt
└── README.md
```

---

## Installation und Start

```bash
pip install -r requirements.txt
cd streamlit_app
streamlit run main.py
```

---

## Wichtigste Erkenntnisse

- Songs in **Dur (Major)** erzielen im Durchschnitt 12 % mehr Streams als Moll-Songs
- **Januar und Mai** sind die Spitzenmonate fuer Veroeffentlichungen in den Top-Charts; August ist der schwaechtse Monat
- **BPM** ist das wichtigste Audio-Merkmal unter den Top-Songs — Audio-Merkmale allein erklaeren jedoch weniger als 20 % der Stream-Varianz, was zeigt dass Reichweite und Playlist-Platzierung den Erfolg staerker bestimmen als der Klang
- K-Means identifiziert vier Klang-Cluster in den Top-Charts: energetische Dance-Tracks, akustische Songs, entspannte Mitteltempo-Songs und vokalstarke Tracks

---

## Technologie-Stack

| Bereich | Werkzeuge |
|---|---|
| Datenaufbereitung | Python, Pandas |
| Machine Learning | Scikit-learn (K-Means, StandardScaler) |
| Visualisierung | Altair |
| Dashboard | Streamlit |
| Datenquelle | [Kaggle — Top Spotify Songs 2023](https://www.kaggle.com/datasets/nelgiriyewithana/top-spotify-songs-2023) |

---

## Autor

Laurenz Brahner — lb184@hdm-stuttgart.de — [github.com/laurenzbrahner](https://github.com/laurenzbrahner)