import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Netflix Data Cleaning",
    page_icon="🧹",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #F0E8FF, #FAF7FF, #E9EFFF);
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DCCBFA;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 12px #7956A815;
}
h1, h2, h3 {
    color: #65458C !important;
}
.stButton > button, .stDownloadButton > button {
    background: #7956A8;
    color: white;
    border-radius: 10px;
    border: none;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #65458C;
    color: white;
}
</style>
""", unsafe_allow_html=True)

folder = Path(__file__).parent
source = folder / "Dataset.csv"
output = folder / "netflix_cleaned.csv"

st.title("🧹 Netflix Data Cleaning & Preparation")
st.caption("Auspify Technologies | Data Analysis Using Python")

df = pd.read_csv(source)
cleaned = df.drop_duplicates().copy()

text_columns = [
    "type", "title", "director", "country",
    "rating", "duration", "listed_in"
]

for col in text_columns:
    if col in cleaned.columns:
        cleaned[col] = cleaned[col].astype("string").str.strip()

if "date_added" in cleaned.columns:
    cleaned["date_added"] = pd.to_datetime(
        cleaned["date_added"], errors="coerce"
    )

# Save cleaned dataset
cleaned.to_csv(output, index=False)

# Key metrics
total_before = len(df)
total_after = len(cleaned)
duplicates = int(df.duplicated().sum())
missing_before = int(df.isna().sum().sum())
missing_after = int(cleaned.isna().sum().sum())

a, b, c, d = st.columns(4)
a.metric("Original Rows", f"{total_before:,}")
b.metric("Cleaned Rows", f"{total_after:,}")
c.metric("Duplicate Rows Removed", f"{duplicates:,}")
d.metric("Missing Values", f"{missing_after:,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Data Quality Before Cleaning")
    before = df.isna().sum().reset_index()
    before.columns = ["Column", "Missing Values"]
    st.plotly_chart(
        px.bar(before, x="Column", y="Missing Values",
               title="Missing Values by Column"),
        use_container_width=True
    )

with right:
    st.subheader("Content Type Overview")
    types = cleaned["type"].value_counts().reset_index()
    types.columns = ["Content Type", "Titles"]
    st.plotly_chart(
        px.pie(types, names="Content Type", values="Titles",
               title="Movies vs TV Shows", hole=0.4),
        use_container_width=True
    )

st.subheader("Cleaning Summary")
summary = pd.DataFrame({
    "Metric": [
        "Rows before cleaning",
        "Rows after removing duplicates",
        "Duplicate rows removed",
        "Missing cells before cleaning",
        "Missing cells after cleaning"
    ],
    "Value": [
        total_before, total_after, duplicates,
        missing_before, missing_after
    ]
})
st.dataframe(summary, use_container_width=True)

st.subheader("Preview Cleaned Dataset")
st.dataframe(cleaned.head(100), use_container_width=True)

st.download_button(
    "Download Cleaned Dataset",
    cleaned.to_csv(index=False).encode("utf-8"),
    "netflix_cleaned.csv",
    "text/csv"
)

st.success("Cleaning completed. The cleaned CSV has been saved.")
