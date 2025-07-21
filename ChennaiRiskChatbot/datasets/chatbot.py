import streamlit as st
import pandas as pd
import os

# Set folder path
DATA_FOLDER = "datasets"
DATA_PATH = os.path.join(os.getcwd(), DATA_FOLDER)

# Load all Excel files
def load_data():
    data_files = {
        "accident": "accident1.xlsx",
        "air pollution": "air pollution.xlsx",
        "crime": "crime details 1.xlsx",
        "flood": "flood.xlsx",
        "heat": "heat.xlsx",
        "population": "population.xlsx",
        "risk factor": "riskanalysis.xlsx"
    }

    data = {}
    for key, filename in data_files.items():
        filepath = os.path.join(DATA_PATH, filename)
        if os.path.exists(filepath):
            try:
                df = pd.read_excel(filepath)
                data[key] = df
            except Exception as e:
                print(f"Error loading {key}: {e}")
        else:
            print(f"File not found: {filepath}")
    return data

# Clean and match category
def detect_category(user_input):
    user_input = user_input.lower()
    if "accident" in user_input:
        return "accident"
    elif "pollution" in user_input or "air" in user_input:
        return "air pollution"
    elif "crime" in user_input:
        return "crime"
    elif "flood" in user_input:
        return "flood"
    elif "heat" in user_input:
        return "heat"
    elif "population" in user_input:
        return "population"
    elif "risk" in user_input:
        return "risk factor"
    return None

# Extract area/location from input
def extract_area(user_input):
    tokens = user_input.lower().split()
    locations = ["t.nagar", "velachery", "adyar", "annanagar", "perambur", "chromepet", "tambaram", "guindy", "egmore", "kodambakkam", "vadapalani", "porur", "ambattur", "besant nagar", "triplicane", "mylapore", "ashok nagar", "thiruvanmiyur", "north chennai", "south chennai", "central chennai", "chennai"]
    for word in tokens:
        for loc in locations:
            if loc in word:
                return loc
    return "chennai"

# Search and return relevant data
def search_data(category, area, data):
    df = data.get(category)
    if df is not None:
        for col in df.columns:
            if df[col].astype(str).str.lower().str.contains(area).any():
                return df[df[col].astype(str).str.lower().str.contains(area)].head()
    return None

# Streamlit UI
st.set_page_config(page_title="Chennai Risk Chatbot", page_icon="🧠")
st.title("🧠 Chennai Risk Chatbot")
st.markdown("Ask me anything about accident, air pollution, crime, flood, heat, population or risk factor in Chennai!")

with st.expander("👋 Hi! I'm your Chennai Risk Assistant. Ask me questions like:"):
    st.markdown("""
- How is the accident data in a specific area?
- Tell me about pollution in T.Nagar
- Crime rate in Chennai?
- Flood risks in North Chennai
    """)

user_input = st.text_input("💬 Type your question below:")

if user_input:
    category = detect_category(user_input)
    area = extract_area(user_input)

    if not category:
        st.error("❌ Could not identify the category (e.g., accident, crime, flood). Please rephrase.")
    else:
        data = load_data()
        result = search_data(category, area, data)
        if result is not None and not result.empty:
            st.success(f"📍 Showing {category.upper()} data for {area.title()}")
            st.dataframe(result)
        else:
            st.error("❌ Data not available for this category or area.")
