
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
    background: linear-gradient(135deg, #F3E8FF 0%, #E8EAFE 50%, #FCE7F3 100%);
}
h1, h2, h3 {
    color: #5B3F8C !important;
    font-weight: 750 !important;
}
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid #D8C9F0;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(91, 63, 140, 0.08);
}
[data-testid="stMetricLabel"] {
    color: #75658F !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #5B3F8C !important;
    font-weight: 800 !important;
}
.stButton button, .stDownloadButton button {
    background: linear-gradient(90deg, #8B72C7, #B18AD9);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}
.stButton button:hover, .stDownloadButton button:hover {
    background: linear-gradient(90deg, #7559B5, #986CCB);
    color: white !important;
}
[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #DED3F0;
    border-radius: 12px;
    overflow: hidden;
}
hr {
    border-color: #D8C9F0;
}
[data-testid="stAlert"] {
    border-radius: 12px;
}
.stCaption {
    color: #76658E;
}
[data-testid="stSidebar"] {
    background: #F0E8FC;
}
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
    df["date_added"] = pd.to_datetime(
        df["date_added"], errors="coerce"
    )

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
    st.dataframe(
        raw_df.head(10),
        width="stretch",
        hide_index=True
    )

with right:
    st.write("**Cleaned Dataset**")
    st.dataframe(
        df.head(10),
        width="stretch",
        hide_index=True
    )

st.markdown("---")
st.subheader("🔍 Data Quality Analysis")

missing_summary = pd.DataFrame({
    "Column": raw_df.columns,
    "Missing Values": raw_df.isna().sum().values,
    "Missing Percentage": (
        raw_df.isna().mean().values * 100
    ).round(2)
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
            color_continuous_scale=[
                "#E8EAFE",
                "#B9A7E8",
                "#8B72C7"
            ],
            title="Missing Values Before Cleaning"
        )

        missing_chart.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        missing_chart.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            font=dict(color="#66508F"),
            title_font=dict(color="#5B3F8C"),
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(
                rangemode="tozero",
                title="Number of Missing Values"
            ),
            margin=dict(l=10, r=20, t=55, b=10)
        )

        st.plotly_chart(
            missing_chart,
            width="stretch",
            key="task1_missing_chart"
        )

with right:
    st.write("**Cleaning Summary**")
    st.dataframe(
        duplicate_summary,
        width="stretch",
        hide_index=True
    )

st.markdown("---")
st.subheader("🎬 Content Type Distribution")

if "type" in df.columns:
    type_summary = (
        df["type"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("Content Type")
        .reset_index(name="Titles")
    )

    content_chart = px.pie(
        type_summary,
        names="Content Type",
        values="Titles",
        hole=0.48,
        color="Content Type",
        color_discrete_map={
            "Movie": "#8B72C7",
            "TV Show": "#E7A8D8",
            "Unknown": "#B8C4F0"
        },
        title="Movies and TV Shows"
    )

    content_chart.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(
            line=dict(color="#FFFFFF", width=3)
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Titles: %{value:,}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    content_chart.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#66508F"),
        title_font=dict(color="#5B3F8C"),
        legend=dict(font=dict(color="#66508F")),
        margin=dict(l=15, r=15, t=60, b=15)
    )

    st.plotly_chart(
        content_chart,
        width="stretch",
        key="task1_content_type_chart"
    )

st.markdown("---")
st.subheader("📥 Download Cleaned Data")

left, right = st.columns(2)

with left:
    st.download_button(
        "📄 Download Cleaned Dataset CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="netflix_cleaned.csv",
        mime="text/csv",
        key="task1_download_cleaned",
        use_container_width=True
    )

with right:
    st.download_button(
        "📊 Download Data Quality Report CSV",
        data=missing_summary.to_csv(index=False).encode("utf-8"),
        file_name="netflix_data_quality_report.csv",
        mime="text/csv",
        key="task1_download_report",
        use_container_width=True
    )

st.markdown("---")
st.caption("Netflix Data Cleaning | Python • Pandas • Plotly • Streamlit")



