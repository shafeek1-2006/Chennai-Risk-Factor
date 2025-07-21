import streamlit as st
import pandas as pd
import os

# Set up Streamlit page
st.set_page_config(page_title="🧠 Chennai Risk Chatbot", layout="centered")

st.title("🧠 Chennai Risk Chatbot")
st.markdown("Ask me anything about accident, air pollution, crime, flood, heat, population or risk factor in Chennai!")

# Folder path
base_path = "datasets"
full_base = os.path.join(os.getcwd(), base_path)

# Load Excel files
files = {
    "accident": "accident1.xlsx",
    "air pollution": "air pollution.xlsx",
    "crime": "crime details 1.xlsx",
    "flood": "flood.xlsx",
    "heat": "heat.xlsx",
    "population": "population.xlsx",
    "riskfactor": "riskanalysis.xlsx"
}

data = {}
for key, fname in files.items():
    try:
        df = pd.read_excel(os.path.join(full_base, fname))
        data[key] = df
    except:
        data[key] = pd.DataFrame()

# Friendly AI-like intro
st.markdown("👋 Hi! I'm your Chennai Risk Assistant. Ask me questions like:")
st.markdown("- How is the accident data in a specific area?")
st.markdown("- Tell me about pollution in T.Nagar")
st.markdown("- Crime rate in Chennai?")
st.markdown("- Flood risks in North Chennai")
st.markdown("")

# Text input from user
query = st.text_input("💬 Type your question below:")

def search_data(query):
    query = query.lower()
    for key in data:
        if key in query:
            df = data[key]
            if df.empty:
                return "❌ Data not available for this category."
            if "area" in df.columns:
                result = ""
                for area in df["area"].unique():
                    if area.lower() in query:
                        filtered = df[df["area"].str.lower() == area.lower()]
                        return filtered
                return df.head(10)
            else:
                return df.head(10)
    return "🤖 Sorry, I couldn't understand your question. Try mentioning accident, crime, flood, etc."

if query:
    response = search_data(query)
    if isinstance(response, pd.DataFrame):
        st.markdown("🔍 Here's what I found:")
        st.dataframe(response)
    else:
        st.markdown(response)
