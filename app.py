import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===============================
# CONFIG PAGE
# ===============================
st.set_page_config(
    page_title="Dashboard Kuesioner",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Visualisasi Data Kuesioner")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data(path):
    return pd.read_excel(path)

file_path = "data_kuesioner.xlsx"
df = load_data(file_path)

question_cols = [col for col in df.columns if col.startswith("Q")]

if not question_cols:
    st.error("Tidak ditemukan kolom pertanyaan (Q1, Q2, dst)")
    st.stop()

# ===============================
# MAPPING LIKERT
# ===============================
likert_map = {
    "SS": 5,
    "S": 4,
    "CS": 4,
    "N": 3,
    "TS": 2,
    "STS": 1
}

df_numeric = df[question_cols].replace(likert_map).apply(
    pd.to_numeric, errors="coerce"
)

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("⚙️ Pengaturan")

selected_questions = st.sidebar.multiselect(
    "Pilih Pertanyaan",
    question_cols,
    default=question_cols
)

chart_type = st.sidebar.radio(
    "Pilih Jenis Grafik",
    [
        "Bar Distribusi",
        "Pie Proporsi",
        "Stacked Bar",
        "Rata-Rata Skor",
        "Kategori Sentimen",
        "Radar Chart"
    ]
)

# ===============================
# FUNCTION GRAFIK
# ===============================

def bar_distribusi():
    data = df[selected_questions].stack().value_counts().reset_index()
    data.columns = ["Jawaban", "Jumlah"]

    fig = px.bar(
        data,
        x="Jawaban",
        y="Jumlah",
        text="Jumlah",
        color="Jawaban"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def pie_proporsi():
    data = df[selected_questions].stack().value_counts().reset_index()
    data.columns = ["Jawaban", "Jumlah"]

    fig = px.pie(
        data,
        names="Jawaban",
        values="Jumlah",
        hole=0.4
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)


def stacked_bar():
    stack_data = pd.DataFrame()

    for q in selected_questions:
        temp = df[q].value_counts().rename(q)
        stack_data = pd.concat([stack_data, temp], axis=1)

    stack_data = stack_data.fillna(0)

    fig = go.Figure()

    for label in stack_data.index:
        fig.add_trace(go.Bar(
            name=label,
            x=stack_data.columns,
            y=stack_data.loc[label]
        ))

    fig.update_layout(barmode="stack")
    st.plotly_chart(fig, use_container_width=True)


def rata_rata():
    mean_scores = df_numeric[selected_questions].mean().reset_index()
    mean_scores.columns = ["Pertanyaan", "Skor"]

    fig = px.bar(
        mean_scores,
        x="Pertanyaan",
        y="Skor",
        text="Skor",
        color="Skor",
        color_continuous_scale="Blues"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def kategori_sentimen():
    kategori_map = {
        "SS": "Positif",
        "S": "Positif",
        "CS": "Positif",
        "N": "Netral",
        "TS": "Negatif",
        "STS": "Negatif"
    }

    flat = df[selected_questions].stack().map(kategori_map)
    data = flat.value_counts().reset_index()
    data.columns = ["Kategori", "Jumlah"]

    fig = px.bar(
        data,
        x="Kategori",
        y="Jumlah",
        text="Jumlah",
        color="Kategori"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def radar_chart():
    mean_scores = df_numeric[selected_questions].mean()

    if len(mean_scores) < 3:
        st.warning("Minimal 3 pertanyaan untuk radar chart")
        return

    labels = mean_scores.index.tolist()
    values = mean_scores.values.tolist()

    labels += [labels[0]]
    values += [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill="toself"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5]))
    )

    st.plotly_chart(fig, use_container_width=True)


# ===============================
# DISPLAY CHART
# ===============================

if chart_type == "Bar Distribusi":
    bar_distribusi()

elif chart_type == "Pie Proporsi":
    pie_proporsi()

elif chart_type == "Stacked Bar":
    stacked_bar()

elif chart_type == "Rata-Rata Skor":
    rata_rata()

elif chart_type == "Kategori Sentimen":
    kategori_sentimen()

elif chart_type == "Radar Chart":
    radar_chart()

