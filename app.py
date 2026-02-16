import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===============================
#   CONFIGURASI DASHBOARD
# ===============================
st.set_page_config(
    page_title="Dashboard Kuesioner",
    page_icon="📊",
    layout="wide"
)

# Tema Plotly default
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = "Blues"

# ===============================
#   LOAD DATA
# ===============================
st.title("📊 Dashboard Visualisasi Data Kuesioner")

uploaded_data = "data_kuesioner.xlsx"
df = pd.read_excel(uploaded_data)

question_cols = [col for col in df.columns if col.startswith("Q")]

# Jika tidak ada kolom pertanyaan, hentikan lebih awal
if not question_cols:
    st.error("Tidak ditemukan kolom pertanyaan (kolom yang diawali 'Q') di file input.")
    st.stop()

# ===============================
#   MAPPING NILAI
# ===============================
mapping = {
    "SS": 5,
    "S": 4,
    "CS": 4,
    "N": 3,
    "TS": 2,
    "STS": 1
}

df_numeric = (
    df[question_cols]
    .replace(mapping)
    .apply(pd.to_numeric, errors="coerce")
)

# Jika semua nilai menjadi NaN setelah mapping, beri tahu user
if df_numeric.isna().all(axis=None):
    st.warning("Semua nilai pertanyaan tidak valid setelah pemetaan. Periksa format jawaban di file input.")

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
#   HALAMAN GRAFIK
# ===============================

# --- 1. Distribusi Semua Jawaban
if chart_choice == "Distribusi Semua Jawaban (Bar Chart)":
    st.subheader("📊 Distribusi Semua Jawaban Kuesioner")

    all_counts = df[question_cols].stack().dropna().value_counts().reset_index()
    all_counts.columns = ["Jawaban", "Jumlah"]

    fig = px.bar(
        all_counts,
        x="Jawaban",
        y="Jumlah",
        color="Jawaban",
        text="Jumlah",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# --- 2. Pie Chart Proporsi Jawaban
elif chart_choice == "Proporsi Jawaban (Pie Chart)":
    st.subheader("🥧 Proporsi Jawaban Keseluruhan")

    all_counts = df[question_cols].stack().dropna().value_counts().reset_index()
    all_counts.columns = ["Jawaban", "Jumlah"]

    fig = px.pie(
        all_counts,
        names="Jawaban",
        values="Jumlah",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textinfo="percent+label")

    st.plotly_chart(fig, use_container_width=True)


# --- 3. Stacked Bar per Pertanyaan
elif chart_choice == "Distribusi Jawaban per Pertanyaan (Stacked Bar)":
    st.subheader("📚 Distribusi Jawaban per Pertanyaan")

    stack_data = pd.DataFrame()
    for q in question_cols:
        temp = df[q].dropna().value_counts().rename(q)
        stack_data = pd.concat([stack_data, temp], axis=1)
    stack_data = stack_data.fillna(0)

    fig = go.Figure()

    for label in stack_data.index:
        fig.add_trace(go.Bar(
            name=label,
            x=stack_data.columns,
            y=stack_data.loc[label],
        ))

    fig.update_layout(barmode="stack")
    st.plotly_chart(fig, use_container_width=True)


# --- 4. Rata-Rata Skor Tiap Pertanyaan
elif chart_choice == "Rata-Rata Skor Tiap Pertanyaan":
    st.subheader("⭐ Rata-Rata Skor Tiap Pertanyaan")

    mean_scores = df_numeric.mean(axis=0).reset_index()
    mean_scores.columns = ["Pertanyaan", "Skor"]

    fig = px.bar(
        mean_scores,
        x="Pertanyaan",
        y="Skor",
        text="Skor",
        color="Skor",
        color_continuous_scale="Peach"
    )
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


# --- 5. Positif / Netral / Negatif
elif chart_choice == "Kategori Positif / Netral / Negatif":
    st.subheader("😀😐🙁 Distribusi Kategori Jawaban")

    kategori_map = {
        "SS": "Positif", "S": "Positif", "CS": "Positif",
        "N": "Netral",
        "TS": "Negatif", "STS": "Negatif"
    }

    flat = df[question_cols].stack().dropna().map(kategori_map)
    kategori_counts = flat.value_counts().reset_index()
    kategori_counts.columns = ["Kategori", "Jumlah"]

    fig = px.bar(
        kategori_counts,
        x="Kategori",
        y="Jumlah",
        text="Jumlah",
        color="Kategori",
        color_discrete_sequence=["#2ecc71", "#f1c40f", "#e74c3c"]
    )

    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# --- 6. Bonus Radar Chart
elif chart_choice == "Bonus Radar Chart":
    st.subheader("🛡️ Radar Chart Rata-Rata Skor")
    mean_scores = df_numeric.mean(axis=0)

    # Jika kurang dari 3 variabel, radar kurang informatif/bermasalah — tampilkan bar chart sebagai fallback
    labels = mean_scores.index.tolist()
    values = mean_scores.values.tolist()

    if len(values) < 3:
        st.warning("Radar chart memerlukan minimal 3 pertanyaan. Menampilkan bar chart sebagai gantinya.")
        mean_df = mean_scores.reset_index()
        mean_df.columns = ["Pertanyaan", "Skor"]
        fig = px.bar(
            mean_df,
            x="Pertanyaan",
            y="Skor",
            text="Skor",
            color="Skor",
            color_continuous_scale="Peach"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Tutup polygon dengan mengulang titik pertama di akhir
        labels_closed = labels + [labels[0]]
        values_closed = values + [values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            line=dict(width=2)
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5]))
        )

        st.plotly_chart(fig, use_container_width=True)
