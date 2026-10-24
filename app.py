
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Netflix Data Cleaning", page_icon="🧹", layout="wide")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #f1f5ff, #e8edff, #fafaff);}
h1, h2, h3 {color: #40558c;}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.9);
    border: 1px solid #d7def5;
    padding: 18px;
    border-radius: 16px;
}
.stButton button, .stDownloadButton button {border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

data_path = Path(__file__).parent / "Dataset.csv"

try:
    raw_df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error("Dataset.csv was not found. Place it in the same folder as app.py.")
    st.stop()

df = raw_df.copy()
original_rows = len(raw_df)
original_columns = len(raw_df.columns)
original_missing = int(raw_df.isna().sum().sum())
original_duplicates = int(raw_df.duplicated().sum())

for column in df.select_dtypes(include=["object", "str"]).columns:
    df[column] = df[column].apply(
        lambda value: value.strip() if isinstance(value, str) else value
    )
    df[column] = df[column].replace("", pd.NA)

df = df.drop_duplicates().copy()

if "show_id" in df.columns:
    df["show_id"] = df["show_id"].astype("string").str.strip()

if "date_added" in df.columns:
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

if "release_year" in df.columns:
    df["release_year"] = pd.to_numeric(
        df["release_year"], errors="coerce"
    ).astype("Int64")

cleaned_rows = len(df)
cleaned_missing = int(df.isna().sum().sum())
removed_duplicates = original_rows - cleaned_rows

st.title("🧹 Netflix Data Cleaning Dashboard")
st.caption("Auspify Technologies | Data Analysis Using Python")
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Original Rows", f"{original_rows:,}")
c2.metric("Cleaned Rows", f"{cleaned_rows:,}")
c3.metric("Duplicates Removed", f"{removed_duplicates:,}")
c4.metric("Missing Values After Cleaning", f"{cleaned_missing:,}")

st.markdown("---")
st.subheader("📋 Dataset Overview")

left, right = st.columns(2)

with left:
    st.write("**Original Dataset**")
    st.dataframe(raw_df.head(10), width="stretch", hide_index=True)

with right:
    st.write("**Cleaned Dataset**")
    st.dataframe(df.head(10), width="stretch", hide_index=True)

st.markdown("---")
st.subheader("🔍 Data Quality Analysis")

missing_summary = pd.DataFrame({
    "Column": raw_df.columns,
    "Missing Values": raw_df.isna().sum().values,
    "Missing Percentage": (raw_df.isna().mean().values * 100).round(2)
}).sort_values("Missing Values", ascending=False)

duplicate_summary = pd.DataFrame({
    "Metric": [
        "Original rows",
        "Original columns",
        "Original missing values",
        "Original duplicate rows",
        "Rows after cleaning",
        "Missing values after cleaning"
    ],
    "Value": [
        original_rows,
        original_columns,
        original_missing,
        original_duplicates,
        cleaned_rows,
        cleaned_missing
    ]
})

left, right = st.columns(2)

with left:
    st.write("**Missing Values by Column**")
    if missing_summary["Missing Values"].sum() == 0:
        st.success("No missing values found in the original dataset.")
        st.info("All columns contain complete values. There are no bars to display.")
    else:
        missing_chart = px.bar(
            missing_summary,
            x="Column",
            y="Missing Values",
            text="Missing Values",
            color="Missing Values",
            color_continuous_scale=["#dce5ff", "#8399df", "#40558c"],
            title="Missing Values Before Cleaning"
        )
        missing_chart.update_traces(textposition="outside", cliponaxis=False)
        missing_chart.update_layout(
            template="plotly_white",
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(rangemode="tozero", title="Number of Missing Values"),
            margin=dict(l=10, r=20, t=55, b=10)
        )
        st.plotly_chart(missing_chart, width="stretch", key="task1_missing_chart")

with right:
    st.write("**Cleaning Summary**")
    st.dataframe(duplicate_summary, width="stretch", hide_index=True)

st.markdown("---")
st.subheader("🎬 Content Type Distribution")

if "type" in df.columns:
    type_summary = (
        df["type"].fillna("Unknown").value_counts()
        .rename_axis("Content Type").reset_index(name="Titles")
    )
    content_chart = px.pie(
        type_summary,
        names="Content Type",
        values="Titles",
        hole=0.45,
        color="Content Type",
        color_discrete_map={
            "Movie": "#8ca3e8",
            "TV Show": "#c2a8e8",
            "Unknown": "#d9d9e8"
        },
        title="Movies and TV Shows"
    )
    content_chart.update_layout(template="plotly_white")
    st.plotly_chart(content_chart, width="stretch", key="task1_content_type_chart")

st.markdown("---")
st.subheader("📥 Download Cleaned Data")

st.download_button(
    "Download Cleaned Dataset CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="netflix_cleaned.csv",
    mime="text/csv",
    key="task1_download_cleaned"
)

st.download_button(
    "Download Data Quality Report CSV",
    data=missing_summary.to_csv(index=False).encode("utf-8"),
    file_name="netflix_data_quality_report.csv",
    mime="text/csv",
    key="task1_download_report"
)

st.markdown("---")
st.caption("Netflix Data Cleaning | Python • Pandas • Plotly • Streamlit")

