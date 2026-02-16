import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ===============================
#   CONFIGURASI DASHBOARD
# ===============================
st.set_page_config(
    page_title="Dashboard Kuesioner",
    page_icon="📊",
    layout="wide"
)

px.defaults.template = "plotly_white"

st.title("📊 Dashboard Visualisasi Data Kuesioner")

# ===============================
#   LOAD DATA
# ===============================
uploaded_data = "data_kuesioner.xlsx"

if not os.path.exists(uploaded_data):
    st.error("File 'data_kuesioner.xlsx' tidak ditemukan.")
    st.stop()

try:
    df = pd.read_excel(uploaded_data)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

question_cols = [col for col in df.columns if col.startswith("Q")]

if not question_cols:
    st.error("Tidak ditemukan kolom pertanyaan (awalan 'Q').")
    st.stop()

# Urutan skala konsisten
skala_order = ["SS", "S", "CS", "N", "TS", "STS"]

# ===============================
#   MAPPING NILAI NUMERIK
# ===============================
mapping = {
    "SS": 5,
    "S": 4,
    "CS": 4,
    "N": 3,
    "TS": 2,
    "STS": 1
}

df_numeric = df[question_cols].applymap(lambda x: mapping.get(x, None))

# ===============================
#   SIDEBAR
# ===============================
st.sidebar.header("📌 Pengaturan")
chart_choice = st.sidebar.selectbox(
    "Pilih Grafik",
    [
        "Distribusi Semua Jawaban (Bar Chart)",
        "Proporsi Jawaban (Pie Chart)",
        "Distribusi Jawaban per Pertanyaan (Stacked Bar)",
        "Rata-Rata Skor Tiap Pertanyaan",
        "Kategori Positif / Netral / Negatif",
        "Bonus Radar Chart"
    ]
)

# ===============================
#   1️⃣ DISTRIBUSI SEMUA JAWABAN
# ===============================
if chart_choice == "Distribusi Semua Jawaban (Bar Chart)":
    st.subheader("📊 Distribusi Semua Jawaban")

    all_counts = (
        df[question_cols]
        .stack()
        .value_counts()
        .reindex(skala_order, fill_value=0)
        .reset_index()
    )
    all_counts.columns = ["Jawaban", "Jumlah"]

    fig = px.bar(
        all_counts,
        x="Jawaban",
        y="Jumlah",
        text="Jumlah",
        color="Jawaban",
        category_orders={"Jawaban": skala_order},
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ===============================
#   2️⃣ PIE CHART
# ===============================
elif chart_choice == "Proporsi Jawaban (Pie Chart)":
    st.subheader("🥧 Proporsi Jawaban")

    all_counts = (
        df[question_cols]
        .stack()
        .value_counts()
        .reindex(skala_order, fill_value=0)
        .reset_index()
    )
    all_counts.columns = ["Jawaban", "Jumlah"]

    fig = px.pie(
        all_counts,
        names="Jawaban",
        values="Jumlah",
        hole=0.4,
        category_orders={"Jawaban": skala_order}
    )

    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

# ===============================
#   3️⃣ STACKED BAR
# ===============================
elif chart_choice == "Distribusi Jawaban per Pertanyaan (Stacked Bar)":
    st.subheader("📚 Distribusi Jawaban per Pertanyaan")

    stack_data = pd.DataFrame()

    for q in question_cols:
        counts = (
            df[q]
            .value_counts()
            .reindex(skala_order, fill_value=0)
        )
        stack_data[q] = counts

    fig = go.Figure()

    for label in skala_order:
        fig.add_trace(go.Bar(
            name=label,
            x=stack_data.columns,
            y=stack_data.loc[label]
        ))

    fig.update_layout(
        barmode="stack",
        xaxis_title="Pertanyaan",
        yaxis_title="Jumlah Respon"
    )

    st.plotly_chart(fig, use_container_width=True)

# ===============================
#   4️⃣ RATA-RATA SKOR
# ===============================
elif chart_choice == "Rata-Rata Skor Tiap Pertanyaan":
    st.subheader("⭐ Rata-Rata Skor")

    mean_scores = df_numeric.mean().reset_index()
    mean_scores.columns = ["Pertanyaan", "Skor"]

    fig = px.bar(
        mean_scores,
        x="Pertanyaan",
        y="Skor",
        text=mean_scores["Skor"].round(2),
        color="Skor",
        color_continuous_scale="Blues"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_range=[0,5])

    st.plotly_chart(fig, use_container_width=True)

# ===============================
#   5️⃣ POSITIF / NETRAL / NEGATIF
# ===============================
elif chart_choice == "Kategori Positif / Netral / Negatif":
    st.subheader("😀😐🙁 Distribusi Kategori")

    kategori_map = {
        "SS": "Positif",
        "S": "Positif",
        "CS": "Positif",
        "N": "Netral",
        "TS": "Negatif",
        "STS": "Negatif"
    }

    flat = df[question_cols].stack().map(kategori_map)

    kategori_counts = flat.value_counts().reindex(
        ["Positif", "Netral", "Negatif"],
        fill_value=0
    ).reset_index()

    kategori_counts.columns = ["Kategori", "Jumlah"]

    fig = px.bar(
        kategori_counts,
        x="Kategori",
        y="Jumlah",
        text="Jumlah",
        color="Kategori",
        color_discrete_map={
            "Positif": "#2ecc71",
            "Netral": "#f1c40f",
            "Negatif": "#e74c3c"
        }
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ===============================
#   6️⃣ RADAR CHART
# ===============================
elif chart_choice == "Bonus Radar Chart":
    st.subheader("🛡️ Radar Chart Rata-Rata Skor")

    mean_scores = df_numeric.mean()

    if len(mean_scores) < 3:
        st.warning("Radar chart memerlukan minimal 3 pertanyaan.")
    else:
        labels = mean_scores.index.tolist()
        values = mean_scores.values.tolist()

        # tutup polygon
        labels += [labels[0]]
        values += [values[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself"
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,5])),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)
